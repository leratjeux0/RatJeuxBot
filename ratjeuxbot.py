import discord
import os
import json
import random
import asyncio
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Activer les intents pour lire les messages
intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(bot)

# ------------------------------- Gestion de l'argent -------------------------------

def load_Bank():
    """Charge les données de la banque depuis un fichier JSON."""
    try:
        with open("Money.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_Money(bank):
    """Enregistre les données de la banque dans un fichier JSON."""
    with open("Money.json", "w") as f:
        json.dump(bank, f)

def get_Bank(user_id):
    """Récupère le solde d'un utilisateur."""
    bank = load_Bank()
    return bank.get(str(user_id), 100)

def update_Bank(user_id, amount):
    """Met à jour le solde d'un utilisateur."""
    bank = load_Bank()
    bank[str(user_id)] = bank.get(str(user_id), 100) + amount
    save_Money(bank)

# ------------------------------- Gestion de la Machine à Sous -------------------------------

class ButtonMachineSous(discord.ui.View):
    """Boutons interactifs pour la machine à sous."""
    
    def __init__(self, user_id, mise):
        super().__init__()
        self.user_id = user_id
        self.mise = mise

    @discord.ui.button(label="Rejouer 🎰", style=discord.ButtonStyle.primary)
    async def rejouer(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Permet de rejouer une partie avec la même mise."""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Tu ne peux pas rejouer cette partie !", ephemeral=True)
            return

        # Génération du tirage
        rouleaux = ["🍒", "🍋", "🔔", "💎", "7️⃣"]
        a, b, c = random.choices(rouleaux, k=3)

        gain = 0
        if a == b == c:
            gain = self.mise * 5
            result_text = "JACKPOT!!! Tu remportes **5x** ta mise !"
        elif a == b or b == c or c == a:
            gain = self.mise * 2
            result_text = "Tu as gagné **2x** ta mise !"
        else:
            gain = -self.mise
            result_text = "Perdu! Retente ta chance."

        update_Bank(self.user_id, gain)
        new_Bank = get_Bank(self.user_id)

        # Créer l'embed de résultat
        embed = discord.Embed(title="🎰 Machine à Sous 🎰", color=discord.Color.gold())
        embed.add_field(name="🎰 Résultat :", value=f"| {a} | {b} | {c} |", inline=False)
        embed.add_field(name="💰 Mise :", value=f"{self.mise}💰", inline=False)
        embed.add_field(name="🏆 Gain :", value=f"{gain if gain > 0 else 0}💰", inline=True)
        embed.add_field(name="💵 Nouveau solde :", value=f"{new_Bank}💰", inline=False)
        embed.set_footer(text=result_text)

        # Modifier le message avec le nouveau résultat
        await interaction.response.edit_message(embed=embed, view=ButtonMachineSous(self.user_id, self.mise))

    @discord.ui.button(label='Changer la mise', style=discord.ButtonStyle.secondary)
    async def changer_mise(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Permet de changer la mise."""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Tu ne peux pas modifier cette mise !", ephemeral=True)
            return

        await interaction.response.send_message("Quelle est le nouveau montant de la mise ?", ephemeral=True)

        def check(m):
            return m.author.id == self.user_id and m.channel.id == interaction.channel.id and m.content.isdigit()

        try:
            msg = await bot.wait_for("message", check=check, timeout=60)
            new_mise = int(msg.content)
        except asyncio.TimeoutError:
            await interaction.followup.send("⏳ Temps écoulé, mise inchangée.", ephemeral=True)
            return

        if new_mise <= 0:
            await interaction.followup.send("❌ La mise doit être supérieure à zéro.", ephemeral=True)
        elif new_mise > get_Bank(self.user_id):
            await interaction.followup.send("❌ Tu n'as pas assez d'argent pour miser autant.", ephemeral=True)
        else:
            self.mise = new_mise
            await interaction.followup.send(f"✅ La nouvelle mise est de {self.mise}💰", ephemeral=True)
            await machine_a_sous(interaction, self.mise)

# ------------------------------- Commandes -------------------------------

@tree.command(name='menu', description='Menu du casino')
async def menu(interaction: discord.Interaction):
    embed = discord.Embed(title='🪙 Accueil du casino 🪙', color=discord.Color.gold())
    embed.add_field(name="🎰 Machine à Sous 🎰", value="Gagne de l'argent en alignant 2 ou 3 mêmes icônes.")

    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="machine-a-sous", description="Joue à la machine à sous")
async def machine_a_sous(interaction: discord.Interaction, mise: int):
    user_id = interaction.user.id
    solde = get_Bank(user_id)

    if mise <= 0:
        await interaction.response.send_message("❌ Ta mise doit être supérieure à zéro.", ephemeral=True)
        return
    elif mise > solde:
        await interaction.response.send_message("❌ Tu n'as pas assez d'argent pour miser autant !", ephemeral=True)
        return

    rouleaux = ["🍒", "🍋", "🔔", "💎", "7️⃣"]
    a, b, c = random.choices(rouleaux, k=3)

    gain = 0
    if a == b == c:
        gain = mise * 5
        result_text = "JACKPOT!!! Tu remportes **5x** ta mise !"
    elif a == b or b == c or c == a:
        gain = mise * 2
        result_text = "Tu as gagné **2x** ta mise !"
    else:
        gain = -mise
        result_text = "Perdu! Retente ta chance."

    update_Bank(user_id, gain)
    new_Bank = get_Bank(user_id)

    embed = discord.Embed(title="🎰 Machine à Sous 🎰", color=discord.Color.gold())
    embed.add_field(name="🎰 Résultat :", value=f"| {a} | {b} | {c} |", inline=False)
    embed.add_field(name="💰 Mise :", value=f"{mise}💰", inline=False)
    embed.add_field(name="🏆 Gain :", value=f"{gain if gain > 0 else 0}💰", inline=True)
    embed.add_field(name="💵 Nouveau solde :", value=f"{new_Bank}💰", inline=False)
    embed.set_footer(text=result_text)

    await interaction.response.send_message(embed=embed, view=ButtonMachineSous(user_id, mise), ephemeral=True)

# ------------------------------- Événement -------------------------------

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Connecté en tant que {bot.user}")

bot.run(os.getenv("TOKEN"))

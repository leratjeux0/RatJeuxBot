import discord
import os
from dotenv import load_dotenv
import json
import random

load_dotenv()

intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(bot)  # CommandTree doit être initialisé après on_ready

#-------------------------------utilis---------------------------------
def load_Bank():
    try:
        with open("Money.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
def save_Money(bank):
    with open("Money.json", "w") as f:
        json.dump(bank, f)
def get_Bank(user_id):
    bank = load_Bank()
    return bank.get(str(user_id), 100)
def update_Bank(user_id, amount):
    bank = load_Bank()
    bank[str(user_id)] = bank.get(str(user_id), 100) + amount
    save_Money(bank)
class ButtonMachineSous(discord.ui.View):
    def __init__(self, user_id, mise):
        super().__init__()
        self.user_id = user_id
        self.mise = mise

    @discord.ui.button(label="Rejouer 🎰", style=discord.ButtonStyle.primary)
    async def rejouer(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Tu ne peux pas rejouer cette partie !", ephemeral=True)
            return

        # Générer un nouveau tirage
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
            gain -= self.mise
            result_text = "Perdu! Retente ta chance."

        update_Bank(self.user_id, gain)
        new_Bank = get_Bank(self.user_id)

        # Créer un nouvel embed avec les résultats mis à jour
        embed = discord.Embed(title="🎰 Machine à Sous 🎰", color=discord.Color.gold())
        embed.add_field(name="🎰 Résultat :", value=f"| {a} | {b} | {c} |", inline=False)
        embed.add_field(name="💰 Mise :", value=f"{self.mise}💰", inline=False)
        embed.add_field(name="🏆 Gain :", value=f"{gain if gain > 0 else 0}💰", inline=True)
        embed.add_field(name="💵 Nouveau solde :", value=f"{new_Bank}💰", inline=False)
        embed.set_footer(text=result_text)

        # Modifier le message existant avec le nouveau résultat
        await interaction.response.edit_message(embed=embed, view=ButtonMachineSous(self.user_id, self.mise))

    @discord.ui.button(label='Changer la mise', style=discord.ButtonStyle.secondary)
    async def changer_mise(self, interaction: discord.Interaction, mise):

        await interaction.response.send_message('Quelle est le nouveau montent de la mise ?', ephemeral=True)
    
        def check(m):
            return m.author.id == self.user_id and m.channel.id == interaction.channel.id

        msg = await bot.wait_for('message', check=check, timeout=60)
        new_mise = msg.content

        print(new_mise)

        bonne_mise = False

        while bonne_mise:
            if new_mise <= 0:
                await interaction.followup.send("La msie doit être supérieur à zéro.", ephemeral=True)
            elif new_mise > get_Bank(self.user_id):
                await interaction.followup.send("Tu n'as pas assez d'argent pour misé autant.", ephemeral=True)
            else:
                self.mise = new_mise
                await interaction.followup.send(f'La nouvelle mise est de {self.mise}$', ephemeral=True)
                machine_a_sous(interaction, self.mise)
                return

#-------------------------------Commande-------------------------------
@tree.command(name='menu', description='Menu du casino')
async def Menu(interaction: discord.Interaction):
    embed = discord.Embed(title='🪙 Accuiel du casino 🪙', color=discord.Color.gold())
    embed.add_field(name="🎰 Machine à Sous 🎰", value="Gagne de l'argent en alignent 2 ou trois même icon.")

    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="machine-a-sous", description="Joue à la machine à sous")
async def machine_a_sous(interaction: discord.Interaction, mise: int):
    user_id = interaction.user.id
    solde = get_Bank(user_id)

    if mise <= 0:
        await interaction.response.send_message("Ta mise doit être supérieure à zéro", ephemeral=True)
        return
    elif mise > solde:
        await interaction.response.send_message("Tu n'as pas assez d'argent pour miser autant!", ephemeral=True)
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
        gain -= mise
        result_text = "Perdu! Retente ta chance."

    update_Bank(user_id, gain)
    new_Bank = get_Bank(user_id)

    embed = discord.Embed(title="🎰 Machine à Sous 🎰", color=discord.Color.gold())
    embed.add_field(name="🎰 Résultat :", value=f"| {a} | {b} | {c} |", inline=False)
    embed.add_field(name="💰 Mise :", value=f"{mise}💰", inline=False)
    embed.add_field(name="🏆 Gain :", value=f"{gain if gain > 0 else 0}💰", inline=True)
    embed.add_field(name="💵 Nouveau solde :", value=f"{new_Bank}💰", inline=False)
    embed.set_footer(text=result_text)

    # Envoyer le message initial avec le bouton "Rejouer"
    await interaction.response.send_message(embed=embed, view=ButtonMachineSous(user_id, mise), ephemeral=True)

@tree.command(name='money', description="Voir l'argent en bank")
async def money(interaction: discord.Interaction):
    user_id = interaction.user.id
    solde = get_Bank(user_id)
    embed = discord.Embed(title='🏛️ Bank 🏛️', color=discord.Color.gold())
    embed.add_field(name='💵 Argent 💵', value=f'💰 Vous avez {solde}$ sur votre compte. 💰')

    await interaction.response.send_message(embed=embed, ephemeral=True)



#-------------------------------event-------------------------------
@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Connecté en tant que {bot.user}")

bot.run(os.getenv("TOKEN"))

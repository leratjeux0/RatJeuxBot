import discord, random
from discord import app_commands
from discord.ext import commands

from cogs.tools import *

class ButtonMachineSous(discord.ui.View):
    def __init__(self, user_id, mise):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.mise = mise

    @discord.ui.button(label="Rejouer", style=discord.ButtonStyle.success)
    async def replay(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("❌ Ce bouton n'est pas pour toi.", ephemeral=True)

        command = interaction.client.tree.get_command("machine-a-sous")  # Récupère la commande
        if command:
            await command._callback(interaction.client.get_cog("Jeux"), interaction, self.mise)  # Appelle la commande proprement
        else:
            await interaction.response.send_message("❌ La machine à sous est indisponible.", ephemeral=True)

    @discord.ui.button(label="Changer la mise", style=discord.ButtonStyle.primary)
    async def change_bet(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("❌ Ce bouton n'est pas pour toi.", ephemeral=True)

        modal = ChangeBetModal(self)
        await interaction.response.send_modal(modal)

class ChangeBetModal(discord.ui.Modal, title="Changer la mise"):
    mise = discord.ui.TextInput(label="Nouvelle mise", style=discord.TextStyle.short, required=True)

    def __init__(self, view: ButtonMachineSous):
        super().__init__()
        self.view = view

    async def on_submit(self, interaction: discord.Interaction):
        try:
            nouvelle_mise = int(self.mise.value)
            if nouvelle_mise < 10:
                return await interaction.response.send_message("❌ La mise doit être d'au moins 10$.", ephemeral=True)

            self.view.mise = nouvelle_mise  # Mise mise à jour pour la prochaine partie
            await interaction.response.send_message(f"✅ Mise mise à jour : {nouvelle_mise}💰", ephemeral=True)

        except ValueError:
            await interaction.response.send_message("❌ Veuillez entrer un nombre valide.", ephemeral=True)

class Jeux(commands.Cog):
    
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="machine-a-sous", description="Joue à la machine à sous")
    async def machine_a_sous(self, interaction: discord.Interaction, mise: int):
        user_id = interaction.user.id
        create_user(user_id)
        solde = get_Bank(user_id)

        if mise < 10:
            return await interaction.response.send_message("❌ Ta mise doit être minimum de 10$.", ephemeral=True)
        elif mise > solde:
            return await interaction.response.send_message(f"❌ Tu n'as pas assez d'argent! Solde: {solde}💰", ephemeral=True)

        rouleaux = ["🍒", "🍋","🍓","🔔", "💎", "7️⃣"]
        a, b, c = random.choices(rouleaux, k=3)

        gain = 0
        if a == b == c:
            gain = mise * 5
            result_text = "JACKPOT!!! Tu remportes **5x** ta mise !"
        elif a == b or b == c or c == a:
            gain = mise / 2
            result_text = "Dommage, tu étais proche."
        else:
            gain = -mise
            result_text = "Perdu! Retente ta chance."

        update_Bank(user_id, gain)
        new_bank = round(get_Bank(user_id))

        embed = discord.Embed(title="🎰 Machine à Sous 🎰", color=discord.Color.gold())
        embed.add_field(name="🎰 Résultat :", value=f"| {a} | {b} | {c} |", inline=False)
        embed.add_field(name="💰 Mise :", value=f"{mise}💰", inline=False)
        embed.add_field(name="🏆 Gain :", value=f"{gain if gain > 0 else 0}💰", inline=True)
        embed.add_field(name="💵 Nouveau solde :", value=f"{new_bank}💰", inline=False)
        embed.set_footer(text=result_text)

        await interaction.response.send_message(embed=embed, view=ButtonMachineSous(user_id, mise), ephemeral=True)

async def setup(client):
    await client.add_cog(Jeux(client))

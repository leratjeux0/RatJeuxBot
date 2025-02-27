import discord, random
from discord import app_commands
from discord.ext import commands

from cogs.interactions import *
from cogs.tools import *


class Jeux(commands.Cog):
    
    def __init__(self, client):
        self.client = client
    

    @app_commands.command(name='menu', description='Menu du casino')
    async def menu(self, interaction: discord.Interaction):
        embed = discord.Embed(title='🪙 Accueil du casino 🪙', color=discord.Color.gold())
        embed.add_field(name="🎰 Machine à Sous 🎰", value="Gagne de l'argent en alignant 2 ou 3 mêmes icônes.")

        await interaction.response.send_message(embed=embed, ephemeral=True)


    @app_commands.command(name="machine-a-sous", description="Joue à la machine à sous")
    async def machine_a_sous(self, interaction: discord.Interaction, mise: int):
        user_id = interaction.user.id
        solde = get_Bank(user_id)

        if mise < 10:
            return await interaction.response.send_message("❌ Ta mise doit être minimum de 10$.", ephemeral=True)
        elif mise > solde:
            return await interaction.response.send_message(f"❌ Tu n'as pas assez d'argent pour miser autant ! Tu n'as que {get_Bank(user_id)}", ephemeral=True)
        rouleaux = ["🍒", "🍋","🍓","🔔", "💎", "7️⃣"]
        a, b, c = random.choices(rouleaux, k=3)

        gain = 0
        if a == b == c:
            gain = mise * 5
            result_text = "JACKPOT!!! Tu remportes **5x** ta mise !"
        elif a == b or b == c or c == a:
            gain = mise / 2
            result_text = "Dommage tu y étais presque. Retente ta chance."
        else:
            gain = -mise
            result_text = "Perdu! Retente ta chance."

        update_Bank(user_id, gain)
        Bank = get_Bank(user_id)
        new_bank = round(Bank)
        new_gain = round(gain)

        embed = discord.Embed(title="🎰 Machine à Sous 🎰", color=discord.Color.gold())
        embed.add_field(name="🎰 Résultat :", value=f"| {a} | {b} | {c} |", inline=False)
        embed.add_field(name="💰 Mise :", value=f"{mise}💰", inline=False)
        embed.add_field(name="🏆 Gain :", value=f"{new_bank if new_gain > 0 else 0}💰", inline=True)
        embed.add_field(name="💵 Nouveau solde :", value=f"{new_bank}💰", inline=False)
        embed.set_footer(text=result_text)

        if not interaction.response.is_done():
            await interaction.response.send_message(embed=embed, view=ButtonMachineSous(user_id, mise), ephemeral=True)
        else:
            await interaction.followup.send(embed=embed, view=ButtonMachineSous(user_id, mise), ephemeral=True)

    # @app_commands.command(name="money", description="💵 Voir ton argent 💵")
    # async def money(interaction : discord.Interaction):
    #     await interaction.response.send_message(f"Tu as {get_Bank(interaction.user.id)}$ sur ton compte ")


async def setup(client):
    await client.add_cog(Jeux(client))
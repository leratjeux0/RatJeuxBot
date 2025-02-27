import discord, random, asyncio

from cogs.tools import *

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
            return await interaction.response.send_message("Tu ne peux pas rejouer cette partie !", ephemeral=True)

        # Génération du tirage
        rouleaux = ["🍒", "🍋", "🔔", "💎", "7️⃣"]
        a, b, c = random.choices(rouleaux, k=3)

        gain = 0
        if a == b == c:
            gain = self.mise * 5
            result_text = "JACKPOT!!! Tu remportes **5x** ta mise !"
        elif a == b or b == c or c == a:
            gain = self.mise / 2
            result_text = "Dommage tu y étais presque. Retente ta chance."
        else:
            gain = -self.mise
            result_text = "Perdu! Retente ta chance."

        update_Bank(self.user_id, gain)
        Bank = get_Bank(self.user_id)
        new_bank = round(Bank)
        new_gain = round(gain)

        # Créer l'embed de résultat
        embed = discord.Embed(title="🎰 Machine à Sous 🎰", color=discord.Color.gold())
        embed.add_field(name="🎰 Résultat :", value=f"| {a} | {b} | {c} |", inline=False)
        embed.add_field(name="💰 Mise :", value=f"{self.mise}💰", inline=False)
        embed.add_field(name="🏆 Gain :", value=f"{new_gain if new_gain > 0 else 0}💰", inline=True)
        embed.add_field(name="💵 Nouveau solde :", value=f"{new_bank}💰", inline=False)
        embed.set_footer(text=result_text)

        # Modifier le message avec le nouveau résultat
        await interaction.response.edit_message(embed=embed, view=ButtonMachineSous(self.user_id, self.mise))


    @discord.ui.button(label='Changer la mise', style=discord.ButtonStyle.secondary)
    async def changer_mise(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Permet de changer la mise."""
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("Tu ne peux pas modifier cette mise !", ephemeral=True)

        await interaction.response.send_message("Quelle est le nouveau montant de la mise ?", ephemeral=True)

        def check(m):
            return m.author.id == self.user_id and m.channel.id == interaction.channel.id and m.content.isdigit()

        try:
            msg = await interaction.client.wait_for("message", check=check, timeout=60)
            new_mise = int(msg.content)
        except asyncio.TimeoutError:
            return await interaction.followup.send("⏳ Temps écoulé, mise inchangée.", ephemeral=True)

        await msg.channel.purge(limit=1)

        if new_mise < 10:
            return await interaction.followup.send("❌ La mise doit être au minimum de 10$", ephemeral=True)
        elif new_mise > get_Bank(self.user_id):
            return await interaction.followup.send(f"❌ Tu n'as pas assez d'argent pour miser autant. Tu n'as que {get_Bank(get_Bank(interaction.user.id))}", ephemeral=True)
        else:
            self.mise = new_mise
            await interaction.followup.send(f"✅ La nouvelle mise est de {self.mise}💰", ephemeral=True)

            # Obtenir la commande et utiliser un followup
            command = interaction.client.tree.get_command("machine-a-sous")
            if command:
                await command.callback(self, interaction, self.mise)
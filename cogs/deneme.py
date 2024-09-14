import discord
from discord.ext import commands
from discord import app_commands

class deneme(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="deneme", description="bu bir deneme komutudur")
    async def deneme(self, interaction:discord.Interaction):
        await interaction.response.send_message(f"Merhaba {interaction.user.mention}")

async def setup(bot):
    await bot.add_cog(deneme(bot))
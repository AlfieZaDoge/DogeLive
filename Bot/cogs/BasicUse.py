import discord
from discord.ext import commands
from discord import app_commands

class BasicUse(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="source", description="Shows the source code for DogeLive Bot!")
    async def source(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Here's my source code: https://github.com/AlfieZaDoge/DogeLive", ephemeral=True
        )

    @app_commands.command(name="invite", description="Sends an invite to add the bot to your own server")
    async def invite(self, interaction: discord.Interaction):
        url = "https://discord.com/oauth2/authorize?client_id=1394358248525529118&permissions=277294017648&integration_type=0&scope=bot"
        await interaction.response.send_message(f"[Invite me]({url})", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(BasicUse(bot))

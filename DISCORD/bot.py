import discord
from discord import app_commands
from discord.ext import commands
import os
import json

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../config.json'))
with open(config_path, 'r') as f:
    config = json.load(f)

TOKEN = config.get('TOKEN')

class MyBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="source", description="Shows the source code for DogeLive Bot!")
    async def source(self, interaction: discord.Interaction):
        await interaction.response.send_message("Here's my source code: https://github.com/AlfieZaDoge/DogeLive", ephemeral=True)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

bot.add_cog(MyBot(bot))

bot.run(TOKEN)

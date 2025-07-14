import discord
from discord import app_commands
from discord.ext import commands
import os
import json
import asyncio

intents = discord.Intents.all()  # grab all the damn intents
bot = commands.Bot(command_prefix="!", intents=intents)

config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../config.json'))
with open(config_path, 'r') as f:
    config = json.load(f)

TOKEN = config.get('TOKEN')  # don’t leak this or you’ll cry

class MyBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="source", description="Shows the source code for DogeLive Bot!")
    async def source(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Here's my source code: https://github.com/AlfieZaDoge/DogeLive", ephemeral=True
        )

    @app_commands.command(name="invite", description="Sends an invite to add the bot to your own server")
    async def invite(self, interaction: discord.Interaction):
        bot_id = self.bot.user.id
        invite_url = f"https://discord.com/oauth2/authorize?client_id=1394358248525529118&permissions=277294017648&integration_type=0&scope=bot" # so this invite link does not just give all perms it gives all the ones it needs i think ..
        await interaction.response.send_message(
            f"Add me to your server using this [Invite link]({invite_url})", ephemeral=True
        )

    def cog_app_commands(self):
        return [self.source, self.invite]

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id}) i love doge :O")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s) – no errors, no drama")
    except Exception as e:
        print(f"Failed to sync commands: {e} 💩")  # not today, Discord

async def main():
    async with bot:
        await bot.add_cog(MyBot(bot))
        await bot.start(TOKEN)

asyncio.run(main())

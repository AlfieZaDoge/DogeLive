import discord
from discord.ext import commands
import json, os, asyncio

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Load token
config_path = os.path.join(os.path.dirname(__file__), '../config.json')
with open(config_path) as f:
    TOKEN = json.load(f).get("TOKEN")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

async def main():
    async with bot:
        await bot.load_extension("cogs.notifier")
        await bot.load_extension("cogs.BasicUse")
        await bot.start(TOKEN)

asyncio.run(main())

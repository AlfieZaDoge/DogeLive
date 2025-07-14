import discord
from discord.ext import commands
from discord import app_commands

import os, json, asyncio, aiohttp
from datetime import datetime, timedelta

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../config.json'))
with open(config_path) as f:
    TOKEN = json.load(f).get('TOKEN')

# Store guild notification channels: {guild_id: {type_name: channel_id}}
notif_channels = {}

class MyBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}

    @app_commands.command(name="source", description="Shows the source code for DogeLive Bot!")
    async def source(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Here's my source code: https://github.com/AlfieZaDoge/DogeLive", ephemeral=True
        )

    @app_commands.command(name="invite", description="Sends an invite to add the bot to your own server")
    async def invite(self, interaction: discord.Interaction):
        url = "https://discord.com/oauth2/authorize?client_id=1394358248525529118&permissions=277294017648&integration_type=0&scope=bot"
        await interaction.response.send_message(f"[Invite me]({url})", ephemeral=True)

    @app_commands.command(name="checkstreaming", description="Checks if Doge Gfx is currently streaming.")
    async def checkstreaming(self, interaction: discord.Interaction):
        uid = interaction.user.id
        now = datetime.utcnow()

        if uid in self.cooldowns and now < self.cooldowns[uid]:
            remaining = self.cooldowns[uid] - now
            m, s = divmod(int(remaining.total_seconds()), 60)
            return await interaction.response.send_message(f"Cooldown: {m}m {s}s left.", ephemeral=True)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:3231/DogeStreaming") as resp:
                    if resp.status != 200:
                        return await interaction.response.send_message("Failed to reach streaming server.", ephemeral=True)

                    data = await resp.json()
                    self.cooldowns[uid] = now + timedelta(minutes=5)

                    if not data.get("answer"):
                        return await interaction.response.send_message("Doge Gfx is not currently streaming.")

                    title = data.get("Title", "Untitled Stream")
                    url = data.get("StreamURL", "No URL provided")
                    embed = discord.Embed(title=title, description=url, color=discord.Color.gold())
                    await interaction.response.send_message(embed=embed)

        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)

    @app_commands.command(name="notifyme", description="Get notified for new streams or videos.")
    @app_commands.describe(type="Choose what you want to be notified about")
    @app_commands.choices(type=[
        app_commands.Choice(name="NEW STREAM", value="New Stream"),
        app_commands.Choice(name="NEW VIDEO", value="New Video")
    ])
    async def notifyme(self, interaction: discord.Interaction, type: app_commands.Choice[str]):
        role = discord.utils.get(interaction.guild.roles, name=type.value)
        if not role:
            return await interaction.response.send_message("Role not found. Try again later.", ephemeral=True)
        await interaction.user.add_roles(role)
        await interaction.response.send_message(f"You’ve been given the **{type.value}** role!", ephemeral=True)

    @app_commands.command(name="removeme", description="Remove a notification role.")
    @app_commands.describe(type="Choose what you want to remove")
    @app_commands.choices(type=[
        app_commands.Choice(name="NEW STREAM", value="New Stream"),
        app_commands.Choice(name="NEW VIDEO", value="New Video")
    ])
    async def removeme(self, interaction: discord.Interaction, type: app_commands.Choice[str]):
        role = discord.utils.get(interaction.guild.roles, name=type.value)
        if not role:
            return await interaction.response.send_message("Role not found. Try again later.", ephemeral=True)
        await interaction.user.remove_roles(role)
        await interaction.response.send_message(f"Removed the **{type.value}** role from you.", ephemeral=True)

    @app_commands.command(name="notifchannel", description="Set the notification channel for new streams or videos.")
    @app_commands.describe(
        type="Choose the notification type",
        channel="Select a channel for notifications"
    )
    @app_commands.choices(type=[
        app_commands.Choice(name="New Stream", value="New Stream"),
        app_commands.Choice(name="New Video", value="New Video")
    ])
    async def notifchannel(self, interaction: discord.Interaction, type: app_commands.Choice[str], channel: discord.TextChannel):
        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message("You need Manage Server permission to use this.", ephemeral=True)

        guild_id = interaction.guild.id
        if guild_id not in notif_channels:
            notif_channels[guild_id] = {}
        notif_channels[guild_id][type.value] = channel.id

        await interaction.response.send_message(f"Set {type.value} notifications to {channel.mention}", ephemeral=True)

@bot.event
async def on_guild_join(guild):
    red = discord.Color.red()
    for name in ["New Stream", "New Video"]:
        if not discord.utils.get(guild.roles, name=name):
            await guild.create_role(name=name, color=red)
    print(f"Created roles in {guild.name}")

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
        await bot.add_cog(MyBot(bot))
        await bot.start(TOKEN)

asyncio.run(main())


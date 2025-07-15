import discord
from discord.ext import commands, tasks
from discord import app_commands

import json, os, aiohttp

NOTIF_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/notifychannels.json'))
CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../config.json'))

def load_notif_data():
    if not os.path.exists(NOTIF_PATH):
        return {}
    with open(NOTIF_PATH, 'r') as f:
        return json.load(f)

def save_notif_data(data):
    with open(NOTIF_PATH, 'w') as f:
        json.dump(data, f, indent=4)

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {}
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

class notifier(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.last_stream_id = None
        self.config = load_config()
        self.api_key = self.config.get("API_KEY")
        self.channel_id = self.config.get("CHANNEL_ID")
        self.check_youtube_stream.start()

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

        data = load_notif_data()
        gid = str(interaction.guild.id)

        if gid not in data:
            data[gid] = {}

        data[gid][type.value] = channel.id
        save_notif_data(data)

        await interaction.response.send_message(f"Set **{type.value}** notifications to {channel.mention}", ephemeral=True)

    @tasks.loop(minutes=15)
    async def check_youtube_stream(self):
        if not self.api_key or not self.channel_id:
            return

        url = (
            f"https://www.googleapis.com/youtube/v3/search"
            f"?part=snippet&channelId={self.channel_id}&eventType=live&type=video&key={self.api_key}"
        )
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        print("YouTube API error:", resp.status)
                        return

                    data = await resp.json()
                    items = data.get("items", [])
                    if not items:
                        self.last_stream_id = None
                        return

                    video = items[0]
                    video_id = video["id"]["videoId"]
                    title = video["snippet"]["title"]

                    if video_id == self.last_stream_id:
                        return  # already notified

                    self.last_stream_id = video_id
                    stream_url = f"https://www.youtube.com/watch?v={video_id}"
                    thumbnail = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

                    data = load_notif_data()
                    for guild_id, types in data.items():
                        if "New Stream" not in types:
                            continue

                        channel = self.bot.get_channel(types["New Stream"])
                        if not channel:
                            continue

                        guild = self.bot.get_guild(int(guild_id))
                        role = discord.utils.get(guild.roles, name="New Stream") if guild else None
                        ping = role.mention if role else "@everyone"

                        embed = discord.Embed(
                            title="DOGE IS LIVE!",
                            description=f"[CLICK HERE TO WATCH]({stream_url})",
                            url=stream_url,
                            color=16763904
                        )
                        embed.set_image(url=thumbnail)

                        await channel.send(content=ping, embed=embed)

        except Exception as e:
            print("Error checking stream:", e)

    @check_youtube_stream.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    await bot.add_cog(notifier(bot))
    

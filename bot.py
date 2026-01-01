from keep_alive import keep_alive

keep_alive()  # Starts the web server in the background

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
from datetime import datetime, timezone

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True  # Required to access join dates

bot = commands.Bot(command_prefix="!", intents=intents)

# Milestone roles by days
MILESTONES = {
    1: "1-day member",
    2: "2-day member",
    3: "3-day member",
    7: "1-week member"
}

# Store which members have received which milestones
# Format: {guild_id: {member_id: [days_received, ...]}}
member_milestones = {}

@bot.event
async def on_ready():
    print(f"✅ Milestone Bot online as {bot.user}")
    for guild in bot.guilds:
        print(f"Connected guilds: {[g.name for g in bot.guilds]}")
    check_milestones.start()  # Start the background task

@tasks.loop(minutes=60)  # Checks every hour
async def check_milestones():
    now = datetime.now(timezone.utc)
    for guild in bot.guilds:
        channel = discord.utils.get(guild.text_channels, name="general")  # Change to your announcement channel
        if guild.id not in member_milestones:
            member_milestones[guild.id] = {}

        for member in guild.members:
            join_date = member.joined_at
            if join_date is None:
                continue

            days_in_server = (now - join_date).days

            if member.id not in member_milestones[guild.id]:
                member_milestones[guild.id][member.id] = []

            for milestone_days, role_name in MILESTONES.items():
                # Only assign if they haven't received this milestone yet
                if days_in_server >= milestone_days and milestone_days not in member_milestones[guild.id][member.id]:
                    role = discord.utils.get(guild.roles, name=role_name)
                    if role:
                        await member.add_roles(role)
                        await channel.send(f"{member.mention} has been given the **{role_name}** role for reaching {milestone_days} day(s) in the server!")
                        member_milestones[guild.id][member.id].append(milestone_days)

# Optional test command
@bot.command()
async def test_milestones(ctx):
    await ctx.send("Milestone check running...")
    await check_milestones()

bot.run(TOKEN)

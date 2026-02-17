import discord
from discord.ext import commands
import json
import os

# ---- CONFIG ----
TOKEN = os.environ['DISCORD_TOKEN']
LIFER_CHANNEL_ID = 1473138417809358991  # Replace with your #liferboard channel ID
YEAR_CHANNEL_ID = 1473138431000580126   # Replace with your #yearboard channel ID
DATA_FILE = "data.json"
# ----------------

# Enable message content intent so the bot can read commands
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True  # needed to see channels

bot = commands.Bot(command_prefix="!", intents=intents)

# Load or create database
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
else:
    data = {"Lifers": {}, "Year": {}}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def build_board(tab_name):
    board = data[tab_name]
    # Sort by total descending
    sorted_board = sorted(board.items(), key=lambda x: x[1]["total"], reverse=True)
    text = f"**{tab_name} Leaderboard**\n\n"
    for i, (user, info) in enumerate(sorted_board, 1):
        text += f"{i}. {user} — {info['total']}\n   Latest: {info['latest']}\n"
    if sorted_board:
        last_user, last_info = sorted_board[-1]
        text += f"\nMost recent addition: {last_user} — {last_info['latest']}"
    return text

async def post_board(channel_id, tab_name):
    channel = bot.get_channel(channel_id)
    if not channel:
        print(f"Channel {channel_id} not found!")
        return
    text = build_board(tab_name)
    pinned = await channel.pins()
    if pinned:
        await pinned[0].edit(content=text)
    else:
        msg = await channel.send(text)
        await msg.pin()

@bot.command()
async def setlifer(ctx, user: str, total: int, *, species: str):
    data["Lifers"][user] = {"total": total, "latest": species}
    save_data()
    await post_board(LIFER_CHANNEL_ID, "Lifers")
    await ctx.send(f"Liferboard updated for {user} ✅")

@bot.command()
async def setyear(ctx, user: str, total: int, *, species: str):
    data["Year"][user] = {"total": total, "latest": species}
    save_data()
    await post_board(YEAR_CHANNEL_ID, "Year")
    await ctx.send(f"Yearboard updated for {user} ✅")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

bot.run(TOKEN)


# redeploy test
git add bot.py
git commit -m "Force redeploy to update intents"
git push origin main

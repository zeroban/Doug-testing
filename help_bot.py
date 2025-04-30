import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from help_response import get_best_match_response

# Load the .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Set up Discord bot
intents = discord.Intents.default()
intents.message_content = True  # Important to read messages
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")

@bot.event
async def on_message(message):
    # Ignore the bot's own messages
    if message.author == bot.user:
        return

    # Only respond in the specified channel
    if str(message.channel.id) != "1366871858112364634":
        return

    question = message.content.strip()
    if question:
        response = get_best_match_response(question)
        await message.channel.send(response)

# Start bot
bot.run(TOKEN)

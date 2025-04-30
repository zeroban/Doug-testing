import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from help_bot import load_help_documents, find_best_match
from question_logger import log_unmatched_question

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.reactions = True
intents.message_content = True  # Required for reading message content
bot = commands.Bot(command_prefix="!", intents=intents)

help_texts = load_help_documents()

@bot.event
async def on_ready():
    print(f'{bot.user} is now running!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Optional: restrict bot to a specific channel
    # if message.channel.name != "your-bot-channel-name":
    #     return

    query = message.content.strip()
    result = find_best_match(query, help_texts)

    if result:
        filename, content, score = result
        response = await message.channel.send(
            f"**Match found in `{filename}` (Score: {score})**\n```{content}```"
        )
        await response.add_reaction("👍")
        await response.add_reaction("👎")
    else:
        log_unmatched_question(query, message.author)
        await message.channel.send("❌ Sorry, I couldn’t find a match for that.")

@bot.event
async def on_reaction_add(reaction, user):
    if user == bot.user:
        return

    if str(reaction.emoji) == "👍":
        print(f"{user} gave positive feedback on: {reaction.message.content[:60]}")
    elif str(reaction.emoji) == "👎":
        print(f"{user} gave negative feedback on: {reaction.message.content[:60]}")

bot.run(TOKEN)

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from pymongo import MongoClient  # Import pymongo
from help_response import get_best_match_response
from question_logger import log_unmatched_question

# Load environment variables
load_dotenv()

# MongoDB connection setup
mongo_uri = os.getenv("MONGO_URI")  # Add your MongoDB URI to your .env file
client = MongoClient(mongo_uri)
db = client['help_bot']  # Replace 'help_bot' with your database name
qa_collection = db['qa_entries']  # Replace 'qa_entries' with your collection name
feedback_collection = db['feedback']  # Create a new collection to track feedback

# Check MongoDB connection
try:
    client.admin.command('ping')  # This checks if MongoDB is connected
    print("Successfully connected to MongoDB!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

# Discord bot setup
TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
intents.messages = True
intents.reactions = True
intents.message_content = True  # Required for reading message content
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} is now running!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Specify the channel ID where the bot should reply
    designated_channel_id = 1366871858112364634  # Replace with the actual channel ID

    # Check if the message is in the designated channel
    if message.channel.id != designated_channel_id:
        return  # Ignore messages from other channels

    query = message.content.strip()
    result = get_best_match_response(query)

    if result:
        response = await message.channel.send(result)
        await response.add_reaction("👍")
        await response.add_reaction("👎")
    else:
        log_unmatched_question(query, message.author)
        await message.channel.send("❌ Sorry, I couldn’t find a match for that.")

@bot.event
async def on_reaction_add(reaction, user):
    if user == bot.user:
        return

    if str(reaction.emoji) in ["👍", "👎"]:
        # Find the Q&A entry that corresponds to this message
        question = reaction.message.content
        feedback = "positive" if str(reaction.emoji) == "👍" else "negative"
        
        # Log feedback to the database
        feedback_data = {
            "question": question,
            "user": user.name,
            "feedback": feedback,
            "reaction_timestamp": reaction.message.created_at,
        }

        # Insert the feedback into the 'feedback' collection
        feedback_collection.insert_one(feedback_data)

        print(f"Feedback received from {user} on question '{question}': {feedback}")

# Run the bot
bot.run(TOKEN)

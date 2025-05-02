import os
import re
from datetime import datetime
from dotenv import load_dotenv
from fuzzywuzzy import fuzz
from pymongo import MongoClient

# Load environment variables
load_dotenv()

# MongoDB connection using MONGO_URI from .env
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client['help_bot']  # Use your actual DB name
qa_collection = db['qa_entries']
feedback_collection = db['feedback']  # New feedback collection

# Normalize text for comparison
def normalize(text):
    return re.sub(r'[^\w\s]', '', text.lower())

# Fetch all Q&A entries from MongoDB
def get_qa_entries():
    return list(qa_collection.find())

# Find the best match to a user question
def get_best_match_response(user_question, threshold=60):
    user_q_norm = normalize(user_question)
    best_match = None
    best_score = 0

    qa_entries = get_qa_entries()

    for doc in qa_entries:
        doc_q_norm = normalize(doc["question"])
        score = fuzz.partial_ratio(user_q_norm, doc_q_norm)
        if score > best_score:
            best_score = score
            best_match = doc

    if best_match and best_score >= threshold:
        return f"**Answer from `{best_match['tags']}`:**\n{best_match['answer']}"
    else:
        return "I couldn't find any information related to that. Try rephrasing your question."

# Save feedback for no-match or reactions
def save_feedback(user_question, feedback_type, user_id=None):
    feedback_doc = {
        "user_id": user_id,
        "question": user_question,
        "feedback_type": feedback_type,  # e.g., "no_match", "positive", "negative"
        "submitted_at": datetime.utcnow()
    }
    feedback_collection.insert_one(feedback_doc)

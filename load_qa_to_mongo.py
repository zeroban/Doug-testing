import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client["help_bot"]
collection = db["qa_entries"]

# Basic keyword-to-tag mapping
keyword_tags = {
    "remove": "removal",
    "delete": "removal",
    "volunteer": "volunteers",
    "account": "accounts",
    "profile": "accounts",
    "merge": "duplicates",
    "schedule": "calendar",
    "shift": "calendar",
    "group": "groups",
    "edit": "profile",
    "login": "access",
    "claimed": "access",
    "organization": "org",
    "export": "data",
    "opportunity": "opportunities",
    "opp": "opportunities",
}

def generate_tags(question: str):
    tags = set()
    question_lower = question.lower()
    for keyword, tag in keyword_tags.items():
        if keyword in question_lower:
            tags.add(tag)
    return list(tags)

def parse_qa_file(file_path):
    qa_entries = []
    with open(file_path, "r", encoding="utf-8") as file:  # Specify UTF-8 encoding
        content = file.read()

    # Split the file content by Q: and A: lines
    qa_pairs = content.split("\nQ:")
    for pair in qa_pairs:
        if pair.strip():  # Ensure that the pair is not empty
            question_answer = pair.split("\nA:")
            if len(question_answer) == 2:
                question = question_answer[0].strip()
                answer = question_answer[1].strip()
                qa_entries.append({"question": question, "answer": answer})
    return qa_entries

# Folder containing the .txt files
help_docs_folder = "help_docs"

# Parse all .txt files in the folder
qa_entries = []
for filename in os.listdir(help_docs_folder):
    if filename.endswith(".txt"):
        file_path = os.path.join(help_docs_folder, filename)
        qa_entries.extend(parse_qa_file(file_path))

# Enrich each Q&A with tags
for entry in qa_entries:
    entry["tags"] = generate_tags(entry["question"])

# Insert into MongoDB
insert_result = collection.insert_many(qa_entries)
print(f"Inserted {len(insert_result.inserted_ids)} entries with tags.")

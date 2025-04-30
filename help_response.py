import os
from fuzzywuzzy import fuzz
import re

# Load help docs
def load_help_docs():
    help_docs = []
    help_folder = "help_docs"
    for filename in os.listdir(help_folder):
        if filename.endswith(".txt"):
            with open(os.path.join(help_folder, filename), "r", encoding="utf-8") as f:
                content = f.read()
                # Look for Q: and A: pairs
                qa_pairs = re.findall(r"Q:\s*(.*?)\s*A:\s*(.*?)(?=\nQ:|\Z)", content, re.DOTALL)
                for question, answer in qa_pairs:
                    help_docs.append({
                        "question": question.strip(),
                        "answer": answer.strip(),
                        "source": filename
                    })
    return help_docs

# Normalize text for comparison
def normalize(text):
    return re.sub(r'[^\w\s]', '', text.lower())

help_texts = load_help_docs()

# Main logic to find the best match
def get_best_match_response(user_question, threshold=60):
    user_q_norm = normalize(user_question)
    best_match = None
    best_score = 0

    for doc in help_texts:
        doc_q_norm = normalize(doc["question"])
        score = fuzz.partial_ratio(user_q_norm, doc_q_norm)
        if score > best_score:
            best_score = score
            best_match = doc

    if best_match and best_score >= threshold:
        return f"**Answer from `{best_match['source']}`:**\n{best_match['answer']}"
    else:
        return "I couldn't find any information related to that. Try rephrasing your question."

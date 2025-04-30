# question_logger.py
import json
from datetime import datetime

LOG_FILE = "unmatched_questions.json"

def log_unmatched_question(question, user):
    data = {
        "question": question,
        "user": str(user),
        "timestamp": datetime.now().isoformat()
    }
    try:
        with open(LOG_FILE, "r+") as f:
            logs = json.load(f)
            logs.append(data)
            f.seek(0)
            json.dump(logs, f, indent=2)
    except FileNotFoundError:
        with open(LOG_FILE, "w") as f:
            json.dump([data], f, indent=2)

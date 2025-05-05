# kb_initializer.py
from google.cloud import firestore
import json

db = firestore.Client()

def initialize_knowledge_base():
    # Initial set of questions and answers
    initial_kb = [
        {
            "question": "What are your business hours?",
            "answer": "We're open Monday to Friday from 9 AM to 5 PM."
        },
        {
            "question": "Where are you located?",
            "answer": "Our office is at 123 Business Street, Suite 100, San Francisco, CA 94105."
        },
        {
            "question": "How can I contact support?",
            "answer": "You can email support@company.com or call our support line at (555) 123-4567."
        }
    ]
    
    # Add to Firestore
    kb_ref = db.collection("knowledge_base")
    for item in initial_kb:
        kb_ref.add(item)
    
    print("Knowledge base initialized with basic questions")

if __name__ == "__main__":
    initialize_knowledge_base()
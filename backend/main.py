# main.py
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.cloud import firestore
import uuid
from typing import Dict, List, Optional
import os
from datetime import datetime

# Initialize Firestore
db = firestore.Client()

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Question(BaseModel):
    question_text: str
    call_id: str
    customer_number: str

class Answer(BaseModel):
    question_id: str
    answer_text: str
    supervisor_id: str

class Call(BaseModel):
    call_id: str
    customer_number: str
    status: str  # "active", "escalated", "resolved"
    questions: List[Dict]
    start_time: str
    end_time: Optional[str]

# In-memory store for active calls (would use Redis in production)
active_calls = {}

@app.post("/receive_call")
async def receive_call(customer_number: str):
    call_id = str(uuid.uuid4())
    new_call = {
        "call_id": call_id,
        "customer_number": customer_number,
        "status": "active",
        "questions": [],
        "start_time": str(datetime.now()),
        "end_time": None
    }
    active_calls[call_id] = new_call
    db.collection("calls").document(call_id).set(new_call)
    return {"call_id": call_id, "message": "Call received"}

@app.post("/handle_question")
async def handle_question(question: Question):
    # Check if call exists
    call_ref = db.collection("calls").document(question.call_id)
    call = call_ref.get()
    if not call.exists:
        raise HTTPException(status_code=404, detail="Call not found")
    
    # Try to answer from knowledge base
    answer = get_answer_from_kb(question.question_text)
    
    if answer:
        # Log the question and answer
        question_data = {
            "question_text": question.question_text,
            "answer_text": answer,
            "timestamp": str(datetime.now()),
            "source": "kb"
        }
        call_ref.update({
            "questions": firestore.ArrayUnion([question_data])
        })
        return {"answer": answer, "source": "kb"}
    else:
        # Escalate to human
        question_id = str(uuid.uuid4())
        question_data = {
            "question_id": question_id,
            "question_text": question.question_text,
            "timestamp": str(datetime.now()),
            "status": "pending",
            "source": "human"
        }
        call_ref.update({
            "questions": firestore.ArrayUnion([question_data]),
            "status": "escalated"
        })
        active_calls[question.call_id]["status"] = "escalated"
        
        # Notify supervisors via WebSocket (implementation omitted for brevity)
        notify_supervisors(question.call_id, question_data)
        
        return {"status": "escalated", "message": "Question escalated to human supervisor"}

@app.post("/submit_answer")
async def submit_answer(answer: Answer):
    # Store the answer in knowledge base
    question_ref = db.collection("questions").document(answer.question_id)
    question = question_ref.get()
    
    if not question.exists:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Update question with answer
    question_ref.update({
        "answer_text": answer.answer_text,
        "supervisor_id": answer.supervisor_id,
        "status": "answered",
        "answered_at": str(datetime.now())
    })
    
    # Add to knowledge base
    kb_ref = db.collection("knowledge_base").document()
    kb_ref.set({
        "question": question.to_dict()["question_text"],
        "answer": answer.answer_text,
        "source": f"human:{answer.supervisor_id}",
        "created_at": str(datetime.now())
    })
    
    # Update call status if all questions answered
    call_id = question.to_dict().get("call_id")
    if call_id:
        call_ref = db.collection("calls").document(call_id)
        call = call_ref.get().to_dict()
        
        all_answered = all(q.get("status") == "answered" for q in call["questions"])
        if all_answered:
            call_ref.update({"status": "resolved", "end_time": str(datetime.now())})
            active_calls.pop(call_id, None)
    
    return {"status": "success", "message": "Answer recorded and knowledge base updated"}

def get_answer_from_kb(question_text: str) -> Optional[str]:
    # Simple implementation - would use NLP for similarity in production
    kb_ref = db.collection("knowledge_base")
    docs = kb_ref.stream()
    
    for doc in docs:
        kb_item = doc.to_dict()
        if kb_item["question"].lower() in question_text.lower():
            return kb_item["answer"]
    
    return None

# WebSocket endpoint for real-time updates
@app.websocket("/ws/supervisor")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        # Handle incoming messages from supervisor UI
        # Implementation would include subscribing to updates
        pass
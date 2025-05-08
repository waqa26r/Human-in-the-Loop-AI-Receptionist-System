Human-in-the-Loop AI Receptionist System 🤖🧑‍💼

This project implements a simple yet effective **Human-in-the-Loop (HITL) AI System** that simulates a receptionist for a salon. The AI agent handles customer queries and escalates to a human supervisor when it does not know the answer. It also learns from the supervisor’s responses to improve over time.

---

## 🚀 Features

- Receive simulated phone calls (via API)
- AI agent answers from a knowledge base (KB)
- Escalates unknown questions to human supervisor
- Supervisor responds via a simple UI
- System sends response back to the customer
- Automatically updates the KB for future queries

---

## 📂 Project Structure

Human-in-the-Loop-AI-Receptionist-System/

├── backend/              # FastAPI backend

| ├── .env
| ├── .gitignore
| ├── firebase-config.json
| ├── firebase_test.py
| ├── follow_up.py
| ├── kb_initializer.py
| ├── livekit_handler.py
| ├── main.py
| ├── requirements.txt
| ├── test_firebase.py

│   └── ...

├── supervisor-ui/        # Supervisor frontend (React)

│   ├── App.jsx        # Simple UI for handling escalations

│   └── ...

└── README.md             # This file

graph TD
    A[Phone Call] --> B{LiveKit Server}
    B --> C[AI Receptionist]
    C --> D{Knows Answer?}
    D -->|Yes| E[Respond Automatically]
    D -->|No| F[Escalate to Supervisor]
    F --> G[React Dashboard]
    G --> H[Human Response]
    H --> I[Update Knowledge Base]

---

## 🧠 How It Works

### 1. 📞 Receive Call (`/receive_call`)

- Input: Customer phone number
- Output: A `call_id` (UUID)
- Usage: Simulates the customer initiating a call

### 2. ❓ Handle Question (`/handle_question`)

- Input: `question_text`, `customer_number`, `call_id`
- Output:
  - If answer exists in KB → return answer
  - If unknown → escalate to human, return pending status

### 3. 📬 Notify Supervisor (Simulated)

- On escalation, the system logs a help request
- Console log or webhook simulates message to supervisor

### 4. 👩‍💼 Submit Answer (`/submit_answer`)

- Supervisor enters answer via UI
- The answer is saved in the knowledge base
- The original customer is notified (console/webhook simulation)

### 5. 🔁 Learning

- Next time same question is asked, AI answers automatically
- No human needed anymore

---

## ✅ Task Completion

- [X] AI agent handles known questions
- [X] Escalation to human if answer unknown
- [X] Human responds via simple UI
- [X] Knowledge base is updated automatically
- [X] Customer gets follow-up message from AI

---

## 📌 API Endpoints Summary

| Endpoint             | Method | Description                                 |
| -------------------- | ------ | ------------------------------------------- |
| `/receive_call`    | POST   | Register new call and return call ID        |
| `/handle_question` | POST   | AI tries to answer, escalates if needed     |
| `/submit_answer`   | POST   | Human submits answer to unresolved question |

---

## 🛠️ Setup Instructions

### Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
python uvicorn main:app --reload
```

Runs at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

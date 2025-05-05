# follow_up.py
from google.cloud import firestore
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText

db = firestore.Client()

def check_for_follow_ups():
    # Get calls resolved in the last 24 hours with escalated questions
    cutoff = datetime.now() - timedelta(hours=24)
    calls_ref = db.collection("calls")
    
    query = calls_ref.where("status", "==", "resolved") \
                   .where("end_time", ">", cutoff.isoformat())
    
    for call_doc in query.stream():
        call = call_doc.to_dict()
        if any(q.get("source") == "human" for q in call.get("questions", [])):
            send_follow_up(call)

def send_follow_up(call_data):
    customer_email = get_customer_email(call_data["customer_number"])
    if not customer_email:
        return
        
    # Prepare email
    msg = MIMEText(f"""
    Dear Customer,
    
    Thank you for contacting us. We hope your questions were answered satisfactorily.
    
    Here's a summary of our interaction:
    {format_call_summary(call_data)}
    
    If you have any further questions, please don't hesitate to contact us.
    
    Best regards,
    Your Company
    """)
    
    msg['Subject'] = "Follow-up on your recent inquiry"
    msg['From'] = "noreply@company.com"
    msg['To'] = customer_email
    
    # Send email (simplified - would use proper email service in production)
    try:
        with smtplib.SMTP('localhost') as server:
            server.send_message(msg)
        print(f"Follow-up sent to {customer_email}")
    except Exception as e:
        print(f"Failed to send follow-up: {e}")

def get_customer_email(phone_number: str) -> Optional[str]:
    # In a real system, this would look up customer data
    return f"customer{phone_number[-4:]}@example.com"

def format_call_summary(call_data: dict) -> str:
    summary = []
    for q in call_data.get("questions", []):
        summary.append(f"Q: {q.get('question_text', '')}")
        summary.append(f"A: {q.get('answer_text', '')}")
        summary.append("")
    return "\n".join(summary)

if __name__ == "__main__":
    check_for_follow_ups()
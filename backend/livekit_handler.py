# livekit_handler.py
from livekit import rtc, agents
import asyncio
from typing import Optional
from datetime import datetime
import logging
from main import handle_question, receive_call

class AIReceptionist(agents.callbacks.Callbacks):
    def __init__(self):
        self._call_id: Optional[str] = None
        self._customer_number: Optional[str] = None
        
    async def on_track_published(self, track: rtc.TrackPublication, participant: rtc.Participant):
        if track.kind == rtc.TrackKind.KIND_AUDIO and participant.identity != "ai_receptionist":
            self._customer_number = participant.identity
            self._call_id = await receive_call(self._customer_number)
            
    async def on_data(self, data: bytes, participant: rtc.Participant):
        question_text = data.decode("utf-8")
        response = await handle_question(Question(
            question_text=question_text,
            call_id=self._call_id,
            customer_number=self._customer_number
        ))
        
        # Send response back to participant
        if response.get("answer"):
            await participant.publish_data(response["answer"].encode("utf-8"))
        elif response.get("status") == "escalated":
            await participant.publish_data("One moment while I connect you with a human supervisor...".encode("utf-8"))

async def run_agent():
    # Connect to LiveKit
    room = rtc.Room()
    await room.connect("wss://your-livekit-server.com", "api-key", "api-secret")
    
    # Create AI receptionist
    receptionist = AIReceptionist()
    room.on("track_published", receptionist.on_track_published)
    room.on("data", receptionist.on_data)
    
    # Join room as receptionist
    await room.local_participant.set_name("AI Receptionist")
    
    print("AI Receptionist is ready to receive calls...")
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(run_agent())
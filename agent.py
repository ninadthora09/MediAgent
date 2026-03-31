import os
from groq import Groq
from tools import check_slots, book_appointment, cancel_appointment

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# In-memory chat history
chat_histories = {}

def chat(session_id: str, user_message: str) -> str:
    if session_id not in chat_histories:
        chat_histories[session_id] = []

    history = chat_histories[session_id]

    message_lower = user_message.lower()

    # ---------- TOOL CALLING LOGIC ----------

    try:
        # Check slots
        if "slot" in message_lower or "available" in message_lower:
            # VERY basic extraction (can improve later)
            return "Please provide doctor name and date (YYYY-MM-DD) to check availability."

        # Book appointment
        elif "book" in message_lower or "appointment" in message_lower:
            return "Please provide your name, email, doctor name, date (YYYY-MM-DD), and time."

        # Cancel appointment
        elif "cancel" in message_lower:
            return "Please provide your appointment ID to cancel."

    except Exception as e:
        print("Tool error:", e)

    # ---------- GROQ RESPONSE ----------

    try:
        messages = [
            {
                "role": "system",
                "content": """You are MediAgent, a helpful healthcare assistant.
You help users book, check, and cancel appointments.
Always be polite and professional."""
            }
        ]

        # Add history
        for msg in history:
            messages.append(msg)

        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages
        )

        reply = response.choices[0].message.content

        # Save to history
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": reply})

        return reply

    except Exception as e:
        print("Groq error:", e)
        return "Sorry, something went wrong. Please try again."
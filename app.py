import os
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS
from agent import chat
from database import init_db

app = Flask(__name__)
CORS(app)

# Initialize database on startup
try:
    init_db()
except Exception as e:
    print("DB already initialized or error:", e)


@app.route("/", methods=["GET"])
def home():
    return "Backend is running 🚀"


@app.route("/chat", methods=["POST"])
def chat_endpoint():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data received."}), 400

        user_message = data.get("message", "").strip()
        session_id = data.get("session_id", "default")

        if not user_message:
            return jsonify({"error": "Message cannot be empty."}), 400

        try:
            response = chat(session_id, user_message)
        except Exception as e:
            print("Chat error:", e)
            return jsonify({"error": "AI service unavailable"}), 500

        return jsonify({
            "reply": response,
            "session_id": session_id
        })

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": "Something went wrong. Please try again."}), 500


@app.route("/slots", methods=["GET"])
def get_slots():
    try:
        from database import get_connection
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT doctor_name, slot_date, slot_time, is_booked
                FROM slots
                ORDER BY doctor_name, slot_date, slot_time
            """).fetchall()

        slots = [dict(row) for row in rows]
        return jsonify({"slots": slots})

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500


@app.route("/appointments", methods=["GET"])
def get_appointments():
    try:
        from database import get_connection
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM appointments
                ORDER BY created_at DESC
            """).fetchall()

        appointments = [dict(row) for row in rows]
        return jsonify({"appointments": appointments})

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


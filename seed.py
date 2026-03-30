from database import get_connection, init_db

def seed_slots():
    conn = get_connection()
    cursor = conn.cursor()

    # Clear existing slots first
    cursor.execute("DELETE FROM slots")

    slots = [
        ("Dr. Sharma",  "2025-04-01", "09:00 AM"),
        ("Dr. Sharma",  "2025-04-01", "10:00 AM"),
        ("Dr. Sharma",  "2025-04-01", "11:00 AM"),
        ("Dr. Sharma",  "2025-04-01", "02:00 PM"),
        ("Dr. Sharma",  "2025-04-01", "04:00 PM"),

        ("Dr. Mehta",   "2025-04-01", "09:00 AM"),
        ("Dr. Mehta",   "2025-04-01", "11:00 AM"),
        ("Dr. Mehta",   "2025-04-01", "03:00 PM"),

        ("Dr. Sharma",  "2025-04-02", "09:00 AM"),
        ("Dr. Sharma",  "2025-04-02", "10:00 AM"),
        ("Dr. Sharma",  "2025-04-02", "02:00 PM"),

        ("Dr. Mehta",   "2025-04-02", "10:00 AM"),
        ("Dr. Mehta",   "2025-04-02", "01:00 PM"),
        ("Dr. Mehta",   "2025-04-02", "04:00 PM"),
    ]

    cursor.executemany("""
        INSERT INTO slots (doctor_name, slot_date, slot_time, is_booked)
        VALUES (?, ?, ?, 0)
    """, slots)

    conn.commit()
    conn.close()
    print(f"{len(slots)} slots seeded successfully.")

if __name__ == "__main__":
    init_db()
    seed_slots()
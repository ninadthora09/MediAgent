from database import get_connection
from email_service import send_confirmation_email

def check_slots(doctor_name: str, slot_date: str) -> str:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT slot_time FROM slots
        WHERE doctor_name = ? AND slot_date = ? AND is_booked = 0
    """, (doctor_name, slot_date))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return f"No available slots for {doctor_name} on {slot_date}."

    times = [row["slot_time"] for row in rows]
    return f"Available slots for {doctor_name} on {slot_date}: {', '.join(times)}"


def book_appointment(patient_name: str, patient_email: str,
                     doctor_name: str, slot_date: str, slot_time: str) -> str:
    conn = get_connection()
    cursor = conn.cursor()

    # Check if slot exists and is free
    cursor.execute("""
        SELECT id FROM slots
        WHERE doctor_name = ? AND slot_date = ? AND slot_time = ? AND is_booked = 0
    """, (doctor_name, slot_date, slot_time))

    slot = cursor.fetchone()

    if not slot:
        return f"Sorry, {slot_time} with {doctor_name} on {slot_date} is not available. Please check available slots."

    # Mark slot as booked
    cursor.execute("""
        UPDATE slots SET is_booked = 1
        WHERE id = ?
    """, (slot["id"],))

    # Save appointment
    cursor.execute("""
        INSERT INTO appointments (patient_name, patient_email, doctor_name, slot_date, slot_time)
        VALUES (?, ?, ?, ?, ?)
    """, (patient_name, patient_email, doctor_name, slot_date, slot_time))

    appointment_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # Send confirmation email
    send_confirmation_email(
        to_email=patient_email,
        patient_name=patient_name,
        doctor_name=doctor_name,
        slot_date=slot_date,
        slot_time=slot_time
    )

    return f"Appointment confirmed! {patient_name} booked with {doctor_name} on {slot_date} at {slot_time}. Confirmation sent to {patient_email}. Appointment ID: {appointment_id}"


def cancel_appointment(appointment_id: int) -> str:
    conn = get_connection()
    cursor = conn.cursor()

    # Check if appointment exists
    cursor.execute("""
        SELECT * FROM appointments WHERE id = ?
    """, (appointment_id,))

    appointment = cursor.fetchone()

    if not appointment:
        return f"No appointment found with ID {appointment_id}."

    # Free up the slot
    cursor.execute("""
        UPDATE slots SET is_booked = 0
        WHERE doctor_name = ? AND slot_date = ? AND slot_time = ?
    """, (appointment["doctor_name"], appointment["slot_date"], appointment["slot_time"]))

    # Delete appointment
    cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))

    conn.commit()
    conn.close()

    return f"Appointment ID {appointment_id} with {appointment['doctor_name']} on {appointment['slot_date']} at {appointment['slot_time']} has been cancelled successfully."
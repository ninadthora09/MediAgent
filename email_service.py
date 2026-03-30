import os
import resend

resend.api_key = os.environ.get("RESEND_API_KEY")

def send_confirmation_email(to_email: str, patient_name: str,
                             doctor_name: str, slot_date: str, slot_time: str):
    try:
        response = resend.Emails.send({
            "from": "MediAgent <noreply@yourdomain.com>",
            "to": to_email,
            "subject": "Appointment Confirmed — MediAgent",
            "html": f"""
            <div style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #1A1A2E;">Appointment Confirmed</h2>
                <p>Hello <strong>{patient_name}</strong>,</p>
                <p>Your appointment has been successfully booked.</p>
                <table style="border-collapse: collapse; margin-top: 10px;">
                    <tr>
                        <td style="padding: 8px; font-weight: bold;">Doctor</td>
                        <td style="padding: 8px;">{doctor_name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; font-weight: bold;">Date</td>
                        <td style="padding: 8px;">{slot_date}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; font-weight: bold;">Time</td>
                        <td style="padding: 8px;">{slot_time}</td>
                    </tr>
                </table>
                <p style="margin-top: 20px;">Please arrive 10 minutes early.</p>
                <p style="color: #888888; font-size: 12px;">
                    This is an automated message from MediAgent.
                </p>
            </div>
            """
        })
        print(f"Email sent successfully. ID: {response['id']}")
        return response

    except Exception as e:
        print(f"Email failed: {e}")
        return None
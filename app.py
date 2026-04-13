from fastapi import FastAPI
from bms import check_ticket, send_notification, send_email_notification

app = FastAPI()

@app.get("/check-and-notify")
def check_and_notify():
    try:
        if check_ticket():
            print("✅ Tickets Released!")
            ntfy_result = send_notification()
            email_result = send_email_notification()
            return {
                "status": "available",
                "ntfy_notified": ntfy_result,
                "email_notified": email_result
            }
        else:
            print("❌ Still not released")
            return {"status": "not_available", "ntfy_notified": False, "email_notified": False}
    except Exception as e:
        print("Error:", e)
        return {"status": "error", "message": str(e)}

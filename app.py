from fastapi import FastAPI
from bms import check_ticket, send_notification

app = FastAPI()

@app.get("/check-and-notify")
def check_and_notify():
    try:
        if check_ticket():
            print("✅ Tickets Released!")
            send_notification()
            return {"status": "available", "notified": True}
        else:
            print("❌ Still not released")
            return {"status": "not_available", "notified": False}
    except Exception as e:
        print("Error:", e)
        return {"status": "error", "message": str(e)}

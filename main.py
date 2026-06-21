from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv
import os
import requests

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",                     # Allows your local React server to test it
        "http://localhost:5174",                     # Allows your active React server on port 5174 to test it
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "https://garv-agarwal2409.vercel.app" # Replace with your actual live Vercel domain link
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")


class ContactForm(BaseModel):
    name: str
    email: EmailStr
    message: str


@app.post("/contact")
async def contact(form: ContactForm):
    try:
        # Check if environment variables are configured
        if not RESEND_API_KEY or not RECEIVER_EMAIL:
            raise ValueError("Resend API Key or Receiver Email is missing from environment variables (.env). Please set RESEND_API_KEY and RECEIVER_EMAIL.")
        
        # Send HTTP POST to Resend API
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "from": "Portfolio Contact Form <onboarding@resend.dev>",
                "to": RECEIVER_EMAIL,
                "reply_to": form.email,
                "subject": f"Portfolio Contact From {form.name}",
                "html": f"""
                <h3>New Message from Portfolio Contact Form</h3>
                <p><strong>Name:</strong> {form.name}</p>
                <p><strong>Email:</strong> {form.email}</p>
                <p><strong>Message:</strong></p>
                <p>{form.message}</p>
                """
            }
        )

        res_data = response.json()
        
        if response.status_code != 200:
            raise Exception(res_data.get("message", "Failed to send email via Resend API."))

        return {
            "message": "Message sent successfully!"
        }

    except Exception as e:
        import traceback
        traceback.print_exc()

        return {
            "message": "Failed to send message.",
            "error": str(e)
        }
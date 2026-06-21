from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",                     # Allows your local React server to test it
        "http://localhost:5174",                     # Allows your active React server on port 5174 to test it
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "https://portfolio-garv-frontend.vercel.app" # Replace with your actual live Vercel domain link
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")


class ContactForm(BaseModel):
    name: str
    email: EmailStr
    message: str


@app.post("/contact")
async def contact(form: ContactForm):
    try:
        msg = MIMEMultipart()

        msg["From"] = EMAIL_ADDRESS
        msg["To"] = RECEIVER_EMAIL
        msg["Subject"] = f"Portfolio Contact From {form.name}"

        body = f"""
New Portfolio Message

Name: {form.name}

Email: {form.email}

Message:
{form.message}
"""

        msg.attach(MIMEText(body, "plain"))

        # --- REPLACE YOUR OLD SMTP SETUP WITH THIS ---
        import socket

        # Force smtplib to route strictly over IPv4 (fixes Render's Network is unreachable error)
        class IPv4SMTP_SSL(smtplib.SMTP_SSL):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
            
            def _get_socket(self, host, port, timeout):
                self.file = None
                # Force AF_INET (IPv4) instead of letting it default to IPv6
                return socket.create_connection((host, port), timeout, source_address=None)

        # Connect securely using our custom IPv4 SSL handler on port 465
        server = IPv4SMTP_SSL("smtp.gmail.com", 465)
        
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        # ---------------------------------------------

        return {
            "message":
            "Message sent successfully!"
        }

    except Exception as e:
        print(e)

        return {
            "message":
            "Failed to send message."
        }

import smtplib
import os
import bcrypt

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

SENDER_EMAIL = os.getenv("sender_email")
SENDER_PASSKEY = os.getenv("passkey")

# Check environment variables
print("Sender email:", SENDER_EMAIL)
print("Passkey loaded:", bool(SENDER_PASSKEY))


def sendEmail(to_email: str, subject: str, body: str):
    # Check email configuration
    if not SENDER_EMAIL or not SENDER_PASSKEY:
        return False, "Sender email or passkey is missing in .env file"

    # Prepare email
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        # Connect to Gmail SMTP server
        with smtplib.SMTP(
            host=SMTP_SERVER,
            port=SMTP_PORT,
            timeout=30
        ) as server:

            server.ehlo()
            server.starttls()
            server.ehlo()

            # Login to sender account
            server.login(
                user=SENDER_EMAIL,
                password=SENDER_PASSKEY
            )

            # Send email
            server.send_message(msg)

        return True, "Email sent successfully"

    except (smtplib.SMTPException, OSError) as e:
        error_message = f"Email sending failed: {repr(e)}"
        print(error_message)
        return False, error_message

    except Exception as e:
        error_message = f"Unexpected email error: {repr(e)}"
        print(error_message)
        return False, error_message


def generateHashPassword(password: str):
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )


def validateHashPassword(password, hash_password):
    if isinstance(hash_password, str):
        hash_password = hash_password.encode("utf-8")

    return bcrypt.checkpw(
        password.encode("utf-8"),
        hash_password
    )


class EmailTemplates:

    @staticmethod
    def registerEmailTemplate(otp: int, username: str = "Dear"):
        template = f"""Hello {username},

Thanks for choosing SNS app to manage your files and notes.

Your OTP: {otp}

If you did not register for this app, please ignore this email.
Do not share your OTP with anyone.

Thank you.

Best Wishes,
SNS Management
"""
        return template

    @staticmethod
    def forgotPasswordTemplate(url: str, username: str = "User"):
        template = f"""Hello {username},

To manage your files and notes, reset your password and log in again.

Your password reset link:
{url}

If you did not request this, please ignore this email.

Thanks for choosing SNS app.

Regards,
SNS Management
"""
        return template


import requests
import os
from dotenv import load_dotenv
import logging

load_dotenv()

def send_single_email(to_address: str, subject: str, message: str):
    try:
        api_key = os.getenv("MAILGUN_API_KEY")
        resp = requests.post(os.getenv("MAILGUN_API_URL"), auth=("api", api_key), 
                             data={"from": "FROM_EMAIL_ADDRESS",
                            "to": to_address, "subject": subject, "text": message})
        if resp.status_code == 200:
            logging.info(f"Successfully sent an email to '{to_address}' via Mailgun API.")
        else:
            logging.error(f"Could not send the email, reason: {resp.text}")
    except Exception as ex:
        logging.exception(f"Mailgun error: {ex}")

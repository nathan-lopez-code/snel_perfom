from twilio.rest import Client
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_sms_notification(to_phone_number, message_body):
    """
    Envoie un SMS via Twilio.
    """

    to_phone_number = '+243' + to_phone_number[1:] # standariser le numero de telephoe
    if not settings.TWILIO_ACCOUNT_SID or \
            not settings.TWILIO_AUTH_TOKEN or \
            not settings.TWILIO_PHONE_NUMBER:
        logger.error("Twilio credentials are not set in settings.py. SMS not sent.")
        return False

    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    try:
        message = client.messages.create(
            to=to_phone_number,
            from_=settings.TWILIO_PHONE_NUMBER,
            body=message_body
        )
        logger.info(f"SMS sent successfully to {to_phone_number}. SID: {message.sid}")
        return True
    except Exception as e:
        logger.error(f"Failed to send SMS to {to_phone_number}. Error: {e}")
        return False
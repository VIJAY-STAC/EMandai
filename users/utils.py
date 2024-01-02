import base64
import string 
from django.core.cache import cache
from django.utils.crypto import get_random_string
from django.conf import settings
from django.core.mail import send_mail


def verify_otp(user_id, otp):
    PASSWORD_RESET_KEY = "user_password_reset_key.{otp_key}"
    base_otp_key = base64.b64encode(str(user_id).encode()).decode()

    otp_key = PASSWORD_RESET_KEY.format(otp_key=base_otp_key)

    cached_otp = cache.get(otp_key)

    if cached_otp is None:
        return "otp_expired", None

    if not cached_otp == otp:
        return "otp_invalid", None

    return None, otp_key


def generate_otp_and_key(uuid, secret_key):
    otp = get_random_string(length=6, allowed_chars=string.digits)
    base_otp_key = base64.b64encode(str(uuid).encode()).decode()
    otp_key = secret_key.format(otp_key=base_otp_key)

    return otp, otp_key


def send_custom_email(subject,message,recipient_list):
    subject = subject 
    message = message
    email_from = settings.EMAIL_HOST_USER
    recipient_list = recipient_list
    send_mail( subject, message, email_from, recipient_list )
    return True

import frappe
import requests
import json
import datetime
from frappe import _


@frappe.whitelist()
def send_custom_sms(to, message):
    if not to.startswith("+"):
        to = "+" + to

    account_sid = frappe.conf.get("twilio_account_sid")
    auth_token = frappe.conf.get("twilio_auth_token")
    from_number = frappe.conf.get("twilio_phone_number")

    if not all([account_sid, auth_token, from_number]):
        frappe.throw(_("Twilio credentials are not configured properly."))

    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"

    data = {
        "From": from_number,
        "To": to,
        "Body": message
    }

    try:
        response = requests.post(url, data=data, auth=(account_sid, auth_token))
        response.raise_for_status()
        return {"status": "success", "sid": response.json().get("sid")}
    except requests.exceptions.RequestException as e:
        frappe.log_error(frappe.get_traceback(), "Twilio SMS Send Error")
        frappe.throw(_("SMS failed: ") + str(e))


@frappe.whitelist()
def send_bulk_sms(phone_numbers, message):
    account_sid = frappe.conf.get("twilio_account_sid")
    auth_token = frappe.conf.get("twilio_auth_token")
    from_number = frappe.conf.get("twilio_phone_number")

    if not all([account_sid, auth_token, from_number]):
        return {"status": "error", "error": "Twilio credentials missing"}

    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    errors = []

    if isinstance(phone_numbers, str):
        phone_numbers = json.loads(phone_numbers)

    for to in phone_numbers:
        if not to.startswith("+"):
            to = "+" + to

        data = {
            "From": from_number,
            "To": to,
            "Body": message
        }

        try:
            response = requests.post(url, data=data, auth=(account_sid, auth_token))
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            errors.append(f"{to}: {str(e)}")

    if errors:
        return {"status": "error", "error": "; ".join(errors)}
    return {"status": "success"}


@frappe.whitelist()
def make_voice_call(to):
    if not to.startswith("+"):
        to = "+" + to

    account_sid = frappe.conf.get("twilio_account_sid")
    auth_token = frappe.conf.get("twilio_auth_token")
    from_number = frappe.conf.get("twilio_phone_number")  # Replace with twilio_voice_number if needed

    if not all([account_sid, auth_token, from_number]):
        frappe.throw(_("Twilio credentials are not configured properly."))

    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Calls.json"

    data = {
        "From": from_number,
        "To": to,
        "Url": "https://demo.twilio.com/welcome/voice/"
    }

    try:
        response = requests.post(url, data=data, auth=(account_sid, auth_token))
        response.raise_for_status()
        return {"status": "success", "sid": response.json().get("sid")}
    except requests.exceptions.RequestException as e:
        frappe.log_error(frappe.get_traceback(), "Twilio Voice Call Error")
        frappe.throw(_("Voice call failed: ") + str(e))




@frappe.whitelist()
def schedule_sms(phone_numbers, message, delay_minutes=5):
    """
    Schedule SMS to be sent after a delay (default 5 minutes).
    """
    if isinstance(phone_numbers, str):
        phone_numbers = json.loads(phone_numbers)

    # Calculate ETA
    eta = frappe.utils.add_to_date(
        frappe.utils.now_datetime(), 
        minutes=int(delay_minutes)
    )

    # Enqueue background job
    frappe.enqueue(
        "web_form_integration.api.twilio_sms._send_bulk_sms_job",
        phone_numbers=phone_numbers,
        message=message,
        enqueue_after_commit=True,
        job_name=f"Delayed SMS ({delay_minutes}min)",
        eta=eta
    )

    return {"status": "scheduled", "delay_minutes": delay_minutes}


def _send_bulk_sms_job(phone_numbers, message):
    """
    Actual job to send SMS (called by scheduler after delay).
    """
    account_sid = frappe.conf.get("twilio_account_sid")
    auth_token = frappe.conf.get("twilio_auth_token")
    from_number = frappe.conf.get("twilio_phone_number")

    if not all([account_sid, auth_token, from_number]):
        frappe.log_error("Twilio credentials missing", "Twilio SMS Config")
        return {"status": "error", "error": "Twilio credentials missing"}

    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    errors = []

    for to in phone_numbers:
        if not to.startswith("+"):
            to = "+" + to
        data = {"From": from_number, "To": to, "Body": message}
        try:
            response = requests.post(url, data=data, auth=(account_sid, auth_token))
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            errors.append(f"{to}: {str(e)}")

    if errors:
        return {"status": "error", "error": "; ".join(errors)}
    return {"status": "success"}
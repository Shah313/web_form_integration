import frappe
import requests
import json
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

import frappe
import requests
from frappe import _


@frappe.whitelist()
def make_voice_call(to):
    if not to.startswith("+"):
        to = "+" + to

    account_sid = frappe.conf.get("twilio_account_sid")
    auth_token = frappe.conf.get("twilio_auth_token")
    from_number = frappe.conf.get("twilio_phone_number")  # Or your voice number

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
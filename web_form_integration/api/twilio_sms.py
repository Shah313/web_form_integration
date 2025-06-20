import frappe
from twilio.rest import Client
import json

@frappe.whitelist()
def send_custom_sms(to, message):
    # Ensure number starts with '+'
    if not to.startswith("+"):
        to = "+{}".format(to)

    sid = frappe.conf.get("twilio_account_sid")
    token = frappe.conf.get("twilio_auth_token")
    from_number = frappe.conf.get("twilio_phone_number")

    if not (sid and token and from_number):
        frappe.throw("Twilio credentials missing")

    client = Client(sid, token)

    try:
        msg = client.messages.create(
            body=message,
            from_=from_number,
            to=to
        )
        return {"status": "success", "sid": msg.sid}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Twilio Custom SMS Error")
        frappe.throw(f"SMS failed: {str(e)}")


@frappe.whitelist()
def send_bulk_sms(phone_numbers, message):
    sid = frappe.conf.get("twilio_account_sid")
    token = frappe.conf.get("twilio_auth_token")
    from_number = frappe.conf.get("twilio_phone_number")

    if not (sid and token and from_number):
        return {"status": "error", "error": "Twilio credentials missing"}

    client = Client(sid, token)
    errors = []

    # If passed as JSON string from JS, convert it to list
    if isinstance(phone_numbers, str):
        phone_numbers = json.loads(phone_numbers)

    for number in phone_numbers:
        try:
            client.messages.create(
                body=message,
                from_=from_number,
                to=number
            )
        except Exception as e:
            errors.append(f"{number}: {str(e)}")

    if errors:
        return {"status": "error", "error": "; ".join(errors)}
    return {"status": "success"}

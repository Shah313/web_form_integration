import frappe
import requests
from frappe import _
from werkzeug.wrappers import Response

@frappe.whitelist()
def connect_agent_and_customer(agent_number, customer_number):
    """
    Step 1: Call the agent, pass redirect to our TwiML when answered
    """
    if not agent_number.startswith("+"):
        agent_number = "+" + agent_number.strip()
    if not customer_number.startswith("+"):
        customer_number = "+" + customer_number.strip()

    account_sid = frappe.conf.get("twilio_account_sid")
    auth_token = frappe.conf.get("twilio_auth_token")
    from_number = frappe.conf.get("twilio_voice_number")

    if not all([account_sid, auth_token, from_number]):
        frappe.throw(_("Twilio credentials missing in site_config.json"))

    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Calls.json"

    callback_url = f"https://roothome.erpnext.com/api/method/web_form_integration.api.twilio_voice.generate_twiml?customer_number={customer_number}"
    
    # print("Generated Callback URL:", callback_url)

    
    call_data = {
        "From": from_number,
        "To": agent_number,
        "Url": callback_url
    }

    try:
        response = requests.post(url, data=call_data, auth=(account_sid, auth_token))
        response.raise_for_status()
        sid = response.json().get("sid")  # Important to capture Call SID
        return {"status": "success", "sid": sid}
    except requests.exceptions.RequestException as e:
        frappe.log_error(frappe.get_traceback(), "Twilio Connect Call Error")


        
@frappe.whitelist(allow_guest=True)
def generate_twiml(customer_number):
    if not customer_number.startswith("+"):
        customer_number = "+" + customer_number.strip()

    response_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Dial>{customer_number}</Dial>
</Response>
"""

    return Response(response_xml, content_type="text/xml")

@frappe.whitelist()
def end_call(call_sid):
    """
    Step 3: Forcefully disconnect an ongoing call from ERPNext
    """
    account_sid = frappe.conf.get("twilio_account_sid")
    auth_token = frappe.conf.get("twilio_auth_token")

    if not (account_sid and auth_token):
        frappe.throw(_("Twilio credentials missing"))

    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Calls/{call_sid}.json"

    try:
        response = requests.post(url, data={"Status": "completed"}, auth=(account_sid, auth_token))
        response.raise_for_status()
        return {"status": "disconnected"}
    except requests.exceptions.RequestException as e:
        frappe.log_error(frappe.get_traceback(), "Twilio Call Disconnect Error")
        frappe.throw(_("Failed to disconnect call: ") + str(e))

import frappe
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from twilio.twiml.voice_response import VoiceResponse, Dial, Number, Client

@frappe.whitelist(allow_guest=True)
def handle_outgoing_call():
    """Handle outgoing call TwiML generation"""
    try:
        to = frappe.form_dict.get("To") or frappe.request.args.get("To")
        caller_id = frappe.conf.twilio_voice_number

        if not to:
            return str(VoiceResponse().reject())

        response = VoiceResponse()
        dial = Dial(callerId=caller_id)
        dial.append(Number(to))
        response.append(dial)

        frappe.local.response["http_status_code"] = 200
        frappe.local.response["headers"] = {"Content-Type": "text/xml"}
        frappe.local.response["message"] = str(response)
        
    except Exception as e:
        frappe.log_error("Outgoing Call TwiML Error", str(e))
        return str(VoiceResponse().reject())

@frappe.whitelist(allow_guest=True)
def handle_incoming_call():
    """Handle incoming call TwiML generation"""
    try:
        response = VoiceResponse()
        dial = Dial()
        dial.append(Client("browser_user"))  # Connects to browser client
        response.append(dial)

        frappe.local.response["http_status_code"] = 200
        frappe.local.response["headers"] = {"Content-Type": "text/xml"}
        frappe.local.response["message"] = str(response)
        
    except Exception as e:
        frappe.log_error("Incoming Call TwiML Error", str(e))
        return str(VoiceResponse().reject())
        

@frappe.whitelist()
def get_twilio_access_token():
    try:
        account_sid = frappe.conf.twilio_account_sid
        api_key = frappe.conf.twilio_api_key_sid
        api_secret = frappe.conf.twilio_api_key_secret
        twiml_app_sid = frappe.conf.twilio_twiml_app_sid

        # Validate configuration
        if not all([account_sid, api_key, api_secret, twiml_app_sid]):
            frappe.throw("Missing Twilio configuration in site_config.json")

        # Generate token
        identity = f"erpnext_{frappe.session.user}"[:64]
        token = AccessToken(account_sid, api_key, api_secret, identity=identity, ttl=3600)
        
        voice_grant = VoiceGrant(
            outgoing_application_sid=twiml_app_sid,
            incoming_allow=True
        )
        token.add_grant(voice_grant)

        return token.to_jwt()

    except Exception as e:
        frappe.log_error("Twilio Token Error", str(e))
        frappe.throw("Failed to generate token. Check server logs.")
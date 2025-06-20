import frappe

import json

@frappe.whitelist(allow_guest=True)
def validate_token(opportunity_name, access_token):
    doc = frappe.get_doc("Opportunity", opportunity_name)
    if doc.state != access_token:
        frappe.throw("Invalid or expired access token.")
    return {"status": "valid"}





@frappe.whitelist(allow_guest=True)
def update_opportunity_data(opportunity_name, access_token, data):
    doc = frappe.get_doc("Opportunity", opportunity_name)

    if doc.state != access_token:
        frappe.throw("Invalid or expired token.")

    # ✅ Convert JSON string to dict
    parsed_data = json.loads(data)

    for fieldname, value in parsed_data.items():
        doc.set(fieldname, value)

    doc.state = ""  # Optional: prevent reuse
    doc.save(ignore_permissions=True)
    return {"status": "success"}

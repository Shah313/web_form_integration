import frappe

import json

from frappe.desk.doctype.notification_log.notification_log import enqueue_create_notification

@frappe.whitelist(allow_guest=True)
def validate_token(opportunity_name, access_token):
    doc = frappe.get_doc("Opportunity", opportunity_name)
    if doc.custom_access_token != access_token:
        frappe.throw("Invalid or expired access token.")
    return {"status": "valid"}





@frappe.whitelist(allow_guest=True)
def update_opportunity_data(opportunity_name, access_token, data):
    import json

    # Load data if sent as JSON string
    if isinstance(data, str):
        data = json.loads(data)

    doc = frappe.get_doc("Opportunity", opportunity_name)

    if doc.custom_access_token != access_token:
        frappe.throw("Invalid or expired access token.")

    # Set the submitted data into Opportunity fields
    for key, value in data.items():
        doc.set(key, value)

    doc.save(ignore_permissions=True)

    # ✅ Manually create a Notification Log (bypassing the queue)
    notif = frappe.new_doc("Notification Log")
    notif.update({
        "type": "Alert",
        "document_type": "Opportunity",
        "document_name": doc.name,
        "subject": "Buyer Form Submitted",
        "email_content": f"Buyer form submitted for Opportunity <b>{doc.name}</b>.",
        "for_user": doc.owner,
        "from_user": frappe.session.user if frappe.session.user != "Guest" else "Administrator"
    })
    notif.insert(ignore_permissions=True)

    # ✅ This will ensure the bell icon updates immediately
    frappe.publish_realtime("notification", after_commit=True)

    return {"status": "success"}

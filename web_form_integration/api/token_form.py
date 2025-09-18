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

    if isinstance(data, str):
        data = json.loads(data)

    doc = frappe.get_doc("Opportunity", opportunity_name)

    if doc.custom_access_token != access_token:
        frappe.throw("Invalid or expired access token.")

    FILE_CHILD_TABLE_MAP = {
        "custom_buyer_1_id_passport": "buyer_1_id_passport",
        "custom_buyer_1_proof_of_address": "buyer_1_proof_of_address",
        "custom_buyer_2_id": "buyer_2_id",
        "custom_buyer_2_proof_of_address": "buyer_2_proof_of_address",
        "custom_proof_of_funds": "proof_of_funds"
    }

    for key, value in data.items():
        try:
            if key in FILE_CHILD_TABLE_MAP and value:
                child_field = FILE_CHILD_TABLE_MAP[key]
                doc.set(key, [])
                doc.append(key, {child_field: value})
            elif isinstance(value, str) and value.startswith("/files/"):
                frappe.logger().info(f"Skipped unmapped file field: {key} → {value}")
                continue
            elif isinstance(value, list):
                continue
            else:
                doc.set(key, value)
        except Exception as e:
            frappe.log_error(f"Error setting field {key} with value {value}: {str(e)}", "Opportunity Web Form Update")
            continue

    doc.save(ignore_permissions=True)

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

    frappe.publish_realtime("notification", after_commit=True)

    return {"status": "success"}


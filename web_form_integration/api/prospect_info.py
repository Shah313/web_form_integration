import frappe

@frappe.whitelist()
def get_party_contact_details(party_name=None, opportunity_from=None):
    if not party_name or not opportunity_from:
        frappe.throw("Missing party or source.")

    # Validate allowed doctypes
    if opportunity_from not in ["Prospect", "Customer"]:
        frappe.throw("Unsupported source: " + opportunity_from)

    # Find the Contact linked to the Party
    link = frappe.db.get_value(
        "Dynamic Link",
        {
            "link_doctype": opportunity_from,
            "link_name": party_name,
            "parenttype": "Contact"
        },
        ["parent"], as_dict=True
    )

    if not link:
        frappe.throw(f"No Contact linked to this {opportunity_from}.")

    contact = frappe.get_doc("Contact", link.parent)

    email = ""
    phone = ""

    for e in contact.email_ids:
        if e.is_primary and e.email_id:
            email = e.email_id
            break

    for p in contact.phone_nos:
        if p.is_primary_mobile_no and p.phone:
            phone = p.phone
            break

    return {
        "email": email,
        "phone": phone
    }

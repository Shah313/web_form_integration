import frappe
from frappe.utils import get_url
import random
import string


@frappe.whitelist()
def generate_buyer_form_link(opportunity_name):
    from frappe.utils import get_url
    import random, string

    doc = frappe.get_doc("Opportunity", opportunity_name)
    if not doc.custom_access_token:
        doc.custom_access_token = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        

    link = get_url(f"/buyer-form?opportunity={doc.name}&token={doc.custom_access_token}")
    return {"link": link}
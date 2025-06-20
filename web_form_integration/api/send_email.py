import frappe
from frappe.utils import get_url
import random
import string

@frappe.whitelist()
def send_buyer_form_email(opportunity_name, recipient_email):
    doc = frappe.get_doc("Opportunity", opportunity_name)

    if not doc.custom_buyer_form_token:
        doc.custom_buyer_form_token = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        doc.save()

    link = get_url(f"/buyer-form?opportunity={doc.name}&token={doc.custom_buyer_form_token}")

    subject = f"Action Required: Complete Buyer Form for {doc.name}"
    message = f"""
        <p>Dear {doc.customer_name or 'Buyer'},</p>
        <p>Please complete your form here:</p>
        <p><a href="{link}">{link}</a></p>
        <p>Best regards,<br>Root Home</p>
    """

    frappe.sendmail(recipients=recipient_email, subject=subject, message=message)
    return {"message": "Email sent successfully"}

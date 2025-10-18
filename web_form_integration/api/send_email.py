import frappe
from frappe.utils import get_url
import random
import string
from frappe.email.doctype.email_queue.email_queue import send_now

@frappe.whitelist()
def send_buyer_form_email(opportunity_name, recipient_email):
    doc = frappe.get_doc("Opportunity", opportunity_name)

    # Generate token if missing
    if not doc.custom_access_token:
        doc.custom_access_token = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        doc.save(ignore_permissions=True)

    link = get_url(f"/buyer-form?opportunity={doc.name}&token={doc.custom_access_token}")
    subject = f"Action Required: Complete Buyer Form for {doc.name}"
    message = f"""
        <p>Dear {doc.customer_name or 'Buyer'},</p>
        <p>Please complete your form here:</p>
        <p><a href="{link}">{link}</a></p>
        <p>Best regards,<br>Root Home</p>
    """

    # Step 1: Sendmail (creates Email Queue record)
    frappe.sendmail(recipients=recipient_email, subject=subject, message=message)
    frappe.db.commit()

    # Step 2: Get the latest queued email (the one we just added)
    email_queues = frappe.get_all(
        "Email Queue",
        filters={"status": "Not Sent"},
        fields=["name"],
        order_by="creation desc",
        limit=1
    )

    # Step 3: Send it instantly
    if email_queues:
        queue_name = email_queues[0].name
        try:
            send_now(queue_name)
            frappe.logger().info(f"Email {queue_name} sent instantly to {recipient_email}")
        except Exception as e:
            frappe.log_error(f"Instant email send failed for {queue_name}: {str(e)}", "Email Instant Send Error")

    return {"message": "Email sent instantly"}

# web_form_integration/api.py
import re
import frappe

@frappe.whitelist(allow_guest=True)
def get_clean_property(opportunity: str):
    """
    Return a 'clean' property string for the given Opportunity.
    - Prefer Opportunity.custom_property if already set.
    - Otherwise derive from custom_project or name, stripping the last '-NNNNN'.
    """
    if not opportunity:
        return ""

    # You may want to restrict guest access or verify a signed token (see note below).
    doc = frappe.get_doc("Opportunity", opportunity)

    val = (doc.get("custom_property") or "").strip()
    if not val:
        # fall back to custom_project or the doc.name
        source = (doc.get("custom_project") or doc.name or "").strip()
        # remove trailing "-digits" (e.g. "-00276")
        val = re.sub(r"-\d+$", "", source)

    return val
import frappe
from frappe.utils.file_manager import save_file
from frappe import _

@frappe.whitelist(allow_guest=True)
def guest_upload():
    from werkzeug.datastructures import FileStorage

    file_storage: FileStorage = frappe.request.files.get("file")
    is_private = int(frappe.form_dict.get("is_private", 0))
    doctype = frappe.form_dict.get("doctype")
    docname = frappe.form_dict.get("docname")

    if not file_storage:
        frappe.throw(_("No file attached"))

    # Use correct save_file signature
    saved_file = save_file(
        fname=file_storage.filename,
        content=file_storage.stream.read(),
        dt=doctype,
        dn=docname,
        is_private=is_private
    )

    return {
        "message": {
            "file_url": saved_file.file_url,
            "file_name": saved_file.file_name
        }
    }
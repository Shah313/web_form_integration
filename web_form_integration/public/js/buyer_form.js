 frappe.ready(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const opp = urlParams.get("opportunity");
    const token = urlParams.get("token");

    if (!opp || !token) {
        document.body.innerHTML = "<h2>Missing parameters</h2>";
        return;
    }

    frappe.call({
        method: "web_form_integration.api.token_form.validate_token",
        args: { opportunity_name: opp, access_token: token },
        callback: (r) => {
            if (r.message.status === "valid") {
                document.getElementById("form-container").style.display = "block";
            }
        },
        error: () => {
            document.body.innerHTML = "<h2>Invalid or expired token.</h2>";
        }
    });

    document.getElementById("submit-btn").onclick = async () => {
        const getVal = id => document.getElementById(id)?.value || "";
        const getCheck = id => document.getElementById(id)?.checked || false;

        
        
const uploadFile = async (id) => {
    const fileInput = document.getElementById(id);
    if (fileInput && fileInput.files.length > 0) {
        const file = fileInput.files[0];

        // ✅ Reject if file is larger than 5MB
         if (file.size > 20 * 1024 * 1024) {
            alert("File too large. Max 20MB allowed.");
            return "";
        }

   

        const formData = new FormData();
        formData.append("file", file);
        formData.append("is_private", 0);
        formData.append("doctype", "Opportunity");
        formData.append("docname", opp);

        const response = await fetch("/api/method/web_form_integration.api.secure_upload.guest_upload", {
            method: "POST",
            body: formData
        });

        
const result = await response.json();

// handle both cases
let fileInfo = result.message;
if (fileInfo && fileInfo.message) {
  fileInfo = fileInfo.message;
}

if (fileInfo && fileInfo.file_url) {
  console.log("File uploaded:", fileInfo.file_url);
  return fileInfo.file_url;
} else {
  console.error("Upload failed:", result);
  return "";
}



        
    }
    return "";
};




// Step 1: trigger all uploads in parallel
const [
    file1, file2, file3, file4, file5, file6
] = await Promise.all([
    uploadFile("custom_buyer_1_id_passport"),
    uploadFile("custom_buyer_1_proof_of_address"),
    uploadFile("custom_buyer_2_id"),
    uploadFile("custom_buyer_2_proof_of_address"),
    uploadFile("custom_proof_of_funds"),
]);

// Step 2: construct data
const data = {
    
    custom_company_name: getVal("custom_company_name"),
    custom_company_number: getVal("custom_company_number"),

    custom_buyer_1_name: getVal("custom_buyer_1_name"),
    custom_buyer_1_phone: getVal("custom_buyer_1_phone"),
    custom_buyer_1_email: getVal("custom_buyer_1_email"),

    custom_buyer_1_id_passport: file1,
    custom_buyer_1_proof_of_address: file2,

    custom_buyer_2_name: getVal("custom_buyer_2_name"),
    custom_buyer_2_phone: getVal("custom_buyer_2_phone"),
    custom_buyer_2_email: getVal("custom_buyer_2_email"),

    custom_buyer_2_id: file3,
    custom_buyer_2_proof_of_address: file4,
    custom_proof_of_funds: file5,

    custom_buying_method_cash: getCheck("custom_buying_method_cash") ? 1 : 0,
    custom_buying_method_cash_and_bridging_loan: getCheck("custom_buying_method_cash_and_bridging_loan") ? 1 : 0,

    custom_survery_quote: getCheck("custom_survery_quote") ? 1 : 0,
    custom_searches_quote__: getCheck("custom_searches_quote__") ? 1 : 0,
    custom_intro_to_root_homes_team: getCheck("custom_intro_to_root_homes_team") ? 1 : 0,
    custom_i_have_my_own_solicitor: getCheck("custom_i_have_my_own_solicitor") ? 1 : 0,

    custom_solicitor_name: getVal("custom_solicitor_name"),
    custom_solicitor_phone: getVal("custom_solicitor_phone"),
    custom_solicitor_email: getVal("custom_solicitor_email"),
    custom_solicitor_firm: getVal("custom_solicitor_firm"),
    custom_solicitor_address: getVal("custom_solicitor_address"),

    custom_different_name: getCheck("custom_different_name") ? 1 : 0,

    custom_different_order_name: getVal("custom_different_order_name"),
};


        frappe.call({
            method: "web_form_integration.api.token_form.update_opportunity_data",
            args: {
                opportunity_name: opp,
                access_token: token,
                data: data
            },
            callback: () => {
                alert("Form submitted successfully!");
                window.location.href = "/thank-you";
            }
        });
    };
});
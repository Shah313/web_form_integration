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
        const formData = new FormData();
        formData.append("file", file);

        formData.append("is_private", 0);
        formData.append("doctype", "Opportunity");
        formData.append("docname", opp);

        const response = await fetch("/api/method/upload_file", {
            method: "POST",
            body: formData
        });

        const result = await response.json();

        // This line:
        const url = result.message?.file_url || `/files/${file.name}`;
        console.log("File uploaded:", url);  // Good for debugging
        return url;
    }
    return "";
};





        const data = {
            custom_property: getVal("custom_property"),
            custom_company_name: getVal("custom_company_name"),
            custom_company_number: getVal("custom_company_number"),
            custom_buyer_1_name: getVal("custom_buyer_1_name"),  
            custom_buyer_1_phone: getVal("custom_buyer_1_phone"),   
            custom_buyer_1_email: getVal("custom_buyer_1_email"),
            custom_buyer_1_id_passport: await uploadFile("custom_buyer_1_id_passport"),
            custom_buyer_1_proof_of_address: await uploadFile("custom_buyer_1_proof_of_address"),

            custom_buyer_2_name: getVal("custom_buyer_2_name"),  
            custom_buyer_2_phone: getVal("custom_buyer_2_phone"),   
            custom_buyer_2_email: getVal("custom_buyer_2_email"),
            custom_buyer_2_id: await uploadFile("custom_buyer_2_id"),
            custom_buyer_2_proof_of_address: await uploadFile("custom_buyer_2_proof_of_address"),
            custom_buying_method_cash: getCheck("custom_buying_method_cash") ? 1 : 0,
            custom_buying_method_cash_and_bridging_loan: getCheck("custom_buying_method_cash_and_bridging_loan") ? 1 : 0,
            custom_proof_of_funds: await uploadFile("custom_proof_of_funds"),



         
            
            custom_survery_quote: getCheck("custom_survery_quote") ? 1 : 0,
            custom_searches_quote: getCheck("custom_searches_quote") ? 1 : 0,
            custom_intro_to_root_homes_team: getCheck("custom_intro_to_root_homes_team") ? 1 : 0,
            custom_i_have_my_own_solicitor: getCheck("custom_i_have_my_own_solicitor") ? 1 : 0,
            custom_different_name_for_order: getCheck("custom_different_name_for_order") ? 1 : 0,
           
            
            
            
            
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

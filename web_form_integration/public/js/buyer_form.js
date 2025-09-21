frappe.ready(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const opp = urlParams.get("opportunity");
    const token = urlParams.get("token");

    if (!opp || !token) {
        document.body.innerHTML = "<h2>Missing parameters</h2>";
        return;
    }

    const storageKey = `buyerFormDraft_${opp}_${token}`; // ✅ unique per opportunity+token
    const form = document.getElementById("buyer-form");

    // ---- Restore draft on load ----
    const draft = localStorage.getItem(storageKey);
    if (draft) {
        try {
            const data = JSON.parse(draft);
            Object.keys(data).forEach(id => {
                const el = document.getElementById(id);
                if (el) {
                    if (el.type === "checkbox" || el.type === "radio") {
                        el.checked = !!data[id];
                    } else if (el.type !== "file") {
                        el.value = data[id];
                    }
                }
            });
        } catch (e) {
            console.warn("Failed to parse saved draft:", e);
        }
    }

    // ---- Auto-save on input change ----
    form.addEventListener("input", () => {
        const saveData = {};
        Array.from(form.elements).forEach(el => {
            if (!el.id) return;
            if (el.type === "checkbox" || el.type === "radio") {
                saveData[el.id] = el.checked;
            } else if (el.type !== "file") {
                saveData[el.id] = el.value;
            }
        });
        localStorage.setItem(storageKey, JSON.stringify(saveData));
    });

    // ✅ Existing token validation (unchanged)
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

    // ✅ Existing submit handler (slightly modified to clear localStorage on success)
    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        // --- your existing helper functions unchanged ---
        const getVal = id => document.getElementById(id)?.value || "";
        const getCheck = id => document.getElementById(id)?.checked || false;

        const uploadFile = async (id) => {
            const fileInput = document.getElementById(id);
            if (fileInput && fileInput.files.length > 0) {
                const file = fileInput.files[0];
                if (file.size > 20 * 1024 * 1024) {
                    alert("File too large. Max 20MB allowed.");
                    return "";
                }
                const formData = new FormData();
                formData.append("file", file);
                formData.append("is_private", 0);
                formData.append("doctype", "Opportunity");
                formData.append("docname", opp);
                const response = await fetch(
                    "/api/method/web_form_integration.api.secure_upload.guest_upload",
                    { method: "POST", body: formData }
                );
                const result = await response.json();
                let fileInfo = result.message;
                if (fileInfo && fileInfo.message) fileInfo = fileInfo.message;
                return (fileInfo && fileInfo.file_url) ? fileInfo.file_url : "";
            }
            return "";
        };

        // --- uploads & data payload (unchanged) ---
        const [file1, file2, file3, file4, file5] = await Promise.all([
            uploadFile("custom_buyer_1_id_passport"),
            uploadFile("custom_buyer_1_proof_of_address"),
            uploadFile("custom_buyer_2_id"),
            uploadFile("custom_buyer_2_proof_of_address"),
            uploadFile("custom_proof_of_funds"),
        ]);

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
            custom_architectural_quotee: getCheck("custom_architectural_quotee") ? 1 : 0,
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
            args: { opportunity_name: opp, access_token: token, data },
            callback: () => {
                // ✅ clear saved draft on success
                localStorage.removeItem(storageKey);
                alert("Form submitted successfully!");
                window.location.href = "/thank-you";
            }
        });
    });
});

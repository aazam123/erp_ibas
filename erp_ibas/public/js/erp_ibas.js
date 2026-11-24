// ERP-IBAS Client Extensions
frappe.provide("erp_ibas");

$(document).on("app_ready", function() {
    console.log("ERP-IBAS Intelligent Business Automation System initialized.");
});

// Real-time AI Insight Button on Core ERPNext Forms
const TARGET_DOCTYPES = ["Sales Invoice", "Purchase Invoice", "Purchase Order", "Payment Entry", "Journal Entry"];

TARGET_DOCTYPES.forEach(function(doctype) {
    frappe.ui.form.on(doctype, {
        refresh: function(frm) {
            if (!frm.is_new()) {
                frm.add_custom_button(__("IBAS AI Insights"), function() {
                    frappe.call({
                        method: "erp_ibas.api.ai.analyze_document",
                        args: {
                            doctype: frm.doc.doctype,
                            docname: frm.doc.name
                        },
                        freeze: true,
                        freeze_message: __("Evaluating with ERP-IBAS AI Intelligence..."),
                        callback: function(r) {
                            if (r.message) {
                                show_ibas_ai_modal(frm, r.message);
                            }
                        }
                    });
                }, __("ERP-IBAS"));
            }
        }
    });
});

function show_ibas_ai_modal(frm, data) {
    let anomalies = data.anomalies || [];
    let fraud = data.fraud_assessment;
    let summary = data.ai_executive_summary || "No anomalies flagged. Document aligns with historical enterprise corridor.";

    let anomaly_html = "";
    if (anomalies.length > 0) {
        anomaly_html = `<div class="ibas-risk-box ibas-risk-alert">
            <h5 style="color: #c53030; font-weight: bold;">⚠️ Detected Anomalies (${anomalies.length})</h5>
            <ul style="padding-left: 20px;">
                ${anomalies.map(a => `<li><strong>${a.anomaly_type}</strong> [Severity: <span class="badge badge-${a.severity === 'Critical' ? 'danger' : 'warning'}">${a.severity}</span>, Risk: ${a.risk_score}]: ${a.explanation}<br><em>Action: ${a.suggested_action}</em></li>`).join("")}
            </ul>
        </div>`;
    } else {
        anomaly_html = `<div class="ibas-risk-box ibas-risk-clean">
            <h5 style="color: #276749; font-weight: bold;">✅ Operational Anomaly Check Passed</h5>
            <p>No abnormal variances, unusual amounts, or duplicate invoice patterns detected.</p>
        </div>`;
    }

    let fraud_html = "";
    if (fraud && fraud.overall_risk_score > 20) {
        fraud_html = `<div class="ibas-risk-box ibas-fraud-alert" style="margin-top: 15px;">
            <h5 style="color: #dd6b20; font-weight: bold;">🛡️ Fraud Risk Assessment: ${fraud.risk_level} (${fraud.overall_risk_score}/100)</h5>
            <p>${fraud.summary}</p>
        </div>`;
    }

    let dialog = new frappe.ui.Dialog({
        title: __("ERP-IBAS AI Intelligence & Risk Audit"),
        fields: [
            {
                fieldname: "insights_html",
                fieldtype: "HTML"
            }
        ],
        primary_action_label: __("Close"),
        primary_action: function() {
            dialog.hide();
        }
    });

    let content = `
        <div class="ibas-ai-dialog">
            ${anomaly_html}
            ${fraud_html}
            <div class="ibas-executive-summary" style="margin-top: 15px; padding: 12px; background: #f7fafc; border-radius: 6px; border: 1px solid #e2e8f0;">
                <h5 style="font-weight: bold; color: #2d3748;">📊 Executive AI Evaluation</h5>
                <p style="white-space: pre-wrap; font-size: 13px; line-height: 1.5; color: #4a5568;">${summary}</p>
            </div>
        </div>
    `;

    dialog.fields_dict.insights_html.$wrapper.html(content);
    dialog.show();
}

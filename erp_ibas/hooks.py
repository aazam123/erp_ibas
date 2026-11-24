app_name = "erp_ibas"
app_title = "ERP-IBAS"
app_publisher = "Aazam Morvadiya"
app_description = "Enterprise Resource Planning & Intelligent Business Automation System"
app_email = "aazammorvadiya@gmail.com"
app_license = "mit"

# JSON request bodies
use_json_request_body = True

# Includes in <head>
# ------------------
# include js, css files in header of desk.html
app_include_js = "/assets/erp_ibas/js/erp_ibas.js"
app_include_css = "/assets/erp_ibas/css/erp_ibas.css"

# Document Events Hooks
# ---------------------
doc_events = {
    "Sales Invoice": {
        "on_submit": [
            "erp_ibas.ai.anomaly_detector.IBASAnomalyDetector.scan_document",
            "erp_ibas.intercompany.intercompany_service.IBASIntercompanyService.on_submit_document"
        ]
    },
    "Sales Order": {
        "on_submit": [
            "erp_ibas.intercompany.intercompany_service.IBASIntercompanyService.on_submit_document"
        ]
    },
    "Purchase Invoice": {
        "on_submit": [
            "erp_ibas.ai.anomaly_detector.IBASAnomalyDetector.scan_document"
        ]
    },
    "Purchase Order": {
        "validate": [
            "erp_ibas.fraud.fraud_detector.IBASFraudDetector.evaluate_document"
        ]
    },
    "Payment Entry": {
        "validate": [
            "erp_ibas.fraud.fraud_detector.IBASFraudDetector.evaluate_document",
            "erp_ibas.ai.anomaly_detector.IBASAnomalyDetector.scan_document"
        ]
    },
    "Journal Entry": {
        "validate": [
            "erp_ibas.ai.anomaly_detector.IBASAnomalyDetector.scan_document"
        ]
    }
}

# Scheduled Tasks
# ---------------
scheduler_events = {
    "hourly": [
        "erp_ibas.tasks.hourly"
    ],
    "daily": [
        "erp_ibas.tasks.daily"
    ]
}

# Typing and API Export
export_python_type_annotations = True
require_type_annotated_api_methods = False

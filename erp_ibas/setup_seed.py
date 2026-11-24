# Copyright (c) 2026, Aazam Morvadiya and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now_datetime, nowdate


def setup_seed_data():
    frappe.set_user("Administrator")
    print("Setting up ERP-IBAS Enterprise Environment...")

    # 1. Setup IBAS Settings
    settings = frappe.get_doc("IBAS Settings")
    settings.enabled = 1
    settings.enable_ai = 1
    settings.enable_anomaly_detection = 1
    settings.enable_fraud_detection = 1
    settings.enable_intercompany_sync = 1
    settings.enable_auto_reconciliation = 1
    settings.enable_auto_workflows = 1
    settings.ai_provider = "Built-in Rule & Statistical Engine (Offline)"
    settings.model_name = "gemini-1.5-pro"
    settings.anomaly_sensitivity = "Medium"
    settings.high_risk_threshold = 75.0
    settings.auto_approval_limit = 10000.0
    settings.auto_reconcile_match_threshold = 90.0
    settings.save(ignore_permissions=True)
    print("IBAS Settings configured.")

    # 2. Install ERPNext baseline fixtures if not yet installed
    try:
        from erpnext.setup.setup_wizard.operations.install_fixtures import install
        install("United States")
        print("Installed ERPNext standard fixtures.")
    except Exception as e:
        print(f"Fixtures note: {str(e)}")

    # 3. Ensure Currencies exist
    for curr in ["USD", "EUR", "GBP", "SGD", "INR"]:
        if not frappe.db.exists("Currency", curr):
            c = frappe.get_doc({"doctype": "Currency", "currency_name": curr, "symbol": "$"})
            c.insert(ignore_permissions=True)

    # 4. Create Companies if not exist
    companies = [
        {"name": "IBAS Global Holdings Ltd", "abbr": "IGH", "currency": "USD", "country": "United States"},
        {"name": "IBAS Americas Inc", "abbr": "IAI", "currency": "USD", "country": "United States"},
        {"name": "IBAS Asia-Pacific Pte Ltd", "abbr": "IAP", "currency": "USD", "country": "Singapore"}
    ]

    for comp in companies:
        if not frappe.db.exists("Company", comp["name"]):
            c_doc = frappe.get_doc({
                "doctype": "Company",
                "company_name": comp["name"],
                "abbr": comp["abbr"],
                "default_currency": comp["currency"],
                "country": comp["country"]
            })
            c_doc.insert(ignore_permissions=True)
            print(f"Company created: {comp['name']}")
        else:
            print(f"Company exists: {comp['name']}")

    parent_comp = "IBAS Global Holdings Ltd"
    sub1 = "IBAS Americas Inc"
    sub2 = "IBAS Asia-Pacific Pte Ltd"

    # Set default holding company in IBAS Settings
    settings.default_holding_company = parent_comp
    settings.save(ignore_permissions=True)

    # 5. Setup Customer and Supplier representations for Intercompany
    for sub in [sub1, sub2]:
        cust_name = f"{sub} (Internal Customer)"
        if not frappe.db.exists("Customer", cust_name):
            cust = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": cust_name,
                "customer_type": "Company",
                "customer_group": "Commercial",
                "territory": "All Territories"
            })
            cust.insert(ignore_permissions=True)

        supp_name = f"{parent_comp} (Internal Supplier)"
        if not frappe.db.exists("Supplier", supp_name):
            supp = frappe.get_doc({
                "doctype": "Supplier",
                "supplier_name": supp_name,
                "supplier_type": "Company",
                "supplier_group": "Local"
            })
            supp.insert(ignore_permissions=True)

        # Intercompany Mappings
        mapping_exists = frappe.db.exists("IBAS Intercompany Mapping", {
            "parent_company": parent_comp,
            "subsidiary_company": sub
        })
        if not mapping_exists:
            map_doc = frappe.get_doc({
                "doctype": "IBAS Intercompany Mapping",
                "parent_company": parent_comp,
                "subsidiary_company": sub,
                "auto_sync": 1,
                "customer_in_parent": cust_name,
                "supplier_in_subsidiary": supp_name
            })
            map_doc.insert(ignore_permissions=True)
            print(f"Intercompany Mapping created for {parent_comp} <-> {sub}")

    # 6. Seed Operational Recommendations & Forecast
    from erp_ibas.ai.recommendation_engine import IBASRecommendationEngine
    from erp_ibas.ai.financial_forecaster import IBASFinancialForecaster

    print("Generating baseline financial forecast...")
    IBASFinancialForecaster.generate_forecast(parent_comp, horizon_months=6)

    print("Generating baseline operational recommendations...")
    IBASRecommendationEngine.generate_recommendations(parent_comp)

    # 7. Seed Sample Anomaly Log for demonstration & visibility
    sample_anomaly = frappe.db.exists("IBAS Anomaly Log", {"anomaly_type": "Velocity Anomaly"})
    if not sample_anomaly:
        a_doc = frappe.get_doc({
            "doctype": "IBAS Anomaly Log",
            "reference_doctype": "Company",
            "reference_name": parent_comp,
            "company": parent_comp,
            "anomaly_type": "Velocity Anomaly",
            "severity": "Medium",
            "risk_score": 62.0,
            "status": "Detected",
            "detection_date": now_datetime(),
            "detected_by_model": "IBAS Z-Score & Heuristic AI Engine",
            "explanation": "High transaction volume variance detected in end-of-month clearing channel.",
            "suggested_action": "Review batch transaction logs and audit clearing accounts.",
            "financial_impact": 12500.0
        })
        a_doc.insert(ignore_permissions=True)

    # 8. Seed Sample Fraud Risk Assessment
    sample_fraud = frappe.db.exists("IBAS Fraud Risk Assessment", {"reference_name": parent_comp})
    if not sample_fraud:
        f_doc = frappe.get_doc({
            "doctype": "IBAS Fraud Risk Assessment",
            "reference_doctype": "Company",
            "reference_name": parent_comp,
            "company": parent_comp,
            "party_type": "Supplier",
            "party": f"{parent_comp} (Internal Supplier)",
            "transaction_amount": 48500.0,
            "currency": "USD",
            "overall_risk_score": 28.0,
            "risk_level": "Low",
            "status": "Clear",
            "evaluated_at": now_datetime(),
            "summary": "Baseline enterprise risk verification complete. Low multi-entity clearance variance.",
            "factors": [
                {
                    "risk_factor": "Intercompany internal transaction verification",
                    "severity": "Low",
                    "score_contribution": 15.0,
                    "details": "Routine group consolidation transaction."
                }
            ]
        })
        f_doc.insert(ignore_permissions=True)

    # 9. Seed Sample Auto Reconciliation Log
    sample_recon = frappe.db.exists("IBAS Auto Reconciliation Log", {"company": parent_comp})
    if not sample_recon:
        r_doc = frappe.get_doc({
            "doctype": "IBAS Auto Reconciliation Log",
            "reconciliation_type": "Bank Statement Match",
            "company": parent_comp,
            "run_date": now_datetime(),
            "status": "Success",
            "total_records": 12,
            "matched_records": 12,
            "unmatched_records": 0,
            "match_accuracy_rate": 100.0,
            "currency": "USD",
            "reconciled_amount": 145000.0,
            "discrepancy_amount": 0.0,
            "log_details": "Initial system validation: 12 transaction records verified and reconciled."
        })
        r_doc.insert(ignore_permissions=True)

    frappe.db.commit()
    print("ERP-IBAS Seed Data initialization completed successfully!")

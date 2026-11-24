# Copyright (c) 2026, Aazam Morvadiya and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt


@frappe.whitelist()
def get_executive_metrics(company: str = None):
    """Returns top-level KPI metrics for ERP-IBAS Desk Dashboard"""
    filters = {"company": company} if company else {}

    open_anomalies = frappe.db.count("IBAS Anomaly Log", filters={**filters, "status": "Detected"})
    critical_fraud = frappe.db.count("IBAS Fraud Risk Assessment", filters={**filters, "risk_level": ["in", ["High", "Critical"]]})
    total_intercompany = frappe.db.count("IBAS Intercompany Transaction", filters={"sync_status": "Synced"})
    active_recommendations = frappe.db.count("IBAS Operational Recommendation", filters={**filters, "status": "Active"})

    # Latest forecast
    forecasts = frappe.get_all("IBAS Financial Forecast", filters=filters, order_by="creation desc", limit=1, fields=["projected_net_cash_flow", "currency"])
    net_cf = forecasts[0].projected_net_cash_flow if forecasts else 0.0
    currency = forecasts[0].currency if forecasts else (frappe.db.get_value("Company", company, "default_currency") if company else "USD")

    # Reconciliation accuracy average
    reconciliations = frappe.get_all("IBAS Auto Reconciliation Log", filters=filters, limit=10, fields=["match_accuracy_rate"])
    avg_reconcile = (
        round(sum(flt(r.match_accuracy_rate) for r in reconciliations) / len(reconciliations), 1)
        if reconciliations else 100.0
    )

    return {
        "open_anomalies": open_anomalies,
        "critical_fraud_alerts": critical_fraud,
        "synced_intercompany_transactions": total_intercompany,
        "active_recommendations": active_recommendations,
        "projected_net_cash_flow": net_cf,
        "currency": currency or "USD",
        "average_reconciliation_rate": avg_reconcile,
        "system_status": "All Systems Operational & Automated"
    }

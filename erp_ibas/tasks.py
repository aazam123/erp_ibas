# Copyright (c) 2026, Aazam Morvadiya and contributors
# For license information, please see license.txt

import frappe
from erp_ibas.ai.financial_forecaster import IBASFinancialForecaster
from erp_ibas.ai.recommendation_engine import IBASRecommendationEngine
from erp_ibas.reconciliation.auto_reconciler import IBASAutoReconciler


def daily():
    """Daily scheduled background jobs for ERP-IBAS"""
    settings = frappe.get_cached_doc("IBAS Settings")
    if not settings.enabled:
        return

    companies = frappe.get_all("Company", pluck="name")
    for comp in companies:
        try:
            # 1. Update Financial Forecast
            IBASFinancialForecaster.generate_forecast(comp, horizon_months=6)
        except Exception as e:
            frappe.log_error(f"Daily forecast error for {comp}: {str(e)}", "IBAS Daily Scheduler")

        try:
            # 2. Run Auto Bank Reconciliation
            if settings.enable_auto_reconciliation:
                IBASAutoReconciler.run_reconciliation(comp, "Bank Statement Match")
        except Exception as e:
            frappe.log_error(f"Daily reconciliation error for {comp}: {str(e)}", "IBAS Daily Scheduler")

        try:
            # 3. Generate AI Recommendations
            IBASRecommendationEngine.generate_recommendations(comp)
        except Exception as e:
            frappe.log_error(f"Daily recommendations error for {comp}: {str(e)}", "IBAS Daily Scheduler")


def hourly():
    """Hourly scheduled background jobs for ERP-IBAS"""
    settings = frappe.get_cached_doc("IBAS Settings")
    if not settings.enabled:
        return

    # Process any failed or pending intercompany mirror retries
    pending = frappe.get_all(
        "IBAS Intercompany Transaction",
        filters={"sync_status": "Pending"},
        fields=["source_doctype", "source_name"]
    )
    for p in pending:
        try:
            from erp_ibas.intercompany.intercompany_service import IBASIntercompanyService
            doc = frappe.get_doc(p.source_doctype, p.source_name)
            IBASIntercompanyService.on_submit_document(doc)
        except Exception as e:
            frappe.log_error(f"Hourly mirror retry error for {p.source_name}: {str(e)}", "IBAS Hourly Scheduler")

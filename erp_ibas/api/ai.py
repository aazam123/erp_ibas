# Copyright (c) 2026, Aazam Morvadiya and contributors
# For license information, please see license.txt

import frappe
from erp_ibas.ai.ai_engine import IBAIAIEngine
from erp_ibas.ai.anomaly_detector import IBASAnomalyDetector
from erp_ibas.ai.financial_forecaster import IBASFinancialForecaster
from erp_ibas.ai.recommendation_engine import IBASRecommendationEngine
from erp_ibas.fraud.fraud_detector import IBASFraudDetector


@frappe.whitelist()
def analyze_document(doctype: str, docname: str):
    """Deep AI analysis of any business document"""
    if not frappe.has_permission(doctype, "read", docname):
        frappe.throw("Not permitted", frappe.PermissionError)

    doc = frappe.get_doc(doctype, docname)
    
    # Run anomaly and fraud evaluation
    IBASAnomalyDetector.scan_document(doc)
    if doctype in ["Purchase Order", "Payment Entry"]:
        IBASFraudDetector.evaluate_document(doc)

    # Fetch associated logs
    anomalies = frappe.get_all(
        "IBAS Anomaly Log",
        filters={"reference_doctype": doctype, "reference_name": docname},
        fields=["name", "anomaly_type", "severity", "risk_score", "status", "explanation", "suggested_action"]
    )
    fraud = frappe.get_all(
        "IBAS Fraud Risk Assessment",
        filters={"reference_doctype": doctype, "reference_name": docname},
        fields=["name", "overall_risk_score", "risk_level", "status", "summary"]
    )

    # AI Synthesis prompt
    summary = IBAIAIEngine.call_ai(
        system_prompt="You are an enterprise CFO and risk auditor AI reviewing an ERP transaction.",
        user_prompt=f"Review transaction {doctype} {docname} with data {doc.as_dict()}. Detected anomalies: {anomalies}. Fraud assessments: {fraud}. Provide an executive evaluation.",
        json_response=False
    )

    return {
        "doctype": doctype,
        "docname": docname,
        "anomalies": anomalies,
        "fraud_assessment": fraud[0] if fraud else None,
        "ai_executive_summary": summary
    }


@frappe.whitelist()
def ask_assistant(prompt: str, company: str = None):
    """Natural Language Business Intelligence Assistant"""
    if not prompt:
        return {"error": "Prompt required"}

    # Fetch enterprise context
    companies = [company] if company else frappe.get_all("Company", pluck="name")
    active_anomalies = frappe.db.count("IBAS Anomaly Log", filters={"status": "Detected"})
    high_fraud = frappe.db.count("IBAS Fraud Risk Assessment", filters={"risk_level": ["in", ["High", "Critical"]]})

    system_context = f"""
    You are ERP-IBAS (Enterprise Resource Planning & Intelligent Business Automation System) AI Assistant.
    You assist C-level executives, operations managers, and accountants with operational insights, financial forecasting, anomaly resolution, and inter-company strategy.
    Current Enterprise State:
    - Registered Companies: {companies}
    - Open Anomalies: {active_anomalies}
    - Critical Fraud Alerts: {high_fraud}
    """

    response = IBAIAIEngine.call_ai(
        system_prompt=system_context,
        user_prompt=prompt,
        json_response=False
    )

    return {
        "prompt": prompt,
        "answer": response
    }


@frappe.whitelist()
def get_cash_flow_forecast(company: str = None, horizon: int = 6):
    """Generates and returns predictive cash flow forecast"""
    forecast = IBASFinancialForecaster.generate_forecast(company, int(horizon))
    return forecast.as_dict() if forecast else {}


@frappe.whitelist()
def generate_recommendations(company: str = None):
    """Generates real-time AI operational recommendations"""
    return IBASRecommendationEngine.generate_recommendations(company)

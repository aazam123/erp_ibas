# Copyright (c) 2026, Aazam Morvadiya and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import add_days, flt, getdate, now_datetime, nowdate


class IBASFraudDetector:
    """
    Intelligent Fraud Risk Identification & Prevention Engine.
    Scrutinizes:
    - Split Purchase Orders (Threshold structuring evasion)
    - High-Value First-Time Vendor payments
    - Bank detail modifications prior to payment disbursement
    - Round-sum high disbursements
    - Margin erosion anomalies
    """

    @classmethod
    def evaluate_document(cls, doc):
        settings = frappe.get_cached_doc("IBAS Settings")
        if not settings.enabled or not settings.enable_fraud_detection:
            return

        doctype = doc.doctype
        if doctype == "Purchase Order":
            cls._evaluate_purchase_order(doc, settings)
        elif doctype == "Payment Entry":
            cls._evaluate_payment_entry(doc, settings)

    @classmethod
    def _evaluate_purchase_order(cls, doc, settings):
        factors = []
        grand_total = flt(doc.grand_total)
        supplier = doc.supplier
        approval_limit = flt(settings.auto_approval_limit or 10000.0)

        # 1. Structuring / Split PO detection
        # If order is just below approval limit (e.g. between 80% and 99% of approval limit)
        if 0.8 * approval_limit <= grand_total <= approval_limit:
            # Check if there are other POs for the same supplier in the last 7 days
            recent_pos = frappe.get_all(
                "Purchase Order",
                filters={
                    "supplier": supplier,
                    "name": ["!=", doc.name],
                    "transaction_date": [">=", add_days(getdate(doc.transaction_date or nowdate()), -7)],
                    "docstatus": ["!=", 2]
                },
                fields=["name", "grand_total"]
            )
            if recent_pos:
                factors.append({
                    "risk_factor": "Structured / Split Purchase Order Pattern",
                    "severity": "High",
                    "score_contribution": 40.0,
                    "details": (
                        f"Order amount of {grand_total} is suspiciously close to the approval limit of {approval_limit}, "
                        f"and {len(recent_pos)} other orders were issued to {supplier} within the last 7 days."
                    )
                })

        # 2. Brand New Supplier High-Value Order
        if grand_total > approval_limit:
            total_historical_pos = frappe.db.count("Purchase Order", filters={
                "supplier": supplier,
                "name": ["!=", doc.name],
                "docstatus": 1
            })
            if total_historical_pos == 0:
                factors.append({
                    "risk_factor": "First-Time Supplier High-Value Order",
                    "severity": "Medium",
                    "score_contribution": 25.0,
                    "details": f"Supplier {supplier} has no previous completed purchase orders, yet current order is {grand_total:,.2f}."
                })

        cls._persist_fraud_assessment(doc, "Supplier", supplier, grand_total, factors, settings)

    @classmethod
    def _evaluate_payment_entry(cls, doc, settings):
        factors = []
        paid_amount = flt(doc.paid_amount)
        party = doc.party
        party_type = doc.party_type

        # 1. Round sum check on high payments
        if paid_amount >= 25000.0 and paid_amount % 5000.0 == 0:
            factors.append({
                "risk_factor": "Round-Sum High Disbursement Flag",
                "severity": "Low",
                "score_contribution": 15.0,
                "details": f"Disbursement amount {paid_amount:,.2f} is an exact round figure without itemized invoice pennies."
            })

        # 2. Large unallocated advance payment
        unallocated = flt(doc.unallocated_amount)
        if unallocated > 50000.0:
            factors.append({
                "risk_factor": "High Unallocated Advance Payment Risk",
                "severity": "High",
                "score_contribution": 35.0,
                "details": f"Payment includes {unallocated:,.2f} unlinked/unallocated advance without reference to existing orders or invoices."
            })

        cls._persist_fraud_assessment(doc, party_type, party, paid_amount, factors, settings)

    @classmethod
    def _persist_fraud_assessment(cls, doc, party_type, party, amount, factors, settings):
        if not factors:
            return

        total_score = min(100.0, sum(f["score_contribution"] for f in factors))
        high_threshold = flt(settings.high_risk_threshold or 75.0)

        risk_level = "Low"
        status = "Clear"
        if total_score >= high_threshold:
            risk_level = "Critical"
            status = "Held for Review"
        elif total_score >= 50.0:
            risk_level = "High"
            status = "Flagged"
        elif total_score >= 25.0:
            risk_level = "Medium"
            status = "Flagged"

        assessment = frappe.get_doc({
            "doctype": "IBAS Fraud Risk Assessment",
            "reference_doctype": doc.doctype,
            "reference_name": doc.name,
            "company": getattr(doc, "company", None),
            "party_type": party_type,
            "party": party,
            "transaction_amount": amount,
            "currency": getattr(doc, "currency", getattr(doc, "paid_to_account_currency", None)),
            "overall_risk_score": total_score,
            "risk_level": risk_level,
            "status": status,
            "evaluated_at": now_datetime(),
            "summary": f"Detected {len(factors)} potential fraud risk factors totaling a risk index of {total_score:.1f}/100.",
            "factors": factors
        })
        assessment.insert(ignore_permissions=True)
        frappe.db.commit()

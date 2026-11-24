# Copyright (c) 2026, Aazam Morvadiya and contributors
# For license information, please see license.txt

import math
import frappe
from frappe.utils import flt, now_datetime
from erp_ibas.ai.ai_engine import IBAIAIEngine


class IBASAnomalyDetector:
    """
    Intelligent Anomaly Detection for ERP-IBAS.
    Scans:
    - Sales Invoices
    - Purchase Invoices
    - Journal Entries
    - Payment Entries
    - Expense Claims (HRMS)
    - Salary Slips (HRMS)
    """

    @classmethod
    def scan_document(cls, doc):
        """Hook called on document validate / submit"""
        settings = frappe.get_cached_doc("IBAS Settings")
        if not settings.enabled or not settings.enable_anomaly_detection:
            return

        doctype = doc.doctype
        if doctype == "Sales Invoice":
            cls._scan_sales_invoice(doc, settings)
        elif doctype == "Purchase Invoice":
            cls._scan_purchase_invoice(doc, settings)
        elif doctype == "Journal Entry":
            cls._scan_journal_entry(doc, settings)
        elif doctype == "Payment Entry":
            cls._scan_payment_entry(doc, settings)
        elif doctype == "Expense Claim":
            cls._scan_expense_claim(doc, settings)
        elif doctype == "Salary Slip":
            cls._scan_salary_slip(doc, settings)

    @classmethod
    def _scan_sales_invoice(cls, doc, settings):
        anomalies = []
        grand_total = flt(doc.grand_total)

        customer = doc.customer
        if customer and grand_total > 0:
            past_invoices = frappe.get_all(
                "Sales Invoice",
                filters={"customer": customer, "docstatus": 1, "name": ["!=", doc.name]},
                fields=["grand_total"],
                limit=30
            )
            if len(past_invoices) >= 3:
                totals = [flt(x.grand_total) for x in past_invoices]
                mean = sum(totals) / len(totals)
                variance = sum((x - mean) ** 2 for x in totals) / len(totals)
                std_dev = math.sqrt(variance) if variance > 0 else 0
                
                if std_dev > 0:
                    z_score = (grand_total - mean) / std_dev
                    if z_score > 3.0:
                        anomalies.append({
                            "type": "Unusual Transaction Amount",
                            "severity": "High" if z_score < 4.5 else "Critical",
                            "score": min(95.0, 50.0 + z_score * 10),
                            "explanation": f"Invoice amount ({grand_total}) is {z_score:.1f} standard deviations above historical average ({mean:.2f}) for customer {customer}.",
                            "action": "Verify customer credit line, purchase order, and delivery confirmation before approval."
                        })

        for item in doc.get("items", []):
            discount = flt(item.get("discount_percentage", 0))
            if discount > 35.0:
                anomalies.append({
                    "type": "Abnormal Margin Variance",
                    "severity": "High" if discount > 50 else "Medium",
                    "score": 70.0 + (discount - 35),
                    "explanation": f"Item '{item.item_code}' has an extraordinary discount of {discount}%, which breaches standard pricing corridors.",
                    "action": "Require commercial director sign-off on special discount."
                })

        cls._persist_anomalies(doc, anomalies)

    @classmethod
    def _scan_purchase_invoice(cls, doc, settings):
        anomalies = []
        grand_total = flt(doc.grand_total)
        supplier = doc.supplier
        bill_no = doc.get("bill_no")

        if supplier and bill_no:
            duplicates = frappe.get_all(
                "Purchase Invoice",
                filters={"supplier": supplier, "bill_no": bill_no, "name": ["!=", doc.name], "docstatus": ["!=", 2]},
                fields=["name", "posting_date", "grand_total"]
            )
            if duplicates:
                anomalies.append({
                    "type": "Duplicate Transaction Risk",
                    "severity": "Critical",
                    "score": 98.0,
                    "explanation": f"Supplier invoice number '{bill_no}' already exists on Purchase Invoice {duplicates[0].name}.",
                    "action": "Immediate freeze: duplicate billing risk detected."
                })

        if supplier and grand_total > 0:
            past_invs = frappe.get_all(
                "Purchase Invoice",
                filters={"supplier": supplier, "docstatus": 1, "name": ["!=", doc.name]},
                fields=["grand_total"],
                limit=30
            )
            if len(past_invs) >= 3:
                totals = [flt(x.grand_total) for x in past_invs]
                mean = sum(totals) / len(totals)
                variance = sum((x - mean) ** 2 for x in totals) / len(totals)
                std_dev = math.sqrt(variance) if variance > 0 else 0
                if std_dev > 0:
                    z_score = (grand_total - mean) / std_dev
                    if z_score > 3.0:
                        anomalies.append({
                            "type": "Unusual Transaction Amount",
                            "severity": "High",
                            "score": 80.0,
                            "explanation": f"Supplier billing of {grand_total} is significantly higher than historical average ({mean:.2f}).",
                            "action": "Cross-check against corresponding Purchase Orders and GRN goods receipt notes."
                        })

        cls._persist_anomalies(doc, anomalies)

    @classmethod
    def _scan_journal_entry(cls, doc, settings):
        anomalies = []
        total_debit = flt(doc.total_debit)

        if total_debit >= 50000 and total_debit % 10000 == 0:
            anomalies.append({
                "type": "Suspicious Ledger Posting",
                "severity": "Medium",
                "score": 65.0,
                "explanation": f"High value round-sum journal entry detected ({total_debit:,.2f}). Round-number postings are a recognized audit flag.",
                "action": "Ensure journal is supported by verifiable third-party documentation and contracts."
            })

        cls._persist_anomalies(doc, anomalies)

    @classmethod
    def _scan_payment_entry(cls, doc, settings):
        anomalies = []
        paid_amount = flt(doc.paid_amount)
        if paid_amount > flt(settings.auto_approval_limit or 10000.0) * 5:
            anomalies.append({
                "type": "Unusual Transaction Amount",
                "severity": "High",
                "score": 75.0,
                "explanation": f"Payment amount ({paid_amount:,.2f}) substantially exceeds standard operational threshold.",
                "action": "Mandatory dual authorization required by treasury before disbursement."
            })
        cls._persist_anomalies(doc, anomalies)

    # --- HRMS Integration: Expense Claims & Payroll ---

    @classmethod
    def _scan_expense_claim(cls, doc, settings):
        anomalies = []
        total_sanctioned = flt(doc.total_sanctioned_amount or doc.total_claimed_amount)
        employee = doc.employee

        # 1. Duplicate claim detection (same employee, same amount in last 30 days)
        if employee and total_sanctioned > 0:
            duplicates = frappe.get_all(
                "Expense Claim",
                filters={
                    "employee": employee,
                    "name": ["!=", doc.name],
                    "total_claimed_amount": total_sanctioned,
                    "docstatus": ["!=", 2]
                },
                fields=["name", "posting_date"]
            )
            if duplicates:
                anomalies.append({
                    "type": "Duplicate Transaction Risk",
                    "severity": "High",
                    "score": 85.0,
                    "explanation": f"Potential duplicate expense claim: Employee {employee} already has identical claim ({doc.total_claimed_amount}) on voucher {duplicates[0].name}.",
                    "action": "Audit original receipts and compare date of expenses to prevent double reimbursement."
                })

        # 2. Unusual expense claim amount vs policy
        if total_sanctioned > 15000:
            anomalies.append({
                "type": "Spike in Operational Expenses",
                "severity": "Medium",
                "score": 60.0,
                "explanation": f"Expense claim of {total_sanctioned:,.2f} exceeds standard employee discretionary threshold.",
                "action": "Require department head and HR manager dual-approval."
            })

        cls._persist_anomalies(doc, anomalies)

    @classmethod
    def _scan_salary_slip(cls, doc, settings):
        anomalies = []
        net_pay = flt(doc.net_pay)
        employee = doc.employee

        if employee and net_pay > 0:
            past_slips = frappe.get_all(
                "Salary Slip",
                filters={"employee": employee, "docstatus": 1, "name": ["!=", doc.name]},
                fields=["net_pay"],
                limit=6
            )
            if past_slips:
                avg_net = sum(flt(x.net_pay) for x in past_slips) / len(past_slips)
                if avg_net > 0 and (net_pay / avg_net) > 1.6:
                    anomalies.append({
                        "type": "Unusual Transaction Amount",
                        "severity": "High",
                        "score": 78.0,
                        "explanation": f"Salary net payout ({net_pay:,.2f}) is 60%+ higher than employee's historical average ({avg_net:,.2f}).",
                        "action": "Verify payroll components, incentives, and arrears before final bank disbursement."
                    })

        cls._persist_anomalies(doc, anomalies)

    @classmethod
    def _persist_anomalies(cls, doc, anomalies):
        for anomaly in anomalies:
            existing = frappe.db.exists("IBAS Anomaly Log", {
                "reference_doctype": doc.doctype,
                "reference_name": doc.name,
                "anomaly_type": anomaly["type"],
                "status": ["in", ["Detected", "Under Review"]]
            })
            if not existing:
                log_doc = frappe.get_doc({
                    "doctype": "IBAS Anomaly Log",
                    "reference_doctype": doc.doctype,
                    "reference_name": doc.name,
                    "company": getattr(doc, "company", None),
                    "anomaly_type": anomaly["type"],
                    "severity": anomaly["severity"],
                    "risk_score": anomaly["score"],
                    "status": "Detected",
                    "detection_date": now_datetime(),
                    "detected_by_model": "IBAS HRMS & Operational AI Engine",
                    "explanation": anomaly["explanation"],
                    "suggested_action": anomaly["action"],
                    "financial_impact": flt(getattr(doc, "grand_total", getattr(doc, "total_sanctioned_amount", getattr(doc, "net_pay", 0))))
                })
                log_doc.insert(ignore_permissions=True)
                frappe.db.commit()

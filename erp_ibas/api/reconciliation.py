# Copyright (c) 2026, Aazam Morvadiya and contributors
# For license information, please see license.txt

import frappe
from erp_ibas.reconciliation.auto_reconciler import IBASAutoReconciler


@frappe.whitelist()
def run_reconciliation(company: str = None, reconciliation_type: str = "Bank Statement Match"):
    """Triggers automated bank or intercompany reconciliation"""
    log = IBASAutoReconciler.run_reconciliation(company, reconciliation_type)
    return log.as_dict() if log else {"status": "no_data"}

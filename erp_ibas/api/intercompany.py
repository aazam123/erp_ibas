# Copyright (c) 2026, Aazam Morvadiya and contributors
# For license information, please see license.txt

import frappe
from erp_ibas.intercompany.intercompany_service import IBASIntercompanyService
from erp_ibas.intercompany.consolidated_financials import IBASConsolidatedFinancials


@frappe.whitelist()
def sync_intercompany_transaction(source_doctype: str, source_name: str):
    """Explicitly triggers mirror creation for an intercompany document"""
    doc = frappe.get_doc(source_doctype, source_name)
    IBASIntercompanyService.on_submit_document(doc)
    return {"status": "success", "message": f"Processed mirror synchronization for {source_doctype} {source_name}"}


@frappe.whitelist()
def get_consolidated_financials(parent_company: str = None):
    """Returns multi-company consolidated financials with intercompany elimination"""
    return IBASConsolidatedFinancials.get_consolidated_summary(parent_company)

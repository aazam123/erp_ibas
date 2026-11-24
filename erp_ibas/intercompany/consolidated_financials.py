# Copyright (c) 2026, Aazam Morvadiya and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt


class IBASConsolidatedFinancials:
    """
    Consolidated Multi-Company Financial Reporting & Elimination Engine.
    Aggregates financials across parent and subsidiaries while automatically
    eliminating inter-company balances and internal transaction turnover.
    """

    @classmethod
    def get_consolidated_summary(cls, parent_company: str = None):
        if not parent_company:
            companies = frappe.get_all("Company", pluck="name")
            if not companies:
                return {}
            parent_company = companies[0]

        # Get all related companies via Intercompany Mappings
        related = frappe.get_all(
            "IBAS Intercompany Mapping",
            filters={"parent_company": parent_company},
            fields=["subsidiary_company", "internal_receivable_account", "internal_payable_account", "elimination_account"]
        )
        all_companies = [parent_company] + [r.subsidiary_company for r in related if r.subsidiary_company]

        # Calculate Combined Invoiced Turnover
        combined_revenue = 0.0
        combined_purchases = 0.0
        company_breakdown = []

        for comp in all_companies:
            currency = frappe.db.get_value("Company", comp, "default_currency") or "USD"
            rev = flt(frappe.db.sql("""
                SELECT COALESCE(SUM(base_grand_total), 0)
                FROM `tabSales Invoice`
                WHERE company = %s AND docstatus = 1
            """, (comp,))[0][0])

            exp = flt(frappe.db.sql("""
                SELECT COALESCE(SUM(base_grand_total), 0)
                FROM `tabPurchase Invoice`
                WHERE company = %s AND docstatus = 1
            """, (comp,))[0][0])

            combined_revenue += rev
            combined_purchases += exp
            company_breakdown.append({
                "company": comp,
                "currency": currency,
                "revenue": rev,
                "purchases": exp,
                "operating_income": rev - exp
            })

        # Calculate Intercompany Elimination
        # All intercompany transactions between these companies
        intercompany_turnover = flt(frappe.db.sql("""
            SELECT COALESCE(SUM(transaction_amount), 0)
            FROM `tabIBAS Intercompany Transaction`
            WHERE source_company IN %s AND target_company IN %s AND sync_status = 'Synced'
        """, (tuple(all_companies), tuple(all_companies)))[0][0])

        eliminated_revenue = combined_revenue - intercompany_turnover
        eliminated_purchases = combined_purchases - intercompany_turnover
        consolidated_ebitda = eliminated_revenue - eliminated_purchases

        return {
            "parent_company": parent_company,
            "participating_companies": all_companies,
            "currency": frappe.db.get_value("Company", parent_company, "default_currency") or "USD",
            "combined_gross_revenue": combined_revenue,
            "intercompany_elimination": intercompany_turnover,
            "consolidated_net_revenue": eliminated_revenue,
            "consolidated_expenses": eliminated_purchases,
            "consolidated_net_operating_profit": consolidated_ebitda,
            "profit_margin_pct": round((consolidated_ebitda / eliminated_revenue * 100), 2) if eliminated_revenue > 0 else 0,
            "company_breakdown": company_breakdown
        }

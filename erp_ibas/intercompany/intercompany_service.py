# Copyright (c) 2026, Aazam Morvadiya and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt, now_datetime


class IBASIntercompanyService:
    """
    Automated Multi-Entity & Inter-Company Transaction Mirroring.
    When a transaction occurs between group entities:
    - Sales Order in Co A  -> Creates Purchase Order in Co B
    - Sales Invoice in Co A -> Creates Purchase Invoice in Co B
    - Delivery Note in Co A -> Creates Purchase Receipt in Co B
    """

    @classmethod
    def on_submit_document(cls, doc):
        """Called via doc_events hook on submit"""
        settings = frappe.get_cached_doc("IBAS Settings")
        if not settings.enabled or not settings.enable_intercompany_sync:
            return

        doctype = doc.doctype
        if doctype == "Sales Order":
            cls._mirror_sales_order(doc, settings)
        elif doctype == "Sales Invoice":
            cls._mirror_sales_invoice(doc, settings)

    @classmethod
    def _find_mapping_for_customer(cls, company: str, customer: str):
        mappings = frappe.get_all(
            "IBAS Intercompany Mapping",
            filters={
                "parent_company": company,
                "customer_in_parent": customer,
                "auto_sync": 1
            },
            fields=["*"]
        )
        return mappings[0] if mappings else None

    @classmethod
    def _mirror_sales_order(cls, doc, settings):
        mapping = cls._find_mapping_for_customer(doc.company, doc.customer)
        if not mapping:
            return

        target_company = mapping.subsidiary_company
        supplier = mapping.supplier_in_subsidiary

        # Prevent circular creation
        existing_log = frappe.db.exists("IBAS Intercompany Transaction", {
            "source_doctype": doc.doctype,
            "source_name": doc.name,
            "sync_status": "Synced"
        })
        if existing_log:
            return

        try:
            po = frappe.new_doc("Purchase Order")
            po.company = target_company
            po.supplier = supplier
            po.schedule_date = doc.delivery_date or doc.transaction_date
            po.currency = doc.currency

            for item in doc.items:
                po.append("items", {
                    "item_code": item.item_code,
                    "item_name": item.item_name,
                    "qty": item.qty,
                    "rate": item.rate,
                    "uom": item.uom,
                    "schedule_date": item.delivery_date or po.schedule_date
                })

            po.flags.ignore_permissions = True
            po.insert()
            if settings.auto_submit_mirrored_docs:
                po.submit()

            log = frappe.get_doc({
                "doctype": "IBAS Intercompany Transaction",
                "transaction_type": "Sales Order -> Purchase Order",
                "source_company": doc.company,
                "source_doctype": doc.doctype,
                "source_name": doc.name,
                "target_company": target_company,
                "target_doctype": "Purchase Order",
                "target_name": po.name,
                "transaction_amount": doc.grand_total,
                "currency": doc.currency,
                "sync_status": "Synced",
                "synced_at": now_datetime()
            })
            log.insert(ignore_permissions=True)
            frappe.db.commit()

        except Exception as e:
            frappe.log_error(f"Intercompany SO->PO Mirror Error: {str(e)}", "IBAS Intercompany")
            cls._log_failure("Sales Order -> Purchase Order", doc, target_company, str(e))

    @classmethod
    def _mirror_sales_invoice(cls, doc, settings):
        mapping = cls._find_mapping_for_customer(doc.company, doc.customer)
        if not mapping:
            return

        target_company = mapping.subsidiary_company
        supplier = mapping.supplier_in_subsidiary

        existing_log = frappe.db.exists("IBAS Intercompany Transaction", {
            "source_doctype": doc.doctype,
            "source_name": doc.name,
            "sync_status": "Synced"
        })
        if existing_log:
            return

        try:
            pi = frappe.new_doc("Purchase Invoice")
            pi.company = target_company
            pi.supplier = supplier
            pi.bill_no = doc.name
            pi.bill_date = doc.posting_date
            pi.posting_date = doc.posting_date
            pi.currency = doc.currency

            for item in doc.items:
                pi.append("items", {
                    "item_code": item.item_code,
                    "item_name": item.item_name,
                    "qty": item.qty,
                    "rate": item.rate,
                    "uom": item.uom,
                    "expense_account": mapping.internal_payable_account
                })

            pi.flags.ignore_permissions = True
            pi.insert()
            if settings.auto_submit_mirrored_docs:
                pi.submit()

            log = frappe.get_doc({
                "doctype": "IBAS Intercompany Transaction",
                "transaction_type": "Sales Invoice -> Purchase Invoice",
                "source_company": doc.company,
                "source_doctype": doc.doctype,
                "source_name": doc.name,
                "target_company": target_company,
                "target_doctype": "Purchase Invoice",
                "target_name": pi.name,
                "transaction_amount": doc.grand_total,
                "currency": doc.currency,
                "sync_status": "Synced",
                "synced_at": now_datetime()
            })
            log.insert(ignore_permissions=True)
            frappe.db.commit()

        except Exception as e:
            frappe.log_error(f"Intercompany SI->PI Mirror Error: {str(e)}", "IBAS Intercompany")
            cls._log_failure("Sales Invoice -> Purchase Invoice", doc, target_company, str(e))

    @classmethod
    def _log_failure(cls, tx_type, doc, target_company, err_msg):
        log = frappe.get_doc({
            "doctype": "IBAS Intercompany Transaction",
            "transaction_type": tx_type,
            "source_company": doc.company,
            "source_doctype": doc.doctype,
            "source_name": doc.name,
            "target_company": target_company,
            "transaction_amount": getattr(doc, "grand_total", 0),
            "currency": getattr(doc, "currency", None),
            "sync_status": "Failed",
            "error_message": err_msg
        })
        log.insert(ignore_permissions=True)
        frappe.db.commit()

from netforce.model import Model,fields,get_model
from netforce import access
from datetime import *
from decimal import *

class Invoice(Model):
    _inherit="account.invoice"

    def kff_copy_to_cust_invoice(self,ids,context={}):
        obj = self.browse(ids)[0]
        res=get_model("contact").search([["code","=","TG"]])
        if not res:
            raise Exception("Contact code not found: TG")
        tg_contact_id=res[0]
        inv_vals = {
            "type": "out",
            "inv_type": obj.inv_type,
            "ref": obj.ref,
            "contact_id": tg_contact_id,
            "currency_id": obj.currency_id.id,
            "tax_type": obj.tax_type,
            "memo": obj.memo,
            "lines": [],
            "company_id": obj.company_id.id,
        }
        for line in obj.lines:
            prod=line.product_id
            line_vals = {
                "product_id": line.product_id.id,
                "description": line.description,
                "qty": line.qty,
                "uom_id": line.uom_id.id,
                "unit_price": line.unit_price,
                "tax_id": prod.sale_tax_id.id if prod else None,
                "account_id": prod.sale_account_id.id if prod else None,
                "amount": line.amount,
                "related_id": "%s,%s"%(line.related_id._model,line.related_id.id) if line.related_id else None,
            }
            inv_vals["lines"].append(("create", line_vals))
        new_id = self.create(inv_vals, context={"type": "out", "inv_type": obj.inv_type})
        return {
            "invoice_id": new_id,
        }

    def kff_copy_to_cust_supp_invoice(self,ids,context={}):
        obj = self.browse(ids)[0]
        res=get_model("contact").search([["code","=","KFF"]])
        if not res:
            raise Exception("Contact code not found: KFF")
        kff_contact_id=res[0]
        res=get_model("company").search([["code","=","TG"]])
        if not res:
            raise Exception("Company code not found: TG")
        tg_company_id=res[0]
        inv_vals = {
            "type": "in",
            "inv_type": obj.inv_type,
            "ref": obj.ref,
            "contact_id": kff_contact_id,
            "currency_id": obj.currency_id.id,
            "tax_type": obj.tax_type,
            "memo": obj.memo,
            "lines": [],
            "company_id": tg_company_id,
        }
        for line in obj.lines:
            prod=line.product_id
            line_vals = {
                "product_id": line.product_id.id,
                "description": line.description,
                "qty": line.qty,
                "uom_id": line.uom_id.id,
                "unit_price": line.unit_price,
                "amount": line.amount,
                "related_id": "%s,%s"%(line.related_id._model,line.related_id.id) if line.related_id else None,
            }
            inv_vals["lines"].append(("create", line_vals))
        access.set_active_company(tg_company_id)
        for _,line_vals in inv_vals["lines"]:
            prod=get_model("product").browse(line_vals["product_id"])
            line_vals.update({
                "tax_id": prod.purchase_tax_id.id if prod else None,
                "account_id": prod.purchase_account_id.id if prod else None,
            })
        new_id = self.create(inv_vals, context={"type": "in", "inv_type": obj.inv_type})
        return {
            "invoice_id": new_id,
        }

Invoice.register()

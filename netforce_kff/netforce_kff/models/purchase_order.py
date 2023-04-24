from netforce.model import Model,fields,get_model
from netforce import access
from datetime import *
from decimal import *

class Order(Model):
    _inherit="purchase.order"

    def send_tg(self, ids, context={}):
        id = ids[0]
        obj = self.browse(id)
        res=get_model("contact").search([["code","=","KFF"]])
        if not res:
            raise Exception("Contact code not found: KFF")
        contact_id=res[0]
        contact=get_model("contact").browse(contact_id)
        res=get_model("company").search([["code","=","TG"]])
        if not res:
            raise Exception("Company code not found: TG")
        company_id=res[0]
        inv_vals = {
            "company_id": company_id,
            "type": "in",
            "inv_type": "invoice",
            "ref": "TG RM %s"%obj.number,
            "related_id": "purchase.order,%s" % obj.id,
            "contact_id": contact_id,
            "currency_id": obj.currency_id.id,
            "lines": [],
            "tax_type": obj.tax_type,
        }
        if contact.purchase_journal_id:
            inv_vals["journal_id"] = contact.purchase_journal_id.id
            if contact.purchase_journal_id.sequence_id:
                inv_vals["sequence_id"] = contact.purchase_journal_id.sequence_id.id
        total_qty=0
        for line in obj.lines:
            prod = line.product_id
            inv_qty=line.qty_received
            total_qty+=inv_qty
            purch_acc_id=None
            if prod:
                purch_acc_id=prod.purchase_account_id.id
                if not purch_acc_id and prod.parent_id:
                    purch_acc_id=prod.parent_id.purchase_account_id.id
                if not purch_acc_id and prod.categ_id and prod.categ_id.purchase_account_id:
                    purch_acc_id=prod.categ_id.purchase_account_id.id
            line_vals = {
                "product_id": prod.id,
                "description": line.description,
                "qty": inv_qty,
                "uom_id": line.uom_id.id,
                "unit_price": line.unit_price,
                "account_id": purch_acc_id,
                "tax_id": line.tax_id.id,
                "amount": inv_qty*line.unit_price,
                "related_id": "purchase.order,%s"%obj.id,
            }
            inv_vals["lines"].append(("create", line_vals))
        if total_qty<=0:
            raise Exception("Nothing received yet: %s"%total_qty)
        inv_id = get_model("account.invoice").create(inv_vals, {"type": "in", "inv_type": "invoice"})
        inv = get_model("account.invoice").browse(inv_id)
        return {
            "next": {
                "name": "view_invoice",
                "active_id": inv_id,
            },
            "flash": "Invoice %s created from purchase order %s" % (inv.number, obj.number),
        }

    def done(self,ids,context={}):
        super().done(ids,context=context)
        obj=self.browse(ids[0])
        if obj.company_id.code=="KFF": # XXX
            tg_inv=False
            for inv in obj.invoices:
                if inv.ref.find("TG RM")!=-1:
                    tg_inv=True
            if not tg_inv:
                raise Exception("Missing TG invoice")

    def kff_copy_to_supp_invoice(self,ids,context={}):
        obj = self.browse(ids[0])
        inv_vals = {
            "type": "in",
            "inv_type": "invoice",
            "ref": "PO FRUIT: "+obj.number,
            "contact_id": obj.contact_id.id,
            "currency_id": obj.currency_id.id,
            "related_id": "purchase.order,%s"%obj.id,
            "company_id": obj.company_id.id,
            "lines": [],
            "procurement_employee_id": obj.procurement_employee_id.id,
        }
        if not obj.gradings:
            raise Exception("Missing grading for purchase order %s"%obj.number)
        prod_qtys={}
        for grad in obj.gradings:
            for line in grad.lines:
                prod=line.product_id
                price=line.unit_price or prod.purchase_price or 0
                k=(prod.id,price)
                prod_qtys.setdefault(k,0)
                prod_qtys[k]+=line.qty or 0
        print("prod_qtys")
        for (prod_id,price),qty in prod_qtys.items():
            prod=get_model("product").browse(prod_id)
            line_vals = {
                "product_id": prod.id,
                "description": prod.description or "/",
                "qty": qty,
                "uom_id": prod.uom_id.id,
                "unit_price": price or 0, # XXX: check this
                "tax_id": prod.purchase_tax_id.id,
                "account_id": prod.purchase_account_id.id,
                "related_id": "purchase.order,%s"%obj.id,
            }
            line_vals["amount"]=line_vals["qty"]*line_vals["unit_price"]
            inv_vals["lines"].append(("create", line_vals))
        inv_id = get_model("account.invoice").create(inv_vals, context={"type":"in","inv_type":"invoice"})
        return {
            "next": {
                "name": "view_invoice",
                "active_id": inv_id,
            },
            "flash": "Supplier invoice copied from goods receipt",
            "invoice_id": inv_id,
        }

Order.register()

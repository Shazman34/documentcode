from netforce.model import Model,fields,get_model
import time

class PaymentPlan(Model):
    _inherit="payment.plan"

    def create_invoice(self,ids,context={}):
        for obj in self.browse(ids):
            if obj.invoice_id:
                raise Exception("Invoice already created")
            job=obj.related_id
            inv_vals={
                "contact_id": job.contact_id.id,
                "type": "out",
                "inv_type": "invoice",
                "related_id": "jc.job,%s"%job.id,
                "memo": job.name,
                "lines": [],
            }
            prod=job.product_id
            if not prod:
                raise Exception("Missing product in job")
            line_vals={
                "product_id": prod.id,
                "description": job.name,
                "qty": 1,
                "uom_id": prod.uom_id.id,
                "unit_price": obj.amount,
                "amount": obj.amount,
                "account_id": prod.sale_account_id.id,
                "tax_id": prod.sale_tax_id.id,
            }
            inv_vals["lines"].append(("create",line_vals))
            inv_id=get_model("account.invoice").create(inv_vals,context={"type":"out","inv_type":"invoice"})
            obj.write({"invoice_id":inv_id})
        return {
            "alert": "Invoice created successfully",
        }

PaymentPlan.register()

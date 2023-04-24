from netforce.model import Model,fields,get_model
from netforce import access
from datetime import *
from decimal import *

class Grade(Model):
    _inherit="stock.grade"

    def validate(self,ids,context={}):
        super().validate(ids,context=context)
        obj=self.browse(ids[0])
        purch_ids=[]
        for line in obj.lines:
            if line.purchase_id:
                purch_ids.append(line.purchase_id.id)
        if purch_ids:
            res=get_model("purchase.order").kff_copy_to_supp_invoice(purch_ids)
            inv_id=res["invoice_id"]
            res=get_model("account.invoice").kff_copy_to_cust_invoice([inv_id])
            inv2_id=res["invoice_id"]
            get_model("account.invoice").kff_copy_to_cust_supp_invoice([inv2_id])

Grade.register()

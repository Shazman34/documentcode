from netforce.model import Model,fields,get_model
from netforce import access
import time

class CustDeposit(Model):
    _name="gt.cust.deposit"
    _string="Customer Deposit"
    _name_field="number"
    _audit_log=True
    _fields={
        "number": fields.Char("Number",required=True,search=True),
        "create_time": fields.DateTime("Create Time",required=True,search=True,readonly=True),
        "customer_id": fields.Many2One("gt.customer","Customer",required=True,search=True),
        "direction": fields.Selection([["in","From Customer"],["out","To Customer"]],"Direction",required=True,search=True),
        "type": fields.Selection([["cash","Cash (THB)"],["gold","Gold"]],"Type",required=True),
        "amount": fields.Decimal("Amount"),
        "product": fields.Selection([["96","96.5%"],["99","99.99% LBMA"]],"Product",search=True),
        "qty": fields.Decimal("Qty"),
        "state": fields.Selection([["draft","Draft"],["done","Completed"]],"Status",required=True,search=True),
    }
    _order="create_time desc"

    def _get_number(self, context={}):
        settings = get_model("gt.settings").browse(1)        
        seq_id = settings.seq_cust_deposit_id.id
        if not seq_id:
            return None
        while 1:
            num = get_model("sequence").get_next_number(seq_id, context=context)
            if not num:
                return None
            user_id = access.get_active_user()
            access.set_active_user(1)
            res = self.search([["number", "=", num]])
            access.set_active_user(user_id)
            if not res:
                return num
            get_model("sequence").increment_number(seq_id, context=context)

    _defaults={
        "create_time": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
        "number": _get_number,
        "state": "draft",
    }

    def set_done(self,ids,context={}):
        obj=self.browse(ids[0])
        obj.write({"state": "done"})
        if obj.direction=="out":
            obj.customer_id.check_account()

    def to_draft(self,ids,context={}):
        obj=self.browse(ids[0])
        obj.write({"state": "draft"})

CustDeposit.register()

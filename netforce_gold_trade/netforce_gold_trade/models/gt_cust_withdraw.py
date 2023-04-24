from netforce.model import Model,fields,get_model
from netforce import access
import time

class CustWithdraw(Model):
    _name="gt.cust.withdraw"
    _string="Customer Withdrawal"
    _fields={
        "number": fields.Char("Number",required=True,search=True),
        "withdraw_time": fields.DateTime("Deposit Time",required=True,search=True,readonly=True),
        "customer_id": fields.Many2One("gt.customer","Customer",required=True,search=True),
        "product": fields.Selection([["thb","THB"],["99","99.99% LBMA"],["96","96.5%"]],"Product",required=True,search=True),
        "amount": fields.Decimal("Amount"),
        "qty": fields.Decimal("Qty"),
    }
    _order="withdraw_time desc"

    def _get_number(self, context={}):
        settings = get_model("gt.settings").browse(1)        
        seq_id = settings.seq_cust_withdraw_id.id
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
        "withdraw_time": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
        "number": _get_number,
    }

CustWithdraw.register()

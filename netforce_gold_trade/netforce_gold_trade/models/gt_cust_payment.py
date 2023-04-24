from netforce.model import Model,fields,get_model
from netforce import access
from netforce.utils import get_data_path
import time

class CustPayment(Model):
    _name="gt.cust.payment"
    _string="Customer Payments"
    _name_field="number"
    _audit_log=True
    _fields={
        "number": fields.Char("Number",required=True,search=True),
        "payment_time": fields.DateTime("Payment Time",required=True,search=True),
        "customer_id": fields.Many2One("gt.customer","Customer",required=True,search=True),
        "direction": fields.Selection([["in","From Customer"],["out","To Customer"]],"Payment Direction",required=True,search=True),
        "is_deposit": fields.Boolean("Is Deposit",search=True),
        "state": fields.Selection([["draft","Draft"],["done","Completed"]],"Status",required=True,search=True),
        "lines": fields.One2Many("gt.cust.payment.line","payment_id","Lines"),
        "amount_total": fields.Decimal("Total Payment Amount",function="get_total",function_multi=True),
        "buy_99_qty": fields.Decimal("Buy 99.99% Qty",function="get_total",function_multi=True),
        "sell_99_qty": fields.Decimal("Sell 99.99% Qty",function="get_total",function_multi=True),
        "buy_96_qty": fields.Decimal("Buy 96.5% Qty",function="get_total",function_multi=True),
        "sell_96_qty": fields.Decimal("Sell 96.5% Qty",function="get_total",function_multi=True),
        "cust_bank_account_id": fields.Many2One("bank.account","Customer Bank Account"),
        "comp_bank_account_id": fields.Many2One("bank.account","Company Bank Account"),
    }
    _order="create_time desc"

    def _get_number(self, context={}):
        settings = get_model("gt.settings").browse(1)        
        seq_id = settings.seq_cust_payment_id.id
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
        "payment_time": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
        "number": _get_number,
        "state": "draft",
    }

    def set_done(self,ids,context={}):
        obj=self.browse(ids[0])
        obj.write({"state": "done"})
        for line in obj.lines:
            if line.order_id:
                line.order_id.update_state()
        if obj.direction=="out":
            obj.customer_id.check_account()

    def to_draft(self,ids,context={}):
        obj=self.browse(ids[0])
        obj.write({"state": "draft"})

    def get_total(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            amt=0
            buy_99_qty=0
            sell_99_qty=0
            buy_96_qty=0
            sell_96_qty=0
            for line in obj.lines:
                amt+=line.amount
                order=line.order_id
                if line.qty:
                    if order.type=="buy":
                        if order.product in ("96","96_mini"):
                            buy_96_qty+=line.qty
                        elif order.product=="99":
                            buy_99_qty+=line.qty
                    elif order.type=="sell":
                        if order.product in ("96","96_mini"):
                            sell_96_qty+=line.qty
                        elif order.product=="99":
                            sell_99_qty+=line.qty
            vals[obj.id]={
                "amount_total": amt,
                "buy_99_qty": buy_99_qty,
                "sell_99_qty": sell_99_qty,
                "buy_96_qty": buy_96_qty,
                "sell_96_qty": sell_96_qty,
            }
        return vals

    def onchange_order(self,context={}):
        data=context["data"]
        path=context["path"]
        line = get_data_path(data, path, parent=True)
        order_id=line["order_id"]
        order=get_model("gt.cust.order").browse(order_id)
        line["amount"]=order.amount_due
        return data

CustPayment.register()

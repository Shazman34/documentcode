from netforce.model import Model,fields,get_model
from netforce import access
import time

class CustPaymentLine(Model):
    _name="gt.cust.payment.line"
    _audit_log=True
    _fields={
        "payment_id": fields.Many2One("gt.cust.payment","Payment",required=True,on_delete="cascade"),
        "order_id": fields.Many2One("gt.cust.order","Order",required=True),
        "qty": fields.Decimal("Qty",required=True),
        "amount": fields.Decimal("Amount",required=True),
        "late_fee": fields.Decimal("Late Fee",function="_get_related",function_context={"path": "order_id.late_fee"}),
    }

CustPaymentLine.register()

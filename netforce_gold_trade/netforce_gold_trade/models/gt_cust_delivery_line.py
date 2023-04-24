from netforce.model import Model,fields,get_model
from netforce import access
import time

class CustDeliveryLine(Model):
    _name="gt.cust.delivery.line"
    _audit_log=True
    _fields={
        "delivery_id": fields.Many2One("gt.cust.delivery","Delivery",required=True,on_delete="cascade"),
        "order_id": fields.Many2One("gt.cust.order","Order",required=True),
        "product": fields.Selection([["96","96.5%"],["99","99.99% LBMA"]],"Product",required=True,search=True),
        "qty": fields.Decimal("Qty",required=True),
        "uom": fields.Selection([["baht","Baht"],["kg","Kg"]],"UoM",function="get_uom"),
    }

    def get_uom(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            uom=None
            if obj.product=="96":
                uom="baht"
            elif obj.product=="99":
                uom="kg"
            vals[obj.id]=uom
        return vals

CustDeliveryLine.register()

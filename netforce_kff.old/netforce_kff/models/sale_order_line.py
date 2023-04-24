from netforce.model import Model,fields,get_model
from netforce import access
from datetime import *
from decimal import *
import time

class OrderLine(Model):
    _inherit="sale.order.line"
    _fields={
        "qty_produced": fields.Decimal("Produced Qty", function="get_qty_produced"),
    }

    def get_qty_produced(self, ids, context={}):
        user_id=access.get_active_user()
        access.set_active_user(1)
        try:
            sale_ids=[]
            for obj in self.browse(ids):
                sale_ids.append(obj.order_id.id)
                for sale in obj.order_id.sale_orders:
                    sale_ids.append(sale.id)
            sale_ids=list(set(sale_ids))
            print("sale_ids",sale_ids)
            qtys={}
            for sale in get_model("sale.order").browse(sale_ids):
                for order in sale.production_orders:
                    k = order.product_id.id
                    qtys.setdefault(k,0)
                    qtys[k]+=order.qty_received
            vals={}
            for obj in self.browse(ids):
                k = obj.product_id.id
                qty=qtys.get(k,0)
                vals[obj.id]=qty
        finally:
            access.set_active_user(user_id)
        return vals

OrderLine.register()

from netforce.model import Model,fields,get_model
from netforce import access
import time

class CustDelivery(Model):
    _name="gt.cust.delivery"
    _string="Customer Delivery"
    _name_field="number"
    _audit_log=True
    _fields={
        "number": fields.Char("Number",required=True,search=True),
        "create_time": fields.DateTime("Create Time",required=True,search=True,readonly=True),
        "customer_id": fields.Many2One("gt.customer","Customer",required=True,search=True),
        "direction": fields.Selection([["in","From Customer"],["out","To Customer"]],"Delivery Direction",required=True,search=True),
        "state": fields.Selection([["draft","Draft"],["done","Completed"]],"Status",required=True,search=True),
        "lines": fields.One2Many("gt.cust.delivery.line","delivery_id","Lines"),
        "qty_96": fields.Decimal("Qty 96.5%",function="get_qty",function_multi=True),
        "qty_99": fields.Decimal("Qty 99.99%",function="get_qty",function_multi=True),
    }
    _order="create_time desc"

    def _get_number(self, context={}):
        settings = get_model("gt.settings").browse(1)        
        seq_id = settings.seq_cust_delivery_id.id
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
        #if obj.orders:
        #    if obj.product=="96":
        #        if obj.qty!=abs(obj.order_qty_96):
        #            raise Exception("Wrong delivery qty (%s, should be %s)"%(obj.qty,obj.order_qty_96))
        #    elif obj.product=="99":
        #        if obj.qty!=abs(obj.order_qty_99):
        #            raise Exception("Wrong delivery qty (%s, should be %s)"%(obj.qty,obj.order_qty_99))
        obj.write({"state": "done"})
        #for order in obj.orders:
        #    order.set_paid(context={"no_check_account":True})
        if obj.direction=="out":
            obj.customer_id.check_account()

    def to_draft(self,ids,context={}):
        obj=self.browse(ids[0])
        obj.write({"state": "draft"})

    def get_order_total(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            qty_96=0
            qty_99=0
            for order in obj.orders:
                if order.type=="buy":
                    if order.product=="96":
                        qty_96+=order.qty
                    elif order.product=="99":
                        qty_99+=order.qty
                elif order.type=="sell":
                    if order.product=="96":
                        qty_96-=order.qty
                    elif order.product=="99":
                        qty_99-=order.qty
            vals[obj.id]={
                "order_qty_96": qty_96,
                "order_qty_99": qty_99,
            }
        return vals

    def set_orders_paid(self,ids,context={}):
        obj=self.browse(ids[0])

    def onchange_order(self,context={}):
        data=context["data"]
        path=context["path"]
        line = get_data_path(data, path, parent=True)
        order_id=line["order_id"]
        order=get_model("gt.cust.order").browse(order_id)
        line["product"]=order.product
        line["qty"]=order.qty
        return data

    def get_qty(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            qty_96=0
            qty_99=0
            for line in obj.lines:
                if line.product=="96":
                    qty_96+=line.qty
                elif line.product=="99":
                    qty_99+=line.qty
            vals[obj.id]={
                "qty_96": qty_96,
                "qty_99": qty_99,
            }
        return vals

CustDelivery.register()

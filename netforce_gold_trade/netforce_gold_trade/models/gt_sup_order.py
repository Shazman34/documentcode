from netforce.model import Model,fields,get_model
from netforce import access
import time
from decimal import *
import requests

class SupOrder(Model):
    _name="gt.sup.order"
    _string="Supplier Order"
    _audit_log=True
    _fields={
        "number": fields.Char("Number",required=True,search=True),
        "time": fields.DateTime("Order Time",required=True,search=True,readonly=True),
        "symbol": fields.Char("Symbol",required=True,search=True),
        "side": fields.Selection([["buy","Buy"],["sell","Sell"]],"Side",required=True,search=True),
        "order_type": fields.Selection([["market","Market"],["limit","Limit"],["stop","Stop"]],"Order Type",required=True,search=True),
        "qty_kg": fields.Decimal("Qty (Kg)",required=True,scale=3),
        "qty_oz": fields.Decimal("Qty (Oz)",required=True,scale=3),
        "price": fields.Decimal("Price"),
        "amount": fields.Decimal("Total Amount",function="get_amount"),
        "time_in_force": fields.Selection([["gtc","Good Till Cancell"],["fok","Fill Or Kill"]],"Time In Force"),
        "state": fields.Selection([["draft","Draft"],["new","New"],["partial_filled","Partially Filled"],["filled","Filled"],["pending_new","Pending New"],["rejected","Rejected"],["canceled","Canceled"]],"Status",required=True,search=True),
        "fill_price": fields.Decimal("Fill Price",readonly=True),
    }
    _order="time desc"

    def _get_number(self, context={}):
        settings = get_model("gt.settings").browse(1)        
        seq_id = settings.seq_sup_order_id.id
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
        "time": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
        "number": _get_number,
        "state": "draft",
    }

    def get_amount(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            amt=(obj.qty_oz or 0)*(obj.price or 0)
            vals[obj.id]=amt
        return vals

    def confirm(self,ids,context={}):
        obj=self.browse(ids[0])
        obj.write({"state": "confirmed"})

    def to_draft(self,ids,context={}):
        obj=self.browse(ids[0])
        obj.write({"state": "draft"})

    def place_order(self,symbol,side,order_type,qty_kg,qty_oz,price,time_in_force,context={}):
        print("place_order symbol=%s side=%s order_type=%s qty_kg=%s qty_oz=%s price=%s"%(symbol,side,order_type,qty_kg,qty_oz,price))
        access.set_active_user(1)
        vals={
            "symbol": symbol,
            "side": side,
            "order_type": order_type,
            "qty_kg": qty_kg,
            "qty_oz": qty_oz,
            "price": price,
            "time_in_force": time_in_force,
        }
        order_id=self.create(vals)
        obj=self.browse(order_id)
        urls={
            "MKS-DEMO": "http://prices.netforce.com:9902/place_order",
            "INTL-DEMO": "http://prices.netforce.com:9903/place_order",
            "ICBC-DEMO": "http://prices.netforce.com:9904/place_order",
            "MKS": "http://prices2.netforce.com:10902/place_order",
            "INTL": "http://prices2.netforce.com:10903/place_order",
            "ICBC": "http://prices2.netforce.com:10904/place_order",
        }
        xg_code=symbol.split(":")[0]
        url=urls.get(xg_code)
        if not url:
            raise Exception("Invalid exchange code: %s"%xg_code)
        print("url",url)
        data={
            "order_id": obj.number,
            "symbol": "XAU/USD",
            "side": side,
            "ord_type": order_type,
            "price": order_type!="market" and price or None,
            "qty": qty_oz,
            "time_in_force": time_in_force,
        }
        print("data",data)
        headers={
            "Content-Type": "application/json",
            "NFX-API-KEY": "test",
        }
        req=requests.post(url,json=data,timeout=5)
        if req.status_code!=200:
            raise Exception("Invalid status: %s, %s"%(req.status,req.content))
        res=req.json()
        error=res.get("error")
        if error:
            raise Exception(error)
        state=res["state"]
        #obj.write({"state":state})
        return {
            "order_id": order_id,
            "order_number": obj.number,
            "state": state,
        }

    def subscribe_qty(self,qty_oz,context={}):
        print("-")
        print("subscribe_qty",qty_oz)
        url="http://prices.netforce.com:19903/subscribe_qty"
        data={
            "qty": qty_oz,
        }
        print("data",data)
        headers={
            "Content-Type": "application/json",
            "NFX-API-KEY": "test",
        }
        req=requests.post(url,json=data,timeout=5)
        if req.status_code!=200:
            raise Exception("Invalid status: %s, %s"%(req.status,req.content))
        res=req.json()
        error=res.get("error")
        if error:
            raise Exception(error)
        #obj.write({"state":state})
        return {
            "order_id": order_id,
            "order_number": obj.number,
            "state": state,
        }

SupOrder.register()

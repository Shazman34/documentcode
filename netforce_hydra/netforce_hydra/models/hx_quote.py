from netforce.model import Model,fields,get_model
from netforce import access
from netforce import database
from netforce import utils
import time
import random

class Quote(Model):
    _name="hx.quote"
    _string="Quote"
    _name_field="number"
    _fields={
        "time": fields.DateTime("Time",required=True),
        "number": fields.Char("Number",required=True),
        "rfq_id": fields.Many2One("hx.rfq","RFQ",required=True),
        "rfq_qty": fields.Decimal("RFQ Qty",scale=8,function="_get_related",function_context={"path":"rfq_id.qty"}),
        "rfq_price": fields.Decimal("RFQ Price",scale=8,function="_get_related",function_context={"path":"rfq_id.price"}),
        "rfq_asset_buy": fields.Char("RFQ Buy Asset",function="_get_related",function_context={"path":"rfq_id.asset_buy"}),
        "rfq_asset_sell": fields.Char("RFQ Sell Asset",function="_get_related",function_context={"path":"rfq_id.asset_sell"}),
        "qty": fields.Decimal("Qty",scale=8),
        "price": fields.Decimal("Price",scale=8,required=True),
        "amount": fields.Decimal("Amount",scale=8,function="get_amount"),
        "state": fields.Selection([["pending","Pending"],["accepted","Accepted"]],"Status",required=True),
        "user_id": fields.Many2One("base.user","Created By",required=True),
        "swap_id": fields.Many2One("hx.swap","Swap"),
    }
    _order="time desc"
    _defaults={
        "time": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
        "number": lambda *a: "Q-%.6d"%random.randint(0,1000000),
        "state": "pending",
        "user_id": lambda *a: access.get_active_user(),
    }

    def get_amount(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            vals[obj.id]=(obj.qty or 0)*(obj.price or 0)
        return vals

    def new_quote(self,data,context={}):
        rfq_id=data.get("rfq_id")
        if not rfq_id:
            raise Exception("Missing rfq_id")
        qty=data.get("qty")
        price=data.get("price")
        if not price:
            raise Exception("Missing price")
        vals={
            "rfq_id": rfq_id,
            "qty": qty,
            "price": price,
        }
        quote_id=self.create(vals)
        quote=self.browse(quote_id)
        return {
            "quote_id": quote_id,
            "number": quote.number,
        }

    def accept_quote(self,ids,context={}):
        quote=self.browse(ids[0])
        if quote.state!="pending":
            raise Exception("Invalid quote status")
        rfq=quote.rfq_id
        if rfq.state!="pending":
            raise Exception("Invalid RFQ status")
        vals={
            "rfq_id": rfq.id,
            "quote_id": quote.id,
            "from_user_id": quote.user_id.id,
            "from_asset": rfq.asset_sell,
            "from_qty": quote.amount,
            "to_user_id": rfq.user_id.id,
            "to_asset": rfq.asset_buy,
            "to_qty": rfq.qty,
        }
        swap_id=get_model("hx.swap").create(vals)
        rfq.write({"state":"accepted","accept_quote_id":quote.id,"swap_id":swap_id})
        quote.write({"state":"accepted","swap_id":swap_id})
        for q in rfq.quotes:
            if q.id!=quote.id:
                q.write({"state":"rejected"})
    
Quote.register()

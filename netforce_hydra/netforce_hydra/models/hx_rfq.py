from netforce.model import Model,fields,get_model
from netforce import access
from netforce import database
from netforce import utils
import time
import random

class RFQ(Model):
    _name="hx.rfq"
    _string="RFQ"
    _name_field="number"
    _fields={
        "time": fields.DateTime("Time",required=True),
        "number": fields.Char("Number",required=True),
        "user_id": fields.Many2One("base.user","Created By",required=True),
        "asset_buy": fields.Char("Buy Asset",required=True),
        "asset_sell": fields.Char("Sell Asset",required=True),
        "price": fields.Decimal("Price",scale=8),
        "qty": fields.Decimal("Qty",required=True,scale=8),
        "amount": fields.Decimal("Amount",scale=8,function="get_amount"),
        "state": fields.Selection([["pending","Pending"],["accepted","Accepted"]],"Status",required=True),
        "valid_until": fields.DateTime("Valid Until"),
        "quotes": fields.One2Many("hx.quote","rfq_id","Quotes"),
        "num_quotes": fields.Integer("# Quotes",function="get_num_quotes"),
        "accept_quote_id": fields.Many2One("hx.quote","Accepted Quote"),
        "swap_id": fields.Many2One("hx.swap","Swap"),
    }
    _order="time desc"
    _defaults={
        "time": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
        "number": lambda *a: "RFQ-%.6d"%random.randint(0,1000000),
        "state": "pending",
        "user_id": lambda *a: access.get_active_user(),
    }

    def get_amount(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            vals[obj.id]=(obj.qty or 0)*(obj.price or 0)
        return vals

    def get_num_quotes(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            vals[obj.id]=len(obj.quotes)
        return vals

    def new_rfq(self,data,context={}):
        asset_buy=data.get("asset_buy")
        if not asset_buy:
            raise Exception("Missing buy asset")
        asset_sell=data.get("asset_sell")
        if not asset_sell:
            raise Exception("Missing sell asset")
        qty=data.get("qty")
        if not qty:
            raise Exception("Missing qty")
        price=data.get("price")
        vals={
            "asset_buy": asset_buy,
            "asset_sell": asset_sell,
            "qty": qty,
            "price": price,
        }
        rfq_id=self.create(vals)
        rfq=self.browse(rfq_id)
        return {
            "rfq_id": rfq_id,
            "number": rfq.number,
        }

RFQ.register()

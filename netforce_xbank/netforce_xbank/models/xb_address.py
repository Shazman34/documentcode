from netforce.model import Model,fields,get_model
from netforce import database
from netforce import access
from datetime import *
import time
import requests
import json

class Address(Model):
    _name="xb.address"
    _string="Address"
    _name_field="address"
    _fields={
        "account_id": fields.Many2One("xb.account","Account",required=True,on_delete="cascade"),
        "currency": fields.Selection([["thb","THB"],["xbt","XBT"],["ltc","LTC"],["eth","ETH"]],"Currency",required=True),
        "address": fields.Char("Address",required=True),
        "balance0": fields.Decimal("Balance (0-conf)",scale=8),
        "balance1": fields.Decimal("Balance (1-conf)",scale=8),
        "balance2": fields.Decimal("Balance (2-conf)",scale=8),
        "balance3": fields.Decimal("Balance (3-conf)",scale=8),
        "balance10": fields.Decimal("Balance (10-conf)",scale=8),
    }

    def update_balance(self,context={}):
        print("update_balance")
        db=database.get_connection()
        settings=get_model("xb.settings").browse(1)
        for currency in ("xbt",):
            url="http://%s/get_balances"%settings.node_ip
            params={
                "currency": currency,
            }
            req=requests.post(url,json=params,timeout=15)
            if req.status_code!=200:
                raise Exception("Invalid status code")
            res=req.json()
            db.execute("UPDATE xb_address SET balance0=0,balance1=0,balance2=0,balance3=0,balance10=0 WHERE currency=%s",currency)
            for addr,amt in res["balance0"].items():
                db.execute("UPDATE xb_address SET balance0=%s WHERE address=%s AND currency=%s",amt,addr,currency)
            for addr,amt in res["balance1"].items():
                db.execute("UPDATE xb_address SET balance1=%s WHERE address=%s AND currency=%s",amt,addr,currency)
            for addr,amt in res["balance2"].items():
                db.execute("UPDATE xb_address SET balance2=%s WHERE address=%s AND currency=%s",amt,addr,currency)
            for addr,amt in res["balance3"].items():
                db.execute("UPDATE xb_address SET balance3=%s WHERE address=%s AND currency=%s",amt,addr,currency)
            for addr,amt in res["balance10"].items():
                db.execute("UPDATE xb_address SET balance10=%s WHERE address=%s AND currency=%s",amt,addr,currency)

Address.register()

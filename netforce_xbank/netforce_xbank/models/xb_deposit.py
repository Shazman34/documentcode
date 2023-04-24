from netforce.model import Model,fields,get_model
from netforce import database
from netforce import access
from datetime import *
import time
import requests
import json

class Deposit(Model):
    _name="xb.deposit"
    _string="Customer Deposit"
    _name_field="number"
    _fields={
        "number": fields.Char("Number",required=True),
        "date_created": fields.DateTime("Date Created",required=True),
        "account_id": fields.Many2One("xb.account","Account",required=True),
        "currency": fields.Selection([["thb","THB"],["xbt","XBT"],["ltc","LTC"],["eth","ETH"]],"Currency",required=True),
        "amount": fields.Decimal("Amount",scale=6,required=True),
        "address": fields.Char("Address"),
        "state": fields.Selection([["done","Completed"]],"Status"),
        "txid": fields.Char("Transaction ID",readonly=True),
    }

    def _get_number(self, context={}):
        seq_id = get_model("sequence").find_sequence(name="xb_deposit",context=context)
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
        "state": "done",
        "date_created": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
        "number": _get_number,
    }
    _order="date_created desc"

    def confirm(self,ids,context={}):
        obj=self.browse(ids[0])
        if not obj.address:
            raise Exception("Missing address")
        obj.write({"state": "pending"})

    def check_received(self,context={}):
        print("check_received")
        for currency in ("xbt",):
            url="http://xbnode.netforce.com/list_received"
            params={
                "currency": currency,
            }
            req=requests.post(url,json=params)
            if req.status_code!=200:
                raise Exception("Invalid status code")
            received=req.json()
            for r in received:
                print("txid",r["txid"])
                res=self.search([["txid","=",r["txid"]]])
                if res:
                    print("skip, already imported")
                    continue
                if currency=="xbt":
                    cond=[["address_xbt","=",r["address"]]]
                elif currency=="ltc":
                    cond=[["address_ltc","=",r["address"]]]
                elif currency=="eth":
                    cond=[["address_eth","=",r["address"]]]
                else:
                    raise Exception("Invalid currency")
                res=get_model("xb.account").search(cond)
                if not res:
                    print("skip, account not found: %s"%r["address"])
                    continue
                acc_id=res[0]
                vals={
                    "account_id": acc_id,
                    "amount": r["amount"],
                    "currency": currency,
                    "txid": r["txid"],
                }
                get_model("xb.deposit").create(vals)

Deposit.register()

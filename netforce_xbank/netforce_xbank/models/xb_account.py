from netforce.model import Model,fields,get_model
from netforce import database
from datetime import *
import time
import requests
import json

class Account(Model):
    _name="xb.account"
    _string="XBank Account"
    _fields={
        "name": fields.Char("Name",required=True),
        "date_created": fields.DateTime("Date Created",required=True),
        "balance_thb": fields.Decimal("Balance THB",function="get_balances",function_multi=True),
        "balance_xbt": fields.Decimal("Balance XBT",scale=6,function="get_balances",function_multi=True),
        "balance_ltc": fields.Decimal("Balance LTC",scale=6,function="get_balances",function_multi=True),
        "balance_eth": fields.Decimal("Balance ETH",scale=6,function="get_balances",function_multi=True),
        "address_xbt_id": fields.Many2One("xb.address","Default Address XBT"),
        "address_ltc_id": fields.Many2One("xb.address","Default Address LTC"),
        "address_eth_id": fields.Many2One("xb.address","Default Address ETH"),
        "addresses": fields.One2Many("xb.address","account_id","Addresses"),
        "transactions": fields.One2Many("xb.transaction","account_id","Transactions"),
        "notif_url": fields.Char("Notification URL"),
    }
    _defaults={
        "date_created": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    _order="date_created"

    def new_addr_xbt(self,ids,context={}):
        print("new_addr_xbt",ids)
        settings=get_model("xb.settings").browse(1)
        obj=self.browse(ids[0])
        url="http://%s/new_address"%settings.node_ip
        print("url",url)
        params={
            "currency": "xbt",
        }
        r=requests.post(url,json=params,timeout=15)
        if r.status_code!=200:
            raise Exception("Invalid status code")
        addr=r.text.strip()
        vals={
            "account_id": obj.id,
            "currency": "xbt",
            "address": addr,
        }
        addr_id=get_model("xb.address").create(vals)
        if not obj.address_xbt_id:
            obj.write({"address_xbt_id":addr_id})
        return addr_id

    def new_addr_ltc(self,ids,context={}):
        print("new_addr_ltc",ids)
        settings=get_model("xb.settings").browse(1)
        obj=self.browse(ids[0])
        url="http://%s/new_address"%settings.node_ip
        params={
            "currency": "ltc",
        }
        r=requests.post(url,json=params,timeout=15)
        if r.status_code!=200:
            raise Exception("Invalid status code")
        addr=r.text.strip()
        vals={
            "account_id": obj.id,
            "currency": "ltc",
            "address": addr,
        }
        addr_id=get_model("xb.address").create(vals)
        if not obj.address_ltc_id:
            obj.write({"address_ltc_id":addr_id})
        return addr_id

    def get_balances(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            bals={}
            for addr in obj.addresses:
                bals.setdefault(addr.currency,0)
                bals[addr.currency]+=addr.balance0 or 0
            vals[obj.id]={
                "balance_thb": bals.get("thb",0),
                "balance_xbt": bals.get("xbt",0),
                "balance_ltc": bals.get("ltc",0),
                "balance_eth": bals.get("eth",0),
            }
        return vals

Account.register()

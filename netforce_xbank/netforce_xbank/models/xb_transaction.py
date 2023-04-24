from netforce.model import Model,fields,get_model
from netforce import database
from netforce import access
from datetime import *
import time
import requests
import json

class Transaction(Model):
    _name="xb.transaction"
    _string="Transaction"
    _name_field="number"
    _fields={
        "account_id": fields.Many2One("xb.account","Account",required=True),
        "currency": fields.Selection([["thb","THB"],["xbt","XBT"],["ltc","LTC"],["eth","ETH"]],"Currency",required=True),
        "hash": fields.Char("Hash",required=True),
        "address": fields.Text("Address"),
        "date": fields.DateTime("Date",required=True),
        "amount": fields.Decimal("Amount",scale=8,required=True),
        "balance": fields.Decimal("Balance",scale=8),
        "num_conf": fields.Integer("Confirmations"),
        "acc_addrs": fields.Text("Account Address"),
    }
    _order="date desc"

    def update_transactions(self,context={}):
        print("#"*80)
        print("#"*80)
        print("#"*80)
        print("Transaction.update_transactions")
        settings=get_model("xb.settings").browse(1)
        for currency in ("xbt",):
            url="http://%s/get_transactions"%settings.node_ip
            params={
                "currency": currency,
            }
            req=requests.post(url,json=params)
            if req.status_code!=200:
                raise Exception("Invalid status code")
            tx_data=req.json()
            for r in tx_data:
                txid=r["txid"]
                print("import transaction %s..."%txid)
                ids=self.search([["currency","=",currency],["hash","=",txid]])
                if ids:
                    self.write(ids,{"num_conf":r["confirmations"]})
                    continue
                acc_bals={}
                addr_accs={}
                for addr,amt in r["addrs"].items():
                    res=get_model("xb.address").search([["currency","=",currency],["address","=",addr]])
                    if not res:
                        print("address %s not found"%addr)
                        addr_accs[addr]=None
                        continue
                    addr_id=res[0]
                    addr_obj=get_model("xb.address").browse(addr_id)
                    acc_id=addr_obj.account_id.id
                    acc_bals.setdefault(acc_id,0)
                    acc_bals[acc_id]+=amt
                    addr_accs[addr]=acc_id
                print("acc_bals",acc_bals)
                for acc_id,amt in acc_bals.items():
                    other_addrs=[addr for addr in addr_accs if addr_accs[addr]!=acc_id]
                    acc_addrs=[addr for addr in addr_accs if addr_accs[addr]==acc_id]
                    vals={
                        "account_id": acc_id,
                        "currency": currency,
                        "hash": txid,
                        "amount": amt,
                        "date": r["time"],
                        "num_conf": r["confirmations"],
                        "address": "\n".join(sorted(other_addrs)),
                        "acc_addrs": "\n".join(sorted(acc_addrs)),
                    }
                    trans_id=self.create(vals)
                    self.send_notif([trans_id])
        self.update_balances()

    def update_balances(self,context={}):
        bals={}
        for obj in self.search_browse([],order="date,id"):
            acc_id=obj.account_id.id
            bals.setdefault(acc_id,0)
            bals[acc_id]+=obj.amount
            if obj.balance!=bals[acc_id]:
                obj.write({"balance":bals[acc_id]})

    def send_notif(self,ids,context={}):
        print("#"*80)
        print("Transaction.send_notif",ids)
        obj=self.browse(ids[0])
        acc=obj.account_id
        url=acc.notif_url
        if not url:
            return
        pmt_url="bitcoin:%s?amount=%s"%(obj.acc_addrs,obj.amount)
        data={
            "account": acc.name,
            "currency": obj.currency,
            "hash": obj.hash,
            "address": obj.address,
            "date": obj.date,
            "amount": obj.amount,
            "num_conf": obj.num_conf,
            "acc_addrs": obj.acc_addrs,
            "payment_url": pmt_url,
        }
        try:
            req=requests.post(url,data=data,timeout=10)
            if req.status_code!=200:
                raise Exception("Invalid status code: %s"%req.status_code)
        except Exception as e:
            print("ERROR: failed to send notification: %s"%e)
            return {
                "flash": "Notif failed: %s"%e,
            }
        return {
            "flash": "Notif success",
        }

Transaction.register()

from netforce.model import Model,fields,get_model
from netforce import database
from netforce import access
from datetime import *
import time
import requests

class Withdrawal(Model):
    _name="xb.withdraw"
    _string="Withdrawal"
    _name_field="number"
    _fields={
        "number": fields.Char("Number",required=True),
        "date_created": fields.DateTime("Date Created",required=True),
        "account_id": fields.Many2One("xb.account","Account",required=True),
        "currency": fields.Selection([["thb","THB"],["xbt","XBT"],["ltc","LTC"],["eth","ETH"]],"Currency",required=True),
        "amount": fields.Decimal("Amount",scale=6,required=True),
        "address": fields.Char("Address",required=True),
        "state": fields.Selection([["draft","Draft"],["done","Completed"]],"Status",required=True),
        "txid": fields.Char("Transaction ID",readonly=True),
    }

    def _get_number(self, context={}):
        seq_id = get_model("sequence").find_sequence(name="xb_withdraw",context=context)
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
        "state": "draft",
        "date_created": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
        "number": _get_number,
    }
    _order="date_created desc"

    def confirm(self,ids,context={}):
        settings=get_model("xb.settings").browse(1)
        obj=self.browse(ids[0])
        if not obj.address:
            raise Exception("Missing address")
        url="http://%s/send"%settings.node_ip
        from_addrs=[]
        for addr in obj.account_id.addresses:
            if addr.currency==obj.currency:
                from_addrs.append(addr.address)
        params={
            "currency": obj.currency,
            "from_addrs": from_addrs,
            "to_addr": obj.address,
            "amount": float(obj.amount),
            "fee": 0.0001,
        }
        r=requests.post(url,json=params,timeout=15)
        if r.status_code!=200:
            raise Exception("Invalid status code")
        txid=r.text.strip()
        obj.write({"state":"done","txid": txid})
        get_model("xb.address").update_balance()

    def to_draft(self,ids,context={}):
        obj=self.browse(ids[0])
        obj.write({"state":"draft","txid":None})

Withdrawal.register()

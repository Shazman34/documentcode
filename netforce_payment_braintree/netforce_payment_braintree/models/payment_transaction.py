from netforce.model import Model,fields
import requests
import urllib
from decimal import *

class Trans(Model):
    _inherit="payment.transaction"
    _fields={
        "paypal_token": fields.Char("Paypal Token"),
        "paypal_trans_no": fields.Char("Paypal Transaction No.",search=True),
    }

    def check_payment_received(self,ids,context={}):
        print("Trans.check_payment_received",ids);
        res=super().check_payment_received(ids,context=context)
        if res:
            return res
        obj=self.browse(ids[0])
        if obj.type!="paypal":
            return
        meth=obj.pay_method_id
        if meth.type!="paypal":
            return
        if not obj.paypal_trans_no:
            return {
                "alert": "Missing Paypal transaction ID",
                "alert_type": "danger",
            }
        data={
            "METHOD": "GetTransactionDetails",
            "VERSION": "104.0",
            "USER": meth.paypal_user,
            "PWD": meth.paypal_password,
            "SIGNATURE": meth.paypal_signature,
            "TRANSACTIONID": obj.paypal_trans_no.replace("{","").replace("}",""),
        }
        if not meth.paypal_nvp_url:
            raise Exception("Missing Paypal NVP API URL")
        print("Paypal SetExpressCheckout request: %s"%data)
        print("URL: %s"%meth.paypal_nvp_url)
        r = requests.get(meth.paypal_nvp_url, params=data, timeout=10)
        res = urllib.parse.parse_qs(r.text)
        print("Paypal SetExpressCheckout response:", res)
        status = res["PAYMENTSTATUS"][0]
        if status!="Completed":
            if obj.state=="done":
                obj.payment_reversed()
            return {
                "alert": "Payment not received (status=%s)"%status,
                "alert_type": "danger",
            }
        try:
            amount_s = res["AMT"][0]
            amount=Decimal(amount_s.replace(",",""))
            if amount!=obj.amount:
                raise Exception("Wrong amount: %s"%amount)
            if obj.state!="done":
                obj.payment_received()
            return {
                "alert": "Payment received (status=%s, amount=%s)"%(status,amount),
            }
        except:
            import traceback
            error=traceback.format_exc()
            obj.payment_error(context={"error": error}) 
    
Trans.register()

from netforce.model import Model,fields,get_model
import hashlib
import requests
import urllib
from datetime import *
import time
from netforce.utils import json_dumps
import paypalrestsdk

class PaymentMethod(Model):
    _inherit="payment.method"
    _fields={
        "type": fields.Selection([["cash","Cash"], ["bank", "Bank Transfer"], ["cheque","Cheque"], ["credit_card", "Credit Card"], ["paypal", "Paypal"],["scb_gateway","SCB Gateway"], ["paysbuy","Paysbuy"]], "Type", search=True), # XXX: inherit
        "paypal_user": fields.Char("Paypal User"),
        "paypal_password": fields.Char("Paypal Password"),
        "paypal_signature": fields.Char("Paypal Signature"),
        "paypal_return_url": fields.Char("Paypal Return URL"),
        "paypal_cancel_url": fields.Char("Paypal Cancel URL"),
        "paypal_nvp_url": fields.Char("Paypal NVP API URL"),
        "paypal_webscr_url": fields.Char("Paypal Webscr URL"),
        "paypal_client_id": fields.Char("Paypal Client ID"),
        "paypal_secret": fields.Char("Paypal Secret"),
        "paypal_sandbox": fields.Boolean("Use Paypal Sandbox"),
    }
    
    def start_payment(self,ids,context={}):
        print("Paypal.start_payment")
        res=super().start_payment(ids,context=context)
        if res:
            return res
        obj=self.browse(ids[0])
        if obj.type=="paypal":
            if not obj.paypal_client_id:
                raise Exception("Missing Paypal Client ID")
            if not obj.paypal_secret:
                raise Exception("Missing Paypal Secret")
            api=paypalrestsdk.Api({
                "mode": obj.paypal_sandbox and "sandbox" or "live",
                "client_id": obj.paypal_client_id,
                "client_secret": obj.paypal_secret,
            })
            amount=context["amount"]
            currency_id=context["currency_id"]
            currency=get_model("currency").browse(currency_id)
            if not obj.paypal_return_url:
                raise Exception("Missing Paypal return URL")
            if not obj.paypal_cancel_url:
                raise Exception("Missing Paypal cancel URL")
            pmt=paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal",
                },
                "redirect_urls": {
                    "return_url": obj.paypal_return_url,
                    "cancel_url": obj.paypal_cancel_url,
                },
                "transactions": [{
                    "item_list": {
                        "items": [{
                            "name": "Quick Consult", # XXX
                            "sku": "QC",
                            "price": "%.2f"%amount,
                            "currency": currency.code,
                            "quantity": 1,
                        }]
                    },
                    "amount": {
                        "total": "%.2f"%amount,
                        "currency": currency.code,
                    },
                    "description": "This is the payment transaction description.",
                }]
            },api=api)
            if not obj.paypal_webscr_url:
                raise Exception("Missing Paypal Webscr URL")
            res=pmt.create()
            if not res:
                raise Exception(pmt.error)
            token=pmt.id
            approval_url=pmt.links[1]["href"]
            vals={
                "type": "paypal",
                "pay_method_id": obj.id,
                "amount": amount,
                "currency_id": currency.id,
                "contact_id": context.get("contact_id"),
                "related_id": context.get("related_id"),
                "return_url": context.get("return_url"),
                "error_url": context.get("error_url"),
                "paypal_token": token,
            }
            trans_id=get_model("payment.transaction").create(vals)
            return {
                "transaction_id": trans_id,
                "payment_action": {
                    "type": "url",
                    "url": approval_url,
                }
            }

    def start_payment_old(self,ids,context={}):
        print("Paypal.start_payment")
        res=super().start_payment(ids,context=context)
        if res:
            return res
        obj=self.browse(ids[0])
        if obj.type=="paypal":
            amount=context["amount"]
            currency_id=context["currency_id"]
            currency=get_model("currency").browse(currency_id)
            if not obj.paypal_user:
                raise Exception("Missing Paypal user")
            if not obj.paypal_password:
                raise Exception("Missing Paypal password")
            if not obj.paypal_signature:
                raise Exception("Missing Paypal signature")
            if not obj.paypal_return_url:
                raise Exception("Missing Paypal return URL")
            if not obj.paypal_cancel_url:
                raise Exception("Missing Paypal cancel URL")
            data={
                "METHOD": "SetExpressCheckout",
                "VERSION": "104.0",
                "USER": obj.paypal_user,
                "PWD": obj.paypal_password,
                "SIGNATURE": obj.paypal_signature,
                "PAYMENTREQUEST_0_AMT": "%.2f" % amount,
                "PAYMENTREQUEST_0_CURRENCYCODE": currency.code,
                "RETURNURL": obj.paypal_return_url,
                "CANCELURL": obj.paypal_cancel_url,
                "PAYMENTREQUEST_0_PAYMENTACTION": "Sale",
                "LANDINGPAGE": "Billing",
                "NOSHIPPING": "1",
                "LOCALECODE": "en_US",
            }
            if not obj.paypal_nvp_url:
                raise Exception("Missing Paypal NVP API URL")
            print("Paypal SetExpressCheckout request: %s"%data)
            print("URL: %s"%obj.paypal_nvp_url)
            r = requests.get(obj.paypal_nvp_url, params=data, timeout=10)
            res = urllib.parse.parse_qs(r.text)
            print("Paypal SetExpressCheckout response:", res)
            token = res["TOKEN"][0]
            if not obj.paypal_webscr_url:
                raise Exception("Missing Paypal Webscr URL")
            url=obj.paypal_webscr_url+"?cmd=_express-checkout&token=%s"%token
            vals={
                "type": "paypal",
                "pay_method_id": obj.id,
                "amount": amount,
                "currency_id": currency.id,
                "contact_id": context.get("contact_id"),
                "related_id": context.get("related_id"),
                "return_url": context.get("return_url"),
                "error_url": context.get("error_url"),
                "paypal_token": token,
            }
            trans_id=get_model("payment.transaction").create(vals)
            return {
                "transaction_id": trans_id,
                "payment_action": {
                    "type": "url",
                    "url": url,
                }
            }

PaymentMethod.register()

from netforce.model import Model,fields,get_model
from netforce import access
from datetime import *
import time

class Trans(Model):
    _name="payment.transaction"
    _string="Payment Transaction"
    _audit_log=True
    _fields={
        "start_time": fields.DateTime("Start Time",required=True),
        "type": fields.Selection([["bank","Bank Transfer"],["paypal","Paypal"],["paypal_preap","Paypal Preapproved"],["paysbuy","Paysbuy"],["2c2p","2C2P"],["xbank","XBank"],["blockchain","Blockchain.info"]],"Type",required=True,search=True),
        "pay_method_id": fields.Many2One("payment.method","Payment Method",required=True,search=True),
        "amount": fields.Decimal("Amount"),
        "currency_id": fields.Many2One("currency","Currency"),
        "contact_id": fields.Many2One("contact","Contact",search=True),
        "related_id": fields.Reference([["sale.order","Sales Order"],["account.invoice","Invoice"]],"Related To"),
        "state": fields.Selection([["in_progress","In Progress"],["done","Completed"],["reversed","Reversed"],["error","Error"]],"Status",required=True,search=True),
        "end_time": fields.DateTime("End Time"),
        "error": fields.Text("Error Message"),
        "request_details": fields.Text("Request Details"),
        "response_details": fields.Text("Response Details",search=True),
        "return_url": fields.Char("Return URL",size=1024),
        "error_url": fields.Char("Error URL",size=1024),
        "card_token_id": fields.Many2One("card.token","Card Token"),
        "bank_transfer_amount": fields.Decimal("Bank Transfer Actual Amount"),
        "bank_transfer_receipt": fields.File("Bank Transfer Receipt"),
        "bank_confirmation_no": fields.Char("Bank Confirmation No"),
        "company_id": fields.Many2One("company","Company",required=True),
        "payment_id": fields.Many2One("account.payment","Payment"),
    }
    _order="start_time desc, id desc"
    _defaults={
        "state": "in_progress",
        "start_time": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
        "company_id": lambda *a: access.get_active_company() or 1, # XXX
    }

    def name_get(self,ids,**kw):
        return [(id,"#%d"%id) for id in ids]

    def payment_error(self,ids,context={}):
        print("!"*80)
        print("Trans.payment_error")
        obj=self.browse(ids[0])
        t=time.strftime("%Y-%m-%d %H:%M:%S")
        obj.write({
            "state": "error",
            "error": context.get("error"),
            "end_time": t,
        })

    def payment_received(self,ids,context={}):
        print("Trans.payment_received")
        obj=self.browse(ids[0])
        t=time.strftime("%Y-%m-%d %H:%M:%S")
        obj.write({
            "state": "done",
            "end_time": t,
        })

    def payment_reversed(self,ids,context={}):
        print("Trans.payment_reversed")
        obj=self.browse(ids[0])
        obj.write({
            "state": "reversed",
        })

    # TODO: rename to check_payment_status
    def check_payment_received(self,ids,context={}):
        pass

    def check_all_payment_received(self,context={}):
        print("Trans.check_all_payment_received")
        min_d=(datetime.today()-timedelta(days=30)).strftime("%Y-%m-%d")
        for obj in self.search_browse([["start_time",">=",min_d],["state","=","in_progress"]]):
            print("#"*80)
            print("checking transaction %s"%obj.id)
            obj.check_payment_received()

    def manual_received(self,ids,context={}):
        obj=self.browse(ids[0])
        user_id=access.get_active_user()
        user=get_model("base.user").browse(user_id)
        obj.write({"response_details":"Manually received by %s"%user.name})
        obj.payment_received(context={})

    def check_all_payment_reversed(self,context={}):
        print("Trans.check_all_payment_reversed")
        min_d=(datetime.today()-timedelta(days=7)).strftime("%Y-%m-%d")
        for obj in self.search_browse([["start_time",">=",min_d],["state","=","done"]]):
            print("#"*80)
            print("checking transaction %s"%obj.id)
            obj.check_payment_received()

Trans.register()

from netforce.model import Model,fields,get_model
from netforce import access
import time

class Card(Model):
    _name="card.token"
    _string="Credit Card Token"
    _name_field="mask_card"
    _fields={
        "add_time": fields.DateTime("Time Added",required=True),
        "contact_id": fields.Many2One("contact","Contact",search=True),
        "brand": fields.Selection([["visa","Visa"],["master","Mastercard"],["amex","American Express"]],"Brand",search=True),
        "mask_card": fields.Char("Masked Card Info"),
        "last4": fields.Char("Last 4 Digits",search=True),
        "exp_month": fields.Char("Expiry Month",required=True,search=True),
        "exp_year": fields.Char("Expiry Year",required=True,search=True),
        "state": fields.Selection([["active","Active"],["inactive","Inactive"]],"Status",required=True),
        "token_type": fields.Selection([["stripe","Stripe"],["braintree","BrainTree"],["2c2p","2C2P"],["omise","Omise"]],"Token Type",search=True),
        "token": fields.Char("Token"),
        "name": fields.Char("Cardholder Name"),
    }
    _defaults={
        "state": "active",
        "add_time": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    _order="add_time desc"

    def delete_card_token(self,ids,context={}):
        if not ids:
            raise Exception("Missing card ids")
        user_id=access.get_active_user()
        if not user_id:
            raise Exception("User is not logged in.")
        access.set_active_user(1) # XXX
        user=get_model("base.user").browse(user_id)
        contact=user.contact_id
        obj=self.browse(ids[0])
        if obj.contact_id.id!=contact.id:
            raise Exception("Credit card belongs to other user")
        obj.delete()

    def add_missing_names(self,ids,context={}):
        for obj in self.browse(ids):
            if not obj.name:
                obj.write({"name":obj.contact_id.name})

Card.register()

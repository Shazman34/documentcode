from netforce.model import Model,fields,get_model

class Account(Model):
    _inherit="sms.account"
    _fields={
        "nexmo_api_key": fields.Text("Nexmo API Key"),
        "nexmo_api_secret": fields.Char("Nexmo API Secret"),
    }

Account.register()

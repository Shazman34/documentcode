from netforce.model import Model,fields,get_model

class Account(Model):
    _inherit="voice.account"
    _fields={
        "nexmo_app_id": fields.Char("Nexmo App ID"),
        "nexmo_private_key": fields.Text("Nexmo Private Key"),
        "nexmo_phone": fields.Char("Nexmo Phone"),
        "nexmo_app_name": fields.Char("Nexmo App Name"),
        "nexmo_key": fields.Char("Nexmo Key"),
        "nexmo_secret": fields.Char("Nexmo Secret"),
    }

Account.register()

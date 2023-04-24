from netforce.model import Model,fields,get_model

class User(Model):
    _inherit="base.user"
    _fields={
        "xb_account_id": fields.Many2One("xb.account","XBank Account"),
    }

User.register()

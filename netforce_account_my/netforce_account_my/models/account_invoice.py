from netforce.model import Model,fields,get_model 

class Invoice(Model):
    _inherit="account.invoice"
    _fields={
        "self_billed": fields.Boolean("Self-Billed Invoice"),
        "bad_debt": fields.Boolean("Bad Debt"),
    }

Invoice.register()

from netforce.model import Model,fields

class PricePlan(Model):
    _name="price.plan"
    _string="Price Plan"
    _fields={
        "name": fields.Char("Plan Name",required=True,search=True),
        "price": fields.Decimal("Price (USD per month)",required=True),
        "addons": fields.Many2Many("addon","Included Addons"),
        "sequence": fields.Integer("Sequence"),
    }
    _order="sequence"

PricePlan.register()   

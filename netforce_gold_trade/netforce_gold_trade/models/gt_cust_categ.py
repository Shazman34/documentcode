from netforce.model import Model,fields,get_model

class Categ(Model):
    _name="gt.cust.categ"
    _string="Customer Category"
    _fields={
        "name": fields.Char("Name",required=True,search=True), 
        "min_margin": fields.Decimal("Min Margin (%)",required=True),
        "disable_margin": fields.Boolean("Disable Margin Check"),
        "payment_days": fields.Decimal("Payment Terms (Days)",required=True),
        "late_pay_fee": fields.Decimal("Late Payment Fee (THB/baht/day)",required=True),
    }
    _order="name"

Categ.register()

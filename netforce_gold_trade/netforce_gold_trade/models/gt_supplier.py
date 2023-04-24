from netforce.model import Model,fields,get_model
import time

class Supplier(Model):
    _name="gt.supplier"
    _string="Supplier"
    _audit_log=True
    _fields={
        "name": fields.Char("Supplier Name",required=True,search=True), 
        "orders": fields.One2Many("gt.sup.order","supplier_id","Orders"),
    }
    _order="name"

Supplier.register()

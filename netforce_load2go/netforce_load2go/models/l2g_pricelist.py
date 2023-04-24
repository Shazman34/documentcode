from netforce.model import Model,fields,get_model
import time

class PriceList(Model):
    _name="l2g.pricelist"
    _string="Price List"
    _key=["name"]
    _fields={
        "name": fields.Char("Name",required=True,search=True),
        "from_regions": fields.Many2Many("l2g.province","Pickup Regions",reltable="m2m_pricelist_from_regions",search=True),
        "to_regions": fields.Many2Many("l2g.province","Delivery Regions",reltable="m2m_pricelist_to_regions",search=True),
        "customer_id": fields.Many2One("l2g.customer","Customer",search=True), # XXX: deprecated
        "customers": fields.Many2Many("l2g.customer","Customers",search=True),
        "prices": fields.One2Many("l2g.price","pricelist_id","Prices"),
        "sequence": fields.Integer("Sequence"),
    }
    _order="sequence,name"

PriceList.register()

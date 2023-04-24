from netforce.model import Model,fields,get_model
import time

class Province(Model):
    _name="l2g.province"
    _string="Province"
    _fields={
        "name": fields.Char("Region Name"),
        "disable_pickup": fields.Boolean("Disable Pickup"),
        "disable_delivery": fields.Boolean("Disable Delivery"),
        "min_weight": fields.Decimal("Min Weight (tons)"), # XXX: deprecated
        "locations": fields.One2Many("l2g.location","region_id","Locations"),
        "min_weights": fields.One2Many("l2g.min.weight","region_id","Min Weights"),
        "price_extra_percent": fields.Decimal("Delivery Extra Price %"),
    }
    _order="name"

Province.register()

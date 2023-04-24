from netforce.model import Model,fields,get_model
import time

class MinWeight(Model):
    _name="l2g.min.weight"
    _string="Min Weight"
    _fields={
        "truck_type_id": fields.Many2One("l2g.truck.type","Truck Type"),
        "region_id": fields.Many2One("l2g.province","Region"),
        "min_weight": fields.Integer("Min Weight"),
    }

MinWeight.register()

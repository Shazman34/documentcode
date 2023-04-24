from netforce.model import Model,fields,get_model
import time

class WeightRange(Model):
    _name="l2g.weight.range"
    _string="Weight Range"
    _fields={
        "truck_type_id": fields.Many2One("l2g.truck.type","Truck Type"),
        "min_weight": fields.Decimal("Min Weight"),
        "max_weight": fields.Decimal("Max Weight"),
        "name": fields.Char("Name"),
    }
    _order="max_weight"

    def name_get(self,ids,**kw):
        vals=[]
        for obj in self.browse(ids):
            vals.append((obj.id,str(obj.max_weight)))
        return vals

WeightRange.register()

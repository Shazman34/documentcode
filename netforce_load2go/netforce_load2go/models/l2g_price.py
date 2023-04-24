from netforce.model import Model,fields,get_model
import time

class Price(Model):
    _name="l2g.price"
    _string="Price"
    _fields={
        "pricelist_id": fields.Many2One("l2g.pricelist","Pricelist",required=True,search=True,on_delete="cascade"),
        "truck_type_id": fields.Many2One("l2g.truck.type","Truck Type",search=True),
        "max_weight": fields.Decimal("Max Weight (Ton)"),
        "min_distance": fields.Decimal("Min Distance (Km)"),
        "from_district": fields.Char("From District"),
        "to_district": fields.Char("To District"),
        "fare_per_km": fields.Decimal("Fare Per Km Per Ton",scale=3),
        "fare_per_ton": fields.Decimal("Fare Per Ton",scale=3),
        "min_fare": fields.Decimal("Min. Fare"),
        "cancel_fee": fields.Decimal("Cancel Fee"),
        "driver_fare_per_km": fields.Decimal("Driver Fare Per Km Per Ton",scale=3),
        "driver_fare_per_ton": fields.Decimal("Driver Fare Per Ton",scale=3),
        "driver_min_fare": fields.Decimal("Driver Min. Fare"),
        "driver_cancel_fee": fields.Decimal("Driver Cancel Fee"),
    }
    _order="pricelist_id.name,truck_type_id.name,max_weight DESC,min_distance"

    def name_get(self,ids,**kw):
        res=[]
        for obj in self.browse(ids):
            res.append((obj.id,"R-%s"%obj.id))
        return res

Price.register()

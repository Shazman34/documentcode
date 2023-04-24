from netforce.model import Model,fields,get_model
import time

class TruckType(Model):
    _name="l2g.truck.type"
    _string="Truck Type"
    _fields={
        "name": fields.Char("Type Name",required=True),
        "code": fields.Char("Code"),
        "max_width": fields.Decimal("Max Width (ft)"),
        "max_height": fields.Decimal("Max Height (ft)"),
        "max_length": fields.Decimal("Max Length (ft)"),
        "max_weight": fields.Decimal("Max Weight (tons)"),
        "max_weight2": fields.Decimal("Max Weight2 (tons)"),
        "sequence": fields.Integer("Sequence"),
        "base_fare": fields.Decimal("Base Fare"),
        "fare_per_min": fields.Decimal("Fare Per Minute"),
        "fare_per_km": fields.Decimal("Fare Per Km"),
        "min_fare": fields.Decimal("Minimum Fare"),
        "image": fields.File("Image"),
        "image_big": fields.File("Image (Bigger)"),
        "description": fields.Text("Description"),
        "type": fields.Selection([["lorry_crane","Lorry Crane"],["cargo","Cargo"],["platform","Platform"],["low_loader","Low Loader"]],"Type"),
        "prices": fields.One2Many("l2g.price","truck_type_id","Prices"),
        "weight_ranges": fields.One2Many("l2g.weight.range","truck_type_id","Weight Ranges"),
        "active": fields.Boolean("Active"),
        "exclude_from_regions": fields.Many2Many("l2g.province","Exclude Pickup Regions"),
        "min_weights": fields.One2Many("l2g.min.weight","truck_type_id","Min Weights"),
        "parent_id": fields.Many2One("l2g.truck.type","Parent"),
        "children": fields.One2Many("l2g.truck.type","parent_id","Children"),
    }
    _order="sequence"
    _defaults={
        "active": True,
    }

TruckType.register()

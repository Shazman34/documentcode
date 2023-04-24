from netforce.model import Model,fields,get_model
import time

class Truck(Model):
    _name="l2g.truck"
    _string="Truck"
    _name_field="plate_no"
    _fields={
        "plate_no": fields.Char("License Plate No.",required=True,search=True),
        "width": fields.Decimal("Width (ft)"),
        "height": fields.Decimal("Height (ft)"),
        "length": fields.Decimal("Length (ft)"),
        "max_weight": fields.Decimal("Max Weight (tons)"),
        "transporter_id": fields.Many2One("l2g.transporter","Transporter"),
        "driver_id": fields.Many2One("l2g.driver","Driver"),
        "register_date": fields.Date("Register Date",required=True),
        "jobs": fields.One2Many("l2g.job","truck_id","Jobs"),
        "truck_type_id": fields.Many2One("l2g.truck.type","Truck Type",search=True,required=True),
        "coords": fields.Char("Coordinates"),
    }
    _defaults={
        "register_date": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    _order="register_date desc,id desc"

Truck.register()

from netforce.model import Model,fields,get_model
import time

class Transporter(Model):
    _name="l2g.transporter"
    _string="Transporter"
    _fields={
        "name": fields.Char("Transporter Name",required=True),
        "drivers": fields.One2Many("l2g.driver","transporter_id","Drivers"),
        "num_drivers": fields.Integer("# Drivers",function="get_num_drivers"),
        "balance": fields.Decimal("Wallet Balance",function="get_balance"),
        "remarks": fields.Text("Remarks #1"),
        "remarks2": fields.Text("Remarks #2"),
        "contact_id": fields.Many2One("contact","Contact"),
    }
    _order="name"

    def get_num_drivers(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            vals[obj.id]=len(obj.drivers)
        return vals

    def get_balance(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            contact=obj.contact_id
            if contact and contact.track_id:
                bal=contact.track_id.balance
            else:
                bal=0
            vals[obj.id]=bal
        return vals

    def copy_to_contact(self,ids,context={}):
        for obj in self.browse(ids):
            if not obj.contact_id:
                vals={
                    "type": "org",
                    "name": obj.name,
                }
                contact_id=get_model("contact").create(vals)
                obj.write({"contact_id": contact_id})

Transporter.register()

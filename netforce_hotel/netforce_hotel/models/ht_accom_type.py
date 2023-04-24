from netforce.model import Model,fields,get_model
import time

class AccomType(Model):
    _name="ht.accom.type"
    _string="Accomodation Type"
    _fields={
        "sequence": fields.Integer("Sequence"),
        "name": fields.Char("Name",required=True,search=True),
        "code": fields.Char("Code",search=True),
        "num_units": fields.Integer("Number of units",function="get_num_units"),
        "max_persons": fields.Integer("Maximum Occupancy"),
        "description": fields.Text("Description"),
        "amenities": fields.Many2Many("ht.amenity","Amenities"),
        "images": fields.One2Many("image","related_id","Images"),
        "accoms": fields.One2Many("ht.accom","accom_type_id","Accomodations"),
        "product_id": fields.Many2One("product","Product"),
    }
    _order="sequence,name"

    def get_num_units(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            vals[obj.id]=len(obj.accoms)
        return vals

AccomType.register()

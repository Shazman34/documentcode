from netforce.model import Model,fields,get_model
import time

class Accom(Model):
    _name="ht.accom"
    _string="Accomodation"
    _fields={
        "name": fields.Char("Name",required=True,search=True),
        "accom_type_id": fields.Many2One("ht.accom.type","Type",required=True,search=True),
        "sequence": fields.Integer("Sequence"),
    }
    _order="accom_type_id.sequence,accom_type_id.name,sequence,name"

Accom.register()

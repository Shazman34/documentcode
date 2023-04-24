from netforce.model import Model,fields,get_model
from netforce import access

class PosTable(Model):
    _name="pos.table"
    _string="Table"
    _fields={
        "number": fields.Char("Table Number",required=True),
        "name": fields.Char("Table Name",required=True),
        "carts": fields.One2Many("ecom2.cart","pos_table_id","Carts"),
    }
    _order="name"

PosTable.register()

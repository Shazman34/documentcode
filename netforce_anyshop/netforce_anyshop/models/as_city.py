from netforce.model import Model,fields,get_model

class City(Model):
    _name="as.city"
    _string="City"
    _fields={
        "name": fields.Char("City Name",required=True,search=True),
        "region_id": fields.Many2One("as.region","Region",required=True,search=True,on_delete="cascade"),
    }
    _order="name"

City.register()

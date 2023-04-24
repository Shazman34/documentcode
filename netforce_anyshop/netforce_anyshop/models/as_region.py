from netforce.model import Model,fields,get_model

class Region(Model):
    _name="as.region"
    _string="Region"
    _fields={
        "name": fields.Char("Region Name",required=True,search=True),
        "country_id": fields.Many2One("as.country","Country",required=True,search=True,on_delete="cascade"),
        "cities": fields.One2Many("as.city","region_id","Cities"),
    }
    _order="name"

Region.register()

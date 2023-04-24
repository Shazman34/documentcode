from netforce.model import Model,fields,get_model

class Country(Model):
    _name="as.country"
    _string="Country"
    _fields={
        "name": fields.Char("Country Name",required=True,search=True),
        "regions": fields.One2Many("as.region","country_id","Regions"),
    }
    _order="name"

Country.register()

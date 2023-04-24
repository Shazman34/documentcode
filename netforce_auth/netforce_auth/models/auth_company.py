from netforce.model import Model,fields,get_model
from netforce import database
from netforce import utils
from netforce import access

class Company(Model):
    _name="auth.company"
    _string="Company"
    _name_field="name"
    _fields={
        "name": fields.Char("Company Name",required=True),
        "domain": fields.Char("Domain (.netforce.com)",required=True),
    }

Company.register()

from netforce.model import Model,fields,get_model
import time

class Company(Model):
    _name="aln.company"
    _string="Company"
    _audit_log=True
    _fields={
        "name": fields.Char("Company Name"),
        "page_name": fields.Char("Page Name"),
        "phone": fields.Char("Phone"),
        "fax": fields.Char("Fax"),
        "street": fields.Char("Street"),
        "building": fields.Char("Building"),
        "city": fields.Char("City"),
        "state": fields.Char("State"),
        "postal_code": fields.Char("Postal Code"),
        "country_id": fields.Many2One("country","Country"),
        "about": fields.Text("About"),
        "linkedin_url": fields.Char("LinkedIn URL"),
        "industries": fields.Many2Many("aln.industry","Industries"),
    }

Company.register()

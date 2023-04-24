from netforce.model import Model,fields,get_model
import time

class Firm(Model):
    _name="aln.firm"
    _string="Law Firm"
    _audit_log=True
    _fields={
        "logo": fields.File("Logo"),
        "name": fields.Char("Name"),
        "full_name": fields.Char("Full Legal Name"),
        "business_idno": fields.Char("ACRA / Business ID"),
        "page_name": fields.Char("Page Name"),
        "email": fields.Char("Email Address"),
        "phone": fields.Char("Phone"),
        "fax": fields.Char("Fax"),
        "street": fields.Char("Street"),
        "building": fields.Char("Building"),
        "city": fields.Char("City"),
        "state": fields.Char("State"),
        "postal_code": fields.Char("Postal Code"),
        "country_id": fields.Many2One("country","Country"),
        "op_countries": fields.Many2Many("country","Operating Countries"),
        "website": fields.Char("Website URL"),
        "about": fields.Text("About"),
        "size": fields.Integer("Size"),
        "year_inc": fields.Integer("Year Incorporated"),
        "languages_spoken": fields.Many2Many("language","Languages Spoken"),
        "languages_written": fields.Many2Many("language","Languages Written"),
        "practice_areas": fields.Many2Many("aln.practice.area","Practice Areas"),
        "industries": fields.Many2Many("aln.industry","Industries"),
        "max_practice_areas": fields.Integer("Max Pratice Areas"),
        "paypal_email": fields.Char("Paypal Email"),
        "lawyers": fields.One2Many("aln.lawyer","firm_id","Lawyers"),
        "quick_contracts": fields.Boolean("Quick Contracts"),
        "qctr_categs": fields.Many2Many("aln.qctr.categ","Quick Contract Categories"),
        "qctr_lawyer_id": fields.Many2One("aln.lawyer","Quick Contracts Lawyer"),
        "prices": fields.One2Many("aln.price","firm_id","Prices"),
    }

Firm.register()

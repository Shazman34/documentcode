from netforce.model import Model,fields,get_model
import time

class Counsel(Model):
    _name="aln.counsel"
    _string="Counsel"
    _audit_log=True
    _fields={
        "first_name": fields.Char("First Name"),
        "last_name": fields.Char("Last Name"),
        "email": fields.Char("Email"),
        "designation": fields.Char("Designation"),
        "phone": fields.Char("Phone",search=True),
        "qc_phone": fields.Char("QC Phone",search=True),
        "country_id": fields.Many2One("country","Country",search=True),
        "profile_picture": fields.File("Profile Picture"),
        "page_name": fields.Char("Page Name"),
        "gender": fields.Selection([["M","Male"],["F","Female"]],"Gender"),
        "linkedin_url": fields.Char("LinkedIn URL"),
        "languages_spoken": fields.Many2Many("language","Languages Spoken"),
        "languages_written": fields.Many2Many("language","Languages Written"),
        "practice_areas": fields.Many2Many("aln.practice.area","Practice Areas"),
        "industries": fields.Many2Many("aln.industry","Industries"),
        "company_id": fields.Many2One("aln.company","Company"),
        "users": fields.One2Many("base.user","aln_counsel_id","Users"),
    }

Counsel.register()

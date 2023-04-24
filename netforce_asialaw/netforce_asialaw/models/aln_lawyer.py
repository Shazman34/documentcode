from netforce.model import Model,fields,get_model
import time

class Lawyer(Model):
    _name="aln.lawyer"
    _string="Lawyer"
    _audit_log=True
    _name_field="page_name"
    _fields={
        "first_name": fields.Char("First Name"),
        "last_name": fields.Char("Last Name"),
        "email": fields.Char("Email"),
        "profile_picture": fields.File("Profile Picture"),
        "page_name": fields.Char("Page Name",search=True),
        "gender": fields.Selection([["M","Male"],["F","Female"]],"Gender",search=True),
        "phone": fields.Char("Phone",search=True),
        "qc_phone": fields.Char("QC Phone",search=True),
        "is_lawyer": fields.Boolean("Is Lawyer"),
        "is_counsel": fields.Boolean("Is Counsel"),
        "fax": fields.Char("Fax"),
        "street": fields.Char("Street"),
        "building": fields.Char("Building"),
        "city": fields.Char("City"),
        "state": fields.Char("State"),
        "postal_code": fields.Char("Postal Code"),
        "country_id": fields.Many2One("country","Country",search=True),
        "designation": fields.Char("Designation"),
        "about": fields.Text("About"),
        "linkedin_url": fields.Char("LinkedIn URL"),
        "education": fields.Text("Education"),
        "affiliation": fields.Text("Affiliation and Awards"),
        "certification": fields.Text("Certification"),
        "prev_appoint": fields.Text("Previous Appointments"),
        "prof_idno": fields.Text("Professional ID"),
        "year_bar": fields.Integer("Year First Admitted to Bar"),
        "jurisdiction": fields.Many2Many("country","Jurisdiction"),
        "languages_spoken": fields.Many2Many("language","Languages Spoken"),
        "languages_written": fields.Many2Many("language","Languages Written"),
        "practice_areas": fields.Many2Many("aln.practice.area","Practice Areas"),
        "industries": fields.Many2Many("aln.industry","Industries"),
        "avg_rate": fields.Decimal("Average Rate (Per Hour)"),
        "avg_rate_currency_id": fields.Many2One("currency","Average Rate Currency"),
        "max_practice_areas": fields.Integer("Max Pratice Areas"),
        "firm_id": fields.Many2One("aln.firm","Law Firm"),
        "company_id": fields.Many2One("aln.company","Company"),
        "users": fields.One2Many("base.user","aln_lawyer_id","Users"),
        "paypal_email": fields.Char("Paypal Email"),
        "probono": fields.Boolean("Pro Bono"),
        "pb_quick_consult": fields.Boolean("Pro Bono Quick Consult"),
        "quick_consult": fields.Boolean("Quick Consult"),
        "quick_consult_plus": fields.Boolean("Quick Consult Plus"),
        "quick_contracts": fields.Boolean("Quick Contracts"),
        "qc_categs": fields.Many2Many("aln.qc.categ","Quick Consult Categories"),
        "pb_categs": fields.Many2Many("aln.pb.categ","Probono Categories"),
        "pb_qc_categs": fields.Many2Many("aln.pb.categ","Probono Quick Consult Categories"),
        "qcp_categs": fields.Many2Many("aln.qc.categ","Quick Consult Plus Categories"),
        "feedback": fields.One2Many("aln.feedback","lawyer_id","Feedback"),
        "remarks": fields.Text("Remarks"),
        "picture": fields.File("Picture"),
    }
    _defaults={
        "type": "lawyer",
    }

Lawyer.register()

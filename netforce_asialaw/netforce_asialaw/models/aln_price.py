from netforce.model import Model,fields,get_model
import time

class Price(Model):
    _name="aln.price"
    _string="Price"
    _audit_log=True
    _fields={
        "firm_id": fields.Many2One("aln.firm","Law Firm"),
        "qctr_categ_id": fields.Many2One("aln.qctr.categ","Quick Contracts Category"),
        "credits": fields.Integer("Credits"),
    }

Price.register()

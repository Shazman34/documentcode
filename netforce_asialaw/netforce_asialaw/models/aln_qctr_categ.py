from netforce.model import Model,fields,get_model
import time

class Categ(Model):
    _name="aln.qctr.categ"
    _string="Quick Contract Category"
    _audit_log=True
    _fields={
        "name": fields.Char("Name"),
        "parent_id": fields.Many2One("aln.qc.categ","Parent Category"),
        "prices": fields.One2Many("aln.price","qctr_categ_id","Prices"),
    }
    _order="name"

Categ.register()

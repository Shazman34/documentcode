from netforce.model import Model,fields,get_model
import time

class Categ(Model):
    _name="aln.qc.categ"
    _string="Quick Consult Category"
    _audit_log=True
    _fields={
        "name": fields.Char("Name"),
        "parent_id": fields.Many2One("aln.qc.categ","Parent Category"),
        "short_desc": fields.Text("Short Description"),
        "examples": fields.Text("Examples"),
        "long_desc": fields.Text("Long Description"),
        "image": fields.File("Image"),
    }
    _order="name"

Categ.register()

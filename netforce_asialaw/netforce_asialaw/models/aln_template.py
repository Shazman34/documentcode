from netforce.model import Model,fields,get_model
import time

class Template(Model):
    _name="aln.template"
    _string="Document Template"
    _audit_log=True
    _fields={
        "date": fields.Date("Date",required=True,search=True),
        "doc_type_id": fields.Many2One("aln.doc.type","Document Type"),
        "name": fields.Char("Name"),
        "file": fields.File("Document File"),
    }
    _order="date desc,id desc"
    _defaults={
        "date": lambda *a: time.strftime("%Y-%m-%d"),
        "state": "requested",
    }

Template.register()

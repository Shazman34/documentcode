from netforce.model import Model,fields,get_model
import time

class Document(Model):
    _name="aln.doc"
    _string="Document"
    _audit_log=True
    _fields={
        "date": fields.Date("Date",required=True,search=True),
        "client_id": fields.Many2One("aln.client","Client",required=True,search=True),
        "job_id": fields.Many2One("aln.job","Job",search=True),
        "task_id": fields.Many2One("aln.task","Task",search=True),
        "doc_type_id": fields.Many2One("aln.doc.type","Document Type"),
        "file": fields.File("Document File"),
        "logs": fields.One2Many("log","related_id","Audit Log"),
        "state": fields.Selection([["upload_request","Upload Request"],["sign_requested","Signature Requested"],["done","Completed"]],"Status",required=True,search=True),
    }
    _order="date desc,id desc"
    _defaults={
        "date": lambda *a: time.strftime("%Y-%m-%d"),
        "state": "requested",
    }

Document.register()

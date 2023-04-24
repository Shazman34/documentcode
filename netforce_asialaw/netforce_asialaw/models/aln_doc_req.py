from netforce.model import Model,fields,get_model
import time

class DocReq(Model):
    _name="aln.doc.req"
    _string="Document Request"
    _fields={
        "date": fields.Date("Date",required=True),
        "client_id": fields.Many2One("aln.client","Client",required=True),
        "job_id": fields.Many2One("aln.job","Job"),
        "doc_type_id": fields.Many2One("aln.doc.type","Document Type",required=True),
    }
    _defaults={
        "date": lambda *a: time.strftime("%Y-%m-%d"),
    }

DocReq.register()

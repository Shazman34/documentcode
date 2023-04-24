from netforce.model import Model,fields,get_model
import time

class Article(Model):
    _name="aln.article"
    _string="Article"
    _audit_log=True
    _fields={
        "date": fields.Date("Date Added",required=True,search=True),
        "lawyer_id": fields.Many2One("aln.lawyer","Lawyer",required=True,search=True),
        "state": fields.Selection([["draft","Draft"],["submitted","Submitted"],["in_review","In Review"],["published","Published"],["rejected","Rejected"]],"Status",required=True,search=True),
        "remarks": fields.Text("Remarks"), 
        "publish_url": fields.Char("Published URL"),
        "body": fields.Text("Body"),
        "file": fields.File("File"),
    }
    _order="date desc,id desc"
    _defaults={
        "date": lambda *a: time.strftime("%Y-%m-%d"),
        "state": "draft",
    }

Article.register()

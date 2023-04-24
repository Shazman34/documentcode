from netforce.model import Model,fields,get_model
import time

class Access(Model):
    _name="aln.user.access"
    _string="User Access"
    _audit_log=True
    _fields={
        "job_id": fields.Many2One("aln.job","Case"),
        "user_id": fields.Many2One("base.user","User"),
        "access_type": fields.Selection([["edit","Edit"],["view","View Only"]],"Access Type"),
    }

Access.register()

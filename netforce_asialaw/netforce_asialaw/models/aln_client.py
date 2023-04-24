from netforce.model import Model,fields,get_model
from netforce import access
import time

class Client(Model):
    _name="aln.client"
    _string="Client"
    _audit_log=True
    _name_field="email"
    _fields={
        "first_name": fields.Char("First Name",required=True,search=True),
        "last_name": fields.Char("Last Name",required=True,search=True),
        "email": fields.Char("Email",required=True,search=True),
        "phone": fields.Char("Phone",required=True,search=True),
        "country_id": fields.Many2One("country","Country"),
        "date": fields.Date("Added Date",required=True,search=True),
        "address": fields.Text("Address",search=True),
        "level": fields.Selection([["1","Main Client"],["2","Sub Client"]],"Level"),
        "jobs": fields.One2Many("aln.job","client_id","Jobs"),
        "meeting_reqs": fields.One2Many("aln.meeting.req","client_id","Meeting Requests"),
        "meetings": fields.One2Many("aln.meeting","client_id","Meetings"),
        "document_reqs": fields.One2Many("aln.doc.req","client_id","Document Requests"),
        "documents": fields.One2Many("aln.doc","client_id","Documents"),
        "bill_reqs": fields.One2Many("aln.bill.req","client_id","Billing Requests"),
        "payments": fields.One2Many("aln.payment","client_id","Payments"),
        "logs": fields.One2Many("log","related_id","Audit Log"),
        "type": fields.Selection([["person","Person"],["org","Organization"]],"Client Type"),
        "users": fields.One2Many("base.user","aln_client_id","Users"),
        "feedback": fields.One2Many("aln.feedback","client_id","Feedback"),
        "active": fields.Boolean("Active"),
    }
    _defaults={
        "active": True,
    }

    def _get_number(self, context={}):
        seq_id = get_model("sequence").find_sequence(name="ALN Client",context=context)
        if not seq_id:
            raise Exception("Missing number sequence for jobs")
        while 1:
            num = get_model("sequence").get_next_number(seq_id, context=context)
            if not num:
                return None
            user_id = access.get_active_user()
            access.set_active_user(1)
            res = self.search([["code", "=", num]])
            access.set_active_user(user_id)
            if not res:
                return num
            get_model("sequence").increment_number(seq_id, context=context)

    _defaults={
        "date": lambda *a: time.strftime("%Y-%m-%d"),
        "code": _get_number,
    }

Client.register()

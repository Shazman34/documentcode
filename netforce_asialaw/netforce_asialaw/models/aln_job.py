from netforce.model import Model,fields,get_model
from netforce import access
from datetime import *
import time

class Job(Model):
    _name="aln.job"
    _string="Case"
    _name_field="number"
    _audit_log=True
    _fields={
        "number": fields.Char("Case File #",required=True,search=True),
        "date": fields.Date("Date Date",required=True,search=True),
        "client_id": fields.Many2One("aln.client","Client",required=True,search=True),
        "lawyer_id": fields.Many2One("aln.lawyer","Lawyer",required=True,search=True),
        "job_type_id": fields.Many2One("aln.job.type","Case Type",search=True),
        "state": fields.Selection([["inquiry","Inquiry"],["wait_accept","Awaiting Acceptance"],["in_progress","In Progress"],["done","Completed"],["archived","Archived"],["canceled","Canceled"]],"Status",search=True),
        "tasks": fields.One2Many("aln.task","job_id","Tasks"),
        "meetings": fields.One2Many("aln.meeting","job_id","Meetings"),
        "documents": fields.One2Many("aln.doc","job_id","Documents"),
        "bill_reqs": fields.One2Many("aln.bill.req","job_id","Billing Requests"),
        "payments": fields.One2Many("aln.payment","job_id","Payments"),
        "logs": fields.One2Many("log","related_id","Audit Log"),
        "origin": fields.Selection([["qc","Quick Consult"],["qc_plus","Quick Consult Plus"],["counsel_consult","Counsel Consult"],["qctr","Quick Contracts"],["other","Other"]],"Origin"),
        "user_id": fields.Many2One("base.user","Created By"),
        "user_access": fields.One2Many("aln.user.access","job_id","User Access"),
        "feedback": fields.One2Many("aln.feedback","job_id","Feedback"),
        "qc_categ_id": fields.Many2One("aln.qc.categ","QC Category"),
        "facts": fields.Text("Case Facts"),
        "questions": fields.Text("Questions"),
        "parties": fields.Text("Involved Parties"),
        "call_times": fields.Text("Call Times"),
        "qc_call_time": fields.DateTime("QC Call Time"),
        "is_paid": fields.Boolean("Is Paid"),
        "qc_state": fields.Selection([["wait_payment","Awaiting Payment"],["wait_accept","Awaiting Acceptance"],["wait_confirm_time","Awaiting Time Confirmation"],["ready_call","Ready To Call"],["done","Completed"],["declined","Declined"]],"QC Status"),
        "decline_reason_id": fields.Many2One("reason.code","Decline Reason"),
        "qc_call_reminders_sent": fields.Boolean("QC Call Reminders Sent"),
    }

    def _get_number(self, context={}):
        seq_id = get_model("sequence").find_sequence(name="ALN Job",context=context)
        if not seq_id:
            raise Exception("Missing number sequence for jobs")
        while 1:
            num = get_model("sequence").get_next_number(seq_id, context=context)
            if not num:
                return None
            user_id = access.get_active_user()
            access.set_active_user(1)
            res = self.search([["number", "=", num]])
            access.set_active_user(user_id)
            if not res:
                return num
            get_model("sequence").increment_number(seq_id, context=context)

    def qc_send_call_reminders(self,minutes_remain=5,context={}):
        max_t=datetime.now()-timedelta(seconds=minutes_remain*60)
        for job in get_model("aln.job").search([["qc_state","=","ready_call"],["qc_call_reminders_sent","!=",True],["qc_call_time","<=",max_t]]):
            job.trigger("call_reminder")
            job.write({"qc_call_reminders_sent":True})

    _defaults={
        "date": lambda *a: time.strftime("%Y-%m-%d"),
        "state": "pending",
        "number": _get_number,
    }

Job.register()

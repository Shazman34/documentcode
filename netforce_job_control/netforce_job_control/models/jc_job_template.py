from netforce.model import Model, fields, get_model
import time
import datetime

class JobTemplate(Model):
    _name="jc.job.template"
    _string="Job Template"
    _name_field="name"
    _fields={
        "name": fields.Char("Template Name",required=True,search=True),
        "service_id": fields.Many2One("jc.service","Service"),  # XXX: deprecated
        "product_id": fields.Many2One("product","Product",condition=[["type","=","service"]]),
        "job_name": fields.Char("Job Name",required=True,search=True),
        "description": fields.Text("Description"),
        "due_date": fields.Char("Due Date"),
        "comments": fields.One2Many("message","related_id","Comments"),
        "task_templates": fields.One2Many("jc.task.template","job_template_id","Task Templates"),
        "auto_complete": fields.Boolean("Mark as completed when all tasks completed"),
        "periodicity": fields.Selection([["ad_hoc","Ad hoc"],["month","Monthly"],["year","Yearly"]],"Periodicity"),
        "assign_from_client": fields.Boolean("Assign from client"),
        #"required_docs": fields.One2Many("required.doc","related_id","Required Documents"),
        "update_due_date": fields.Boolean("Update job due date from tasks"),
        "est_hours": fields.Decimal("Est. Hours"),
        "active": fields.Boolean("Active"),
    }
    _order="name"
    _defaults={
        "active": True,
    }

    def copy(self,ids,context={}):
        obj=self.browse(ids)[0]
        vals={
            "name": obj.name+" (Copy)",
            "service_id": obj.service_id.id,
            "job_name": obj.job_name,
            "description": obj.description,
            "due_date": obj.due_date,
            "auto_complete": obj.auto_complete,
            "create_when": obj.create_when,
            "task_templates": [],
        }
        for task in obj.task_templates:
            task_vals={
                "name": task.name,
                "description": task.description,
                "deadline": task.deadline,
                "user_id": task.user_id.id,
                "sequence": task.sequence,
                "wait_for": task.wait_for,
            }
            vals["task_templates"].append(("create",task_vals))
        new_id=get_model("job.template").create(vals)
        return {
            "next": {
                "name": "job_template",
                "mode": "form",
                "active_id": new_id,
            },
            "flash": "Job template created",
        }

    def create_job(self,ids,context={}):
        contact_id=context["contact_id"]
        obj=self.browse(ids)[0]
        vals={
            "template_id": obj.id,
            "contact_id": contact_id,
            "service_id": obj.service_id.id,
            "name": obj.job_name,
            "description": obj.description,
        }
        if obj.due_date:
            if obj.due_date.startswith("+"):
                days=int(obj.due_date[1:])
                d=(datetime.date.today()+datetime.timedelta(days=days)).strftime("%Y-%m-%d")
            else:
                d=time.strftime("%Y-%m-")+obj.due_date
            vals["due_date"]=d
        ctx={
            "categ_id": obj.service_id.categ_id.id,
        }
        job_id=get_model("job").create(vals,context=ctx)
        return job_id

JobTemplate.register()

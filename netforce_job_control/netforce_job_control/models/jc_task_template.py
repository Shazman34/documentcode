from netforce.model import Model, fields, get_model
import time
import datetime

class TaskTemplate(Model):
    _name="jc.task.template"
    _string="Task Template"
    _fields={
        "job_template_id": fields.Many2One("jc.job.template","Job Template",required=True,on_delete="cascade"),
        "name": fields.Char("Task Name",required=True),
        "description": fields.Text("Description"),
        "deadline": fields.Char("Deadline"),
        "user_id": fields.Many2One("base.user","Assign To",search=True),
        "assign_from_job": fields.Boolean("Assign from job"),
        "sequence": fields.Integer("Sequence"),
        "wait_for": fields.Char("Wait For"),
        "comments": fields.One2Many("message","related_id","Comments"),
        "est_hours": fields.Decimal("Est. Hours"),
    }
    _order="sequence,name"

TaskTemplate.register()

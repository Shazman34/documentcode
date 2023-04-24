from netforce.model import Model, fields, get_model
import time

class Project(Model):
    _name="jc.project"
    _string="Project"
    _audit_log=True
    _fields={
        "name": fields.Char("Project Name",required=True,search=True),
        "contact_id": fields.Many2One("contact","Contact",required=True,search=True),
        "start_date": fields.Date("Start Date",required=True),
        "end_date": fields.Date("End Date"),
        "product_id": fields.Many2One("product","Product"),
        "comments": fields.One2Many("message","related_id","Comments"),
        "documents": fields.One2Many("document","related_id","Documents"),
        "state": fields.Selection([["in_progress","In Progress"],["done","Completed"],["canceled","Canceled"]],"Status",required=True),
        "jobs": fields.One2Many("job","project_id","Jobs"),
        "tasks": fields.One2Many("task","project_id","Tasks"),
        "work_time": fields.One2Many("work.time","job_id","Work Time"),
        "description": fields.Text("Description"),
    }
    _order="start_date"

    _defaults={
        "start_date": lambda *a: time.strftime("%Y-%m-%d"),
        "state": "in_progress",
    }

Project.register()

from netforce.model import Model,fields,get_model
import time

class Course(Model):
    _name="ed.course"
    _string="Course"
    _fields={
        "name": fields.Char("Course Name",required=True,search=True),
        "description": fields.Text("Description",search=True),
        "period_id": fields.Many2One("ed.period","Period",required=True,search=True),
        "group_id": fields.Many2One("ed.group","Group",required=True),
    }
    _defaults={
    }

Course.register()

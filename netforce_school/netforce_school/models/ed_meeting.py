from netforce.model import Model,fields,get_model
import time

class Meeting(Model):
    _name="ed.meeting"
    _string="Appointment"
    _fields={
        "date": fields.Date("Date",required=True,search=True),
        "time": fields.Char("Time",required=True),
        "teacher_id": fields.Many2One("ed.teacher","Teacher",required=True,search=True),
        "course_id": fields.Many2One("ed.course","Course",search=True),
        "student_id": fields.Many2One("ed.student","Student",required=True,search=True),
        "state": fields.Selection([["requested","Requested"],["accepted","Accepted"],["done","Completed"],["canceled","Canceled"]],"Status",required=True,search=True),
        "notes": fields.Text("Notes",search=True),
    }
    _defaults={
        "date": lambda *a: time.strftime("%Y-%m-%d"),
        "state": "requested",
    }

Meeting.register()

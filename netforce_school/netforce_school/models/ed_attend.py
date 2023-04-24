from netforce.model import Model,fields,get_model
import time

class Attend(Model):
    _name="ed.attend"
    _string="Attendance"
    _fields={
        "date": fields.Date("Date",required=True),
        "student_id": fields.Many2One("ed.student","Student",required=True),
        "state": fields.Selection([["present","Present"],["absent","Absent"],["late","Late"]],"Status",required=True),
        "course_id": fields.Many2One("ed.course","Course"),
        "teacher_id": fields.Many2One("ed.teacher","Teacher"),
    }
    _defaults={
        "date": lambda *a: time.strftime("%Y-%m-%d"),
        "state": "present",
    }

Attend.register()

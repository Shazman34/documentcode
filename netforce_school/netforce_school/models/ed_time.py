from netforce.model import Model,fields,get_model
import time

class Time(Model):
    _name="ed.time"
    _string="Time Slot"
    _fields={
        "date": fields.Date("Date",required=True,search=True),
        "time_from": fields.Char("Time From",required=True),
        "time_to": fields.Char("Time To",required=True),
        "title": fields.Char("Title",required=True,search=True),
        "group_id": fields.Many2One("ed.group","Group",required=True,search=True),
        "course_id": fields.Many2One("ed.course","Course"),
    }
    _defaults={
        "date": lambda *a: time.strftime("%Y-%m-%d"),
    }

Time.register()

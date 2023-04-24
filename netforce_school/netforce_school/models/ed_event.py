from netforce.model import Model,fields,get_model
import time

class Event(Model):
    _name="ed.event"
    _string="Event"
    _fields={
        "date": fields.Date("Date",required=True,search=True),
        "time_from": fields.Char("From Time"),
        "time_to": fields.Char("To Time"),
        "title": fields.Char("Title",required=True,search=True),
        "description": fields.Text("Description"),
        "group_id": fields.Many2One("ed.group","Group",search=True),
    }
    _defaults={
        "date": lambda *a: time.strftime("%Y-%m-%d"),
    }

Event.register()

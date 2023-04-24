from netforce.model import Model,fields,get_model
import time

class Media(Model):
    _name="ed.media"
    _string="Media"
    _fields={
        "date": fields.Date("Date",required=True,search=True),
        "title": fields.Char("Title"),
        "file": fields.File("File"),
        "group_id": fields.Many2One("ed.group","Group"),
        "event_id": fields.Many2One("ed.event","Event"),
    }
    _defaults={
        "date": lambda *a: time.strftime("%Y-%m-%d"),
    }

Media.register()

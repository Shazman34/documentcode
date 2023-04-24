from netforce.model import Model,fields,get_model
import time

class Notice(Model):
    _name="ed.notice"
    _string="Notice"
    _fields={
        "date": fields.Date("Date",required=True,search=True),
        "title": fields.Char("Title",required=True,search=True),
        "message": fields.Text("Message",search=True),
        "group_id": fields.Many2One("ed.group","Group",search=True),
    }
    _defaults={
        "date": lambda *a: time.strftime("%Y-%m-%d"),
    }

Notice.register()

from netforce.model import Model,fields,get_model

class WorkPeriod(Model):
    _name="nd.work.period"
    _string="Delivery Period"
    _fields={
        "name": fields.Char("Work Period Name",required=True,search=True),
        "time_from": fields.Char("From Time"),
        "time_to": fields.Char("To Time"),
    }
    _order="time_from"

WorkPeriod.register()

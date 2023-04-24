from netforce.model import Model,fields,get_model

class Option(Model):
    _name="nd.poll.option"
    _string="Poll Option"
    _fields={
        "poll_id": fields.Many2One("nd.poll","Poll",required=True,on_delete="cascade"),
        "name": fields.Char("Answer",required=True),
    }

Option.register()

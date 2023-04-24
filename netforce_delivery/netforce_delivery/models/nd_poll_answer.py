from netforce.model import Model,fields,get_model
import time

class Answer(Model):
    _name="nd.poll.answer"
    _string="Poll Answer"
    _fields={
        "date": fields.DateTime("Date"),
        "poll_id": fields.Many2One("nd.poll","Poll",required=True,on_delete="cascade"),
        "option_id": fields.Many2One("nd.poll.option","Selected Option"),
        "order_id": fields.Many2One("nd.order","Delivery Order"),
    }
    _defaults={
        "date": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
    }

Answer.register()

from netforce.model import Model, fields, get_model
from netforce import access
from datetime import *


class Items(Model):
    _name = "lazada.order.shipping"
    _fields = {
        "order_id": fields.Many2One("lazada.order","Lazada Order"),
        "title": fields.Char("Title"),
        "detail_type": fields.Char("Detail Type"),
        "description": fields.Text("Description"),
        "event_time": fields.Text("Event Time")

    }

Items.register()

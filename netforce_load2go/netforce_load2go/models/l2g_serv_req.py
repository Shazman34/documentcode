from netforce.model import Model,fields,get_model
import time

class Req(Model):
    _name="l2g.serv.req"
    _string="Service Request"
    _fields={
        "number": fields.Char("Number",required=True),
        "date": fields.Char("Date",required=True),
        "state": fields.Selection([["draft","Draft"],["confirmed","Confirmed"]],"Status",required=True),
        "type": fields.Selection([["engine","Engine"]],"Service Type",required=True),
        "eng_pipe": fields.Boolean("Pipe Broken"),
        "eng_part": fields.Boolean("Part Failure"),
    }
    _order="name"
    _defaults={
        "state": "draft",
    }

Req.register()

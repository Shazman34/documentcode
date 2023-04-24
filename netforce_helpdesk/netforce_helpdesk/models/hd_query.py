from netforce.model import Model,fields,get_model
from netforce import access
import time

class Query(Model):
    _name="hd.query"
    _string="Query"
    _fields={
        "time": fields.DateTime("Time",required=True,search=True),
        "query": fields.Char("Query",required=True,search=True),
        "num_results": fields.Integer("Num Results",search=True),
        "ip_addr": fields.Char("IP Address",search=True),
    }
    _order="id desc"
    _defaults={
        "time": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
        "ip_addr": lambda *a: access.get_ip_addr(),
    }

Query.register()   

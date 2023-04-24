from netforce.model import Model, fields, get_model
from netforce.database import get_connection
from datetime import *
import time

class Service(Model):
    _name="jc.service"
    _string="Service"
    _import_field="code" # XXX
    _fields={
        "name": fields.Char("Service Name",required=True),
        "code": fields.Char("Short Code",required=True),
        "categ_id": fields.Many2One("jc.service.categ","Service Category",required=True),
        "group_id": fields.Many2One("user.group","User Group"),
        "active": fields.Boolean("Active"),
        "comments": fields.One2Many("message","related_id","Comments"),
        "task_templates": fields.One2Many("task.template","service_id","Task Templates"),
        "product_id": fields.Many2One("product","Product",condition=[["type","=","service"]]),
    }
    _order="name"
    _defaults={
        "active": True,
    }

Service.register()

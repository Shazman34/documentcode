from netforce.model import Model,fields,get_model
from netforce import access
from netforce import database
from netforce import utils
from datetime import *
import time
from netforce.utils import json_dumps
import requests
from decimal import *
import json

class PriceParam(Model):
    _name="gt.price.param"
    _string="Price Parameter"
    _fields={
        "name": fields.Char("Name",required=True,search=True),
        "value": fields.Decimal("Value"),
        "description": fields.Text("Description",search=True),
        "group_id": fields.Many2One("gt.price.param.group","Group",search=True),
        "group_color": fields.Char("Group Color",function="_get_related",function_context={"path":"group_id.color"}),
        "time_from": fields.Char("Time From"),
        "time_to": fields.Char("Time To"),
        "weekday": fields.Selection([["0","Monday"],["1","Tuesday"],["2","Wednesday"],["3","Thursday"],["4","Friday"],["5","Saturday"],["6","Sunday"]],"Weekday",search=True),
        "sequence": fields.Integer("Sequence"),
    }
    _order="group_id.sequence,name"

    def create(self,vals,**kw):
        new_id=super().create(vals,**kw)
        self.upload_params()
        return new_id

    def write(self,ids,vals,**kw):
        super().write(ids,vals,**kw)
        self.upload_params()

    def get_params(self,context={}):
        params={}
        for obj in self.search_browse([]):
            params[obj.name]=obj.value
        return params

    def upload_params(self,context={}):
        print("upload_params")
        params=self.get_params()
        print("params",params)
        url="http://prices.netforce.com:5555/upload_params"
        data=json.loads(json_dumps(params))
        r=requests.post(url,json=data)
        if r.status_code!=200:
            raise Exception("Failed to upload params: response code %s"%r.status_code)

PriceParam.register()

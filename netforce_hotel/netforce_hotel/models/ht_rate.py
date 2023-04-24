from netforce.model import Model,fields,get_model
from datetime import *
import time

class Rate(Model):
    _name="ht.rate"
    _string="Rate"
    _fields={
        "accom_type_id": fields.Many2One("ht.accom.type","Type",required=True,search=True),
        "sequence": fields.Char("Sequence"),
        "date_from": fields.Date("From Date",search=True),
        "date_to": fields.Date("To Date"),
        "min_los": fields.Integer("Min LOS"),
        "max_los": fields.Integer("Max LOS"),
        "weekday": fields.Selection([["0","Monday"],["1","Tuesday"],["2","Wednesday"],["3","Thursday"],["4","Friday"],["5","Saturday"],["6","Sunday"]],"Weekday",search=True),
        "price": fields.Decimal("Price",required=True),
    }
    _order="accom_type_id.name,sequence,id"

    def get_amount(self,accom_type_id,from_date,to_date,num_guests=None):
        d0=datetime.strptime(from_date,"%Y-%m-%d")
        d1=datetime.strptime(to_date,"%Y-%m-%d")
        num_days=(d1-d0).days
        for obj in self.search_browse([["accom_type_id","=",accom_type_id]]):
            price=obj.price
            return price*num_days

Rate.register()

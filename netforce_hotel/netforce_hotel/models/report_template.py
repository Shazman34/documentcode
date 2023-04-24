from netforce.model import Model,fields,get_model
from datetime import *
from dateutil.relativedelta import *
import time

def get_date_range(date):
    if not date:
        return [None,None]
    if len(date)==10:
        return [None,date]
    if len(date)==7:
        date_from=date+"-01"
        date_to=(datetime.strptime(date_from,"%Y-%m-%d")+relativedelta(day=31)).strftime("%Y-%m-%d")
        return [date_from,date_to]

def get_num_days(date):
    date_from,date_to=get_date_range(date)
    if not date_from:
        date_from=time.strftime("%Y-01-01")
    if not date_to:
        date_to=time.strftime("%Y-%m-%d")
    d0=datetime.strptime(date_from,"%Y-%m-%d")
    d1=datetime.strptime(date_to,"%Y-%m-%d")
    return (d1-d0).days

def get_num_rooms(date=None):
    res=get_model("ht.accom").search([])
    return len(res)

def get_total_room_days(date=None):
    num_rooms=get_num_rooms()
    num_days=get_num_days(date)
    return num_rooms*num_days

def get_avail_room_days(date=None):
    num_rooms=get_num_rooms()
    num_days=get_num_days(date)
    return num_rooms*num_days

def get_occup_room_days(date=None,ota=None):
    date_from,date_to=get_date_range(date)
    if not date_from:
        date_from=time.strftime("%Y-01-01")
    if not date_to:
        date_to=time.strftime("%Y-%m-%d")
    cond=[["to_date",">=",date_from],["from_date","<=",date_to]]
    if ota:
        cond.append(["booking_id.source_id.is_ota","=",True])
    num_days=0
    for obj in get_model("ht.assign").search_browse(cond):
        d0=datetime.strptime(max(date_from,obj.from_date),"%Y-%m-%d")
        d1=datetime.strptime(min(date_to,obj.to_date),"%Y-%m-%d")
        n=(d1-d0).days
        num_days+=n 
    return num_days

def get_occup_room_days_ota(date=None):
    return get_occup_room_days(date,ota=True)

def get_avg_rate(date=None,ota=None):
    date_from,date_to=get_date_range(date)
    if not date_from:
        date_from=time.strftime("%Y-01-01")
    if not date_to:
        date_to=time.strftime("%Y-%m-%d")
    cond=[["to_date",">=",date_from],["from_date","<=",date_to]]
    if ota:
        cond.append(["booking_id.source_id.is_ota","=",True])
    num_days=0
    amount=0
    for obj in get_model("ht.assign").search_browse(cond):
        d0=datetime.strptime(max(date_from,obj.from_date),"%Y-%m-%d")
        d1=datetime.strptime(min(date_to,obj.to_date),"%Y-%m-%d")
        price=obj.amount/obj.num_nights if obj.num_nights else 0
        n=(d1-d0).days
        num_days+=n 
        amount+=n*price
    return amount/num_days if num_days else 0

def get_avg_rate_ota(date=None):
    return get_avg_rate(date,ota=True)

class ReportTemplate(Model):
    _inherit="report.template"

    def get_report_functions(self,context={}):
        res=super().get_report_functions()
        res.update({
            "NUM_ROOMS": get_num_rooms,
            "TOTAL_ROOM_DAYS": get_total_room_days,
            "AVAIL_ROOM_DAYS": get_avail_room_days,
            "OCCUP_ROOM_DAYS": get_occup_room_days,
            "OCCUP_ROOM_DAYS_OTA": get_occup_room_days_ota,
            "AVG_ROOM_RATE": get_avg_rate,
            "AVG_ROOM_RATE_OTA": get_avg_rate_ota,
        })
        return res

ReportTemplate.register()

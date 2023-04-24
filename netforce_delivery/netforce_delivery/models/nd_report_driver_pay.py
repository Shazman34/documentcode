from netforce.model import Model,fields,get_model
from netforce import database
from datetime import *
from dateutil.relativedelta import *
from pprint import pprint

class Report(Model):
    _name="nd.report.driver.pay"
    _fields={
        "date_from": fields.Date("From Date"),
        "date_to": fields.Date("To Date"),
        "driver_id": fields.Many2One("nd.driver","Driver"),
    }
    _defaults = {
        "date_from": lambda *a: date.today().strftime("%Y-%m-01"),
        "date_to": lambda *a: (date.today() + relativedelta(day=31)).strftime("%Y-%m-%d"),
    }

    def get_report_data(self,ids,context={}):
        print("get_report_data",ids)
        obj=self.browse(ids[0])
        cond=[["date",">=",obj.date_from],["date","<=",obj.date_to],["state","=","done"]]
        driver_jobs={}
        for job in get_model("nd.job").search_browse(cond,context=context,order="date,id"):
            driver_jobs.setdefault(job.driver_id.id,[]).append(job)
        driver_ids=list(driver_jobs.keys())
        drivers=[]
        for driver in get_model("nd.driver").browse(driver_ids):
            jobs=driver_jobs[driver.id]
            driver_vals={
                "id": driver.id,
                "name": driver.name,
                "jobs": [],
            }
            for job in jobs:
                job_vals={
                    "id": job.id,
                    "number": job.number,
                    "date": job.date,
                    "amount_due": job.amount_due,
                }
                driver_vals["jobs"].append(job_vals)
            driver_vals["amount_due_total"]=sum(j["amount_due"] or 0 for j in jobs)
            drivers.append(driver_vals)
        drivers.sort(key=lambda d: d["name"])
        data={
            "date_from": obj.date_from,
            "date_to": obj.date_to,
            "drivers": drivers,
        }
        pprint(data)
        return data

Report.register()

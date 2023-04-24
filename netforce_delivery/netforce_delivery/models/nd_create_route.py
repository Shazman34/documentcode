from netforce.model import Model,fields,get_model
import time

class CreateRoute(Model):
    _name="nd.create.route"
    _fields={
        "date": fields.Date("Date",required=True),
    }
    _defaults={
        "date": lambda *a: time.strftime("%Y-%m-%d"),
    }

    def create_routes(self,ids,context={}):
        print("create_routes",ids)

    def create_routes(self,ids,context={}):
        obj=self.browse(ids[0])
        n=0
        for driver in get_model("nd.driver").search_browse([],context=context):
            for rnd in driver.rounds:
                if not rnd.period_id:
                    raise Exception("Missing work period for round %s of driver %s"%(rnd.name,driver.name))
                vals={
                    "delivery_date": obj.date,
                    "driver_id": driver.id,
                    "round_id": rnd.id,
                }
                cond=[["delivery_date","=",vals["delivery_date"]],["driver_id","=",vals["driver_id"]],["round_id","=",vals["round_id"]]]
                res=get_model("nd.route").search(cond,context=context)
                if not res:
                    get_model("nd.route").create(vals,context=context)
                    n+=1
        return {
            "flash": "%s delivery routes created"%n,
            "action": {
                "name": "nd_route",
                "active_tab": 3,
            },
        }

CreateRoute.register()

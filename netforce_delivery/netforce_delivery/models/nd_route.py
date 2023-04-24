from netforce.model import Model,fields,get_model
from netforce import access
from datetime import *
import time
import requests
from pprint import pprint
import math
import json
from .polyline import polyline_decode

class Route(Model):
    _name="nd.route"
    _string="Route"
    _audit_log=True
    _fields={
        "driver_id": fields.Many2One("nd.driver","Driver",required=True,search=True),
        "delivery_date": fields.Date("Delivery Date",required=True,search=True),
        "round_id": fields.Many2One("nd.round","Round",required=True,search=True),
        "state": fields.Selection([["draft","Draft"],["wait_pick","Waiting Pickup"],["in_transit","In Transit"],["done","Completed"]],"Status",required=True,search=True),
        "orders": fields.One2Many("nd.order","route_id","Delivery Orders"),
        "num_orders": fields.Integer("Num Orders",function="get_num_orders"),
        "tasks": fields.One2Many("nd.task","route_id","Tasks"),
        "today": fields.Boolean("Today",store=False,function_search="search_today"),
        "today_p1": fields.Boolean("Today+1",store=False,function_search="search_today_p1"),
        "today_p2": fields.Boolean("Today+2",store=False,function_search="search_today_p2"),
        "est_distance": fields.Decimal("Est. Distance (Km)",readonly=True),
        "est_duration": fields.Decimal("Est. Duration (minutes)",readonly=True),
        "act_duration": fields.Decimal("Act. Duration (minutes)",readonly=True),
        "directions_data": fields.Text("Directions Data"),
        "directions_path": fields.Text("Directions Path"),
        "pickup_address_id": fields.Many2One("address","Pickup Address"),
        "pickup_image": fields.File("Pickup Photo"),
        "require_pickup_image": fields.Boolean("Require Pickup Photo"),
        "return_address_id": fields.Many2One("address","Return Address"),
        "return_image": fields.File("Return Photo"),
        "require_return_image": fields.Boolean("Require Return Photo"),
        "est_pickup_time": fields.Char("Est. Pickup Time",function="_get_related",function_context={"path":"round_id.period_id.time_from"}),
        "est_return_time": fields.Char("Est. Return Time",readonly=True),
        "blind_mode": fields.Boolean("Blind Mode"),
        "amount": fields.Decimal("Pay Amount"), # XXX: deprecated
        "seq_from": fields.Integer("From Sequence",function="_get_related",function_context={"path":"round_id.seq_from"}),
        "seq_to": fields.Integer("To Sequence",function="_get_related",function_context={"path":"round_id.seq_to"}),
        "period_id": fields.Many2One("nd.work.period","Work Period",function="_get_related",function_context={"path":"round_id.period_id"}),
        "filter_order_id": fields.Many2One("nd.order","Filter Order",store=False,function_search="search_filter_order"),
    }
    _order="delivery_date,round_id.period_id.time_from,driver_id.sequence"

    def get_pickup_address(self,context={}):
        settings=get_model("settings").browse(1)
        return settings.delivery_pickup_address_id.id if settings.delivery_pickup_address_id  else None

    _defaults={
        "state": "draft",
        "delivery_date": lambda *a: time.strftime("%Y-%m-%d"),
        "pickup_address_id": get_pickup_address,
    }

    def name_get(self,ids,context={}):
        res=[]
        for obj in self.browse(ids,context=context):
            name="%s-%s-%s"%(obj.driver_id.name,obj.round_id.period_id.name,obj.delivery_date[5:])
            res.append([obj.id,name])
        return res

    def name_search(self,name,condition,*args,context={},**kw):
        ids=self.search(condition,context=context)
        return self.name_get(ids)

    def get_num_orders(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            vals[obj.id]=len(obj.orders)
        return vals

    def view_route_map(self,ids,context={}):
        return {
            "next": {
                "name": "action",
                "action": "ndc_route_map",
                "context": {"active_id":ids[0]},
            }
        }

    def set_in_progress(self,ids,context={}):
        obj=self.browse(ids[0])
        if obj.require_pickup_image and not obj.pickup_image:
            raise Exception("Missing pickup photo")
        obj.write({"state":"in_progress"},context=context)
        for order in obj.orders:
            if order.state=="waiting":
                order.set_in_progress(context=context)

    def set_done(self,ids,context={}):
        obj=self.browse(ids[0])
        #for order in obj.orders:
        #    if order.state not in ("done","error"):
        #        raise Exception("Can not finish route yet because some orders are still in transit")
        obj.write({"state":"done"},context=context)

    def set_waiting(self,ids,context={}):
        obj=self.browse(ids[0],context=context)
        obj.write({"state":"waiting"})

    def set_error(self,ids,context={}):
        obj=self.browse(ids[0],context=context)
        obj.write({"state":"error"})

    def search_today(self,clause,context={}):
        d=datetime.today().strftime("%Y-%m-%d")
        ids=self.search([["delivery_date","=",d]])
        return ["id","in",ids]

    def search_today_p1(self,clause,context={}):
        d=(datetime.today()+timedelta(days=1)).strftime("%Y-%m-%d")
        ids=self.search([["delivery_date","=",d]])
        return ["id","in",ids]

    def search_today_p2(self,clause,context={}):
        d=(datetime.today()+timedelta(days=2)).strftime("%Y-%m-%d")
        ids=self.search([["delivery_date","=",d]])
        return ["id","in",ids]

    def get_directions(self,ids,context={}):
        obj=self.browse(ids[0])
        paddr=obj.pickup_address_id
        if not paddr:
            raise Exception("Missing pickup address")
        if not paddr.coords:
            raise Exception("Missing coordinates for pickup address")
        if not obj.orders:
            raise Exception("Missing customer orders")
        daddr=obj.orders[-1].ship_address_id
        if not daddr:
            raise Exception("Missing shipping address for order %s"%obj.orders[-1].number)
        if not daddr.coords:
            raise Exception("Missing coordinates for address %s"%daddr.street_address)
        waypoints=[]
        for order in obj.orders[:-1]:
            addr=order.ship_address_id
            if not addr:
                raise Exception("Missing shipping address for order %s"%order.number)
            if not addr.coords:
                raise Exception("Missing coordinates for address %s"%addr.street_adress)
            waypoints.append(addr.coords)
        url = 'https://maps.googleapis.com/maps/api/directions/json'
        key = "AIzaSyAnOTbaAFeCz6YM_eIkv_oaHpc-eSsV8Ho"
        params = {
            'origin': paddr.coords,
            "destination": daddr.coords,
            "key": key,
        }
        if waypoints:
            params["waypoints"]="|".join(waypoints)
        print("params:")
        pprint(params)
        r = requests.get(url, params=params, timeout=15)
        res = r.json()
        print("response:")
        pprint(res)
        if res["status"]!="OK":
            raise Exception("Invalid response")
        route=res["routes"][0]
        total_dur=0
        total_dist=0
        t=datetime.strptime(obj.delivery_date+" "+obj.round_id.period_id.time_from+":00","%Y-%m-%d %H:%M:%S")
        settings=get_model("nd.settings").browse(1)
        t+=timedelta(minutes=int(settings.delivery_pickup_duration or 0))
        i=0
        for leg in route["legs"]:
            t+=timedelta(seconds=leg["duration"]["value"])
            obj.orders[i].write({"est_deliver_time":t.strftime("%H:%M")})
            addr=obj.orders[i].ship_address_id
            t+=timedelta(minutes=int(settings.delivery_dropoff_duration or settings.delivery_dropoff_duration or 0))
            total_dur+=leg["duration"]["value"]
            total_dist+=leg["distance"]["value"]
            i+=1
        dur=math.ceil(total_dur/60.0)
        dist=math.ceil(total_dist/1000.0)
        path=polyline_decode(route["overview_polyline"]["points"])
        obj.write({"directions_data":json.dumps(res),"directions_path":json.dumps(path),"est_distance":dist,"est_duration":dur})

    def confirm(self,ids,context={}):
        obj=self.browse(ids[0])
        for order in obj.orders:
            order.send_update_notif()
        obj.write({"state": "wait_pick"})

    def print_pdf(self,ids,context={}):
        print("Route.print_pdf",ids)
        url="https://admin.nfdelivery.com/report?type=report_jsx&model=nd.route&template=test&ids=%s"%json.dumps(ids)
        return {
            "action": {
                "type": "download",
                "url": url,
            }
        }

    def calc_times(self,ids,context={}):
        print("Route.calc_times",ids)
        settings=get_model("settings").browse(1)
        for obj in self.browse(ids):
            t=datetime.strptime(obj.delivery_date+" "+obj.round_id.period_id.time_from+":00","%Y-%m-%d %H:%M:%S")
            t+=timedelta(minutes=int(settings.delivery_pickup_duration or 0))
            for order in obj.orders:
                addr=order.ship_address_id
                drive_dur=int(addr.drive_duration or settings.delivery_drive_duration or 0)
                t+=timedelta(minutes=drive_dur)
                if order.time_from:
                    min_t=datetime.strptime(obj.delivery_date+" "+order.time_from+":00","%Y-%m-%d %H:%M:%S")
                else:
                    min_t=None
                if min_t and t<min_t:
                    wait_dur=int((min_t-t).total_seconds()/60)
                    t=min_t
                else:
                    wait_dur=0
                order.write({"est_deliver_time":t.strftime("%H:%M"),"est_drive_duration":drive_dur,"est_wait_duration":wait_dur})
                t+=timedelta(minutes=int(settings.delivery_dropoff_duration or settings.delivery_dropoff_duration or 0))
            drive_dur=int(obj.pickup_address_id.drive_duration or settings.delivery_drive_duration or 0)
            t+=timedelta(minutes=drive_dur)
            obj.write({"est_return_time":t.strftime("%H:%M")})

    def time_sort(self,ids,context={}):
        print("Route.time_sort",ids)
        n=0
        for obj in self.browse(ids):
            orders=[]
            for order in obj.orders:
                n+=1
                if order.time_from and order.time_to:
                    orders.append((order.time_from,order.time_to,order.id))
                else:
                    orders.append(("23:59:59","00:00:00",order.id))
            orders.sort()
            seq=1
            for _,_,order_id in orders:
                get_model("nd.order").write([order_id],{"sequence":seq})
                seq+=1
        self.calc_times(ids)
        return {
            "message": "%d delivery orders sorted"%n
        }

    def search_filter_order(self,clause,context={}):
        order_id=clause[2]
        order=get_model("nd.order").browse(order_id)
        cond=[["delivery_date","=",order.delivery_date]]
        if order.time_from and order.time_to:
            cond+=[["round_id.period_id.time_from","<",order.time_to],["round_id.period_id.time_to",">",order.time_from]]
        return cond

    def create_jobs(self,ids,context={}):
        job_routes={}
        for obj in self.browse(ids):
            if not obj.orders:
                continue
            k=(obj.delivery_date,obj.driver_id.id)
            job_routes.setdefault(k,[])
            job_routes[k].append((obj.est_pickup_time,obj.id))
        n=0
        for (delivery_date,driver_id),routes in job_routes.items():
            driver=get_model("nd.driver").browse(driver_id)
            job_vals={
                "date": delivery_date,
                "driver_id": driver_id,
                "title": "Delivery routes",
                "tasks": [],
                "state": "waiting",
            }
            res=get_model("nd.job").search([["date","=",job_vals["date"]],["driver_id","=",job_vals["driver_id"]]])
            if res:
                raise Exception("Job already created %s %s"%(job_vals["date"],driver.name))
            routes.sort()
            route_ids=[r[1] for r in routes]
            seq=1
            for route in self.browse(route_ids):
                task_vals={
                    "sequence": seq,
                    "type": "pickup",
                    "est_start_time": route.est_pickup_time,
                    "route_id": route.id,
                    "require_gps": True,
                    "state": "waiting",
                }
                job_vals["tasks"].append(("create",task_vals))
                seq+=1
                for order in route.orders:
                    task_vals={
                        "sequence": seq,
                        "type": "delivery",
                        "est_start_time": order.est_deliver_time,
                        "order_id": order.id,
                        "require_gps": True,
                        "state": "waiting",
                    }
                    job_vals["tasks"].append(("create",task_vals))
                    seq+=1
                task_vals={
                    "sequence": seq,
                    "type": "return",
                    "route_id": route.id,
                    "state": "waiting",
                }
                job_vals["tasks"].append(("create",task_vals))
            job_id=get_model("nd.job").create(job_vals,context=context)
            n+=1
        return {
            "message": "%s jobs created"%n,
        }

    def sort_addr_seq(self,ids,context={}):
        print("Route.sort_addr_seq",ids)
        n=0
        for obj in self.browse(ids):
            seq=1
            for order in get_model("nd.order").search_browse([["route_id","=",obj.id]],order="ship_address_id.sequence"):

                order.write({"sequence":seq})
                seq+=1
        self.calc_times(ids)

    def split_route(self,ids,context={}):
        print("Route.split_route",ids)
        obj=self.browse(ids[0])
        if len(obj.orders)<2:
            raise Exception("Route must contain at least 2 orders")
        vals={
            "delivery_date": obj.delivery_date,
            "driver_id": obj.driver_id.id,
            "round_id": obj.round_id.id,
        }
        route_id=self.create(vals,context=context)
        obj.orders[-1].write({"route_id":route_id})

    def get_report_data(self,ids,context={}):
        print("get_report_data",ids)
        routes=self.read_path(ids,["delivery_date","driver_id.name","round_id.period_id.name","round_id.period_id.time_from","round_id.period_id.time_to","orders.number","orders.ship_address_id.street_address","orders.time_from","orders.time_to","orders.ship_address_id.instructions","orders.item_desc","orders.customer_id.code","orders.customer_id.first_name","orders.customer_id.last_name","orders.sequence"])
        data={"routes":routes}
        #print("data",data)
        return data

Route.register()

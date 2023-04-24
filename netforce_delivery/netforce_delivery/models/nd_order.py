from netforce.model import Model,fields,get_model
from netforce import access
from netforce import utils
from datetime import *
import time
import requests
import csv
import re

URL_PREFIX="https://admin.nfdelivery.com/static/db/nfdelivery/files/"

class Order(Model):
    _name="nd.order"
    _string="Delivery Order"
    _audit_log=True
    _name_field="number"
    _key=["number"]
    _fields={
        "number": fields.Char("Order Number",required=True,search=True),
        "order_time": fields.DateTime("Order Time",required=True),
        "delivery_date": fields.Date("Delivery Date",required=True,search=True),
        "from_region_id": fields.Many2One("region","From Region"),
        "to_region_id": fields.Many2One("region","To Region"),
        "sender_id": fields.Many2One("contact","Sender Contact"),
        "sender_name": fields.Char("Sender Name"),
        "recipient_id": fields.Many2One("contact","Recipient Contact"),
        "recipient_name": fields.Char("Recipient Name"),
        "qty": fields.Decimal("Qty"),
        "uom_id": fields.Many2One("uom","UoM"),
        "product_id": fields.Many2One("product","Product"),
        "cash_collect_amount": fields.Decimal("Cash Collect"),
        "ref": fields.Char("Ref"),
        "time_from": fields.Char("From Time"),
        "time_to": fields.Char("To Time"),
        "ship_address_id": fields.Many2One("address","Shipping Address"),
        "cust_code": fields.Char("Customer Code",function="_get_related",function_context={"path":"customer_id.code"}),
        "cust_name": fields.Char("Customer Name",function="_get_related",function_context={"path":"customer_id.name"}),
        "coords": fields.Char("Coords",function="_get_related",function_context={"path":"ship_address_id.coords"}),
        "postal_code": fields.Char("Postal Code",function="_get_related",function_context={"path":"ship_address_id.postal_code"}),
        "street_address": fields.Char("Street Address",function="_get_related",function_context={"path":"ship_address_id.street_address"}),
        "instructions": fields.Char("Instructions",function="_get_related",function_context={"path":"ship_address_id.instructions"}),
        "addr_sequence": fields.Integer("Addr. Sequence",function="_get_related",function_context={"path":"ship_address_id.sequence"}),
        "item_desc": fields.Text("Item Description"),
        "state": fields.Selection([["wait_payment","Awaiting Payment"],["waiting","Awaiting Pickup"],["in_progress","In Progress"],["done","Completed"],["error","Can Not Deliver"]],"Status",required=True,search=True),
        "sequence": fields.Integer("Sequence"),
        "images": fields.One2Many("nd.image","related_id","Images"),
        "driver_id": fields.Many2One("nd.driver","Driver"),
        "route_id": fields.Many2One("nd.route","Delivery Route"),
        "round_id": fields.Many2One("nd.round","Delivery Round",function="_get_related",function_context={"path":"route_id.round_id"}),
        "period_id": fields.Many2One("nd.work.period","Delivery Period",function="_get_related",function_context={"path":"route_id.round_id.period_id"}),
        "user_id": fields.Many2One("base.user","Responsible User",function="_get_related",function_context={"path":"route_id.round_id.user_id"}),
        "pickup_time": fields.DateTime("Pickup Time",readonly=True),
        "deliver_time": fields.DateTime("Deliver Time",readonly=True),
        "tasks": fields.One2Many("nd.task","order_id","Tasks"),
        "est_deliver_time": fields.Char("Est. Delivery Time"),
        "act_deliver_time": fields.Char("Act. Delivery Time"),
        "error_time": fields.Char("Error Time"),
        "est_drive_duration": fields.Decimal("Est. Driving Duration(minutes)"),
        "est_wait_duration": fields.Decimal("Est. Waiting Duration (minutes)"),
        "est_state": fields.Selection([["on_time","On Time"],["late","Late"]],"Est. Status",function="get_est_state"),
        "dropoff_image": fields.File("Drop-off Photo"),
        "return_image": fields.File("Return Photo"),
        "require_dropoff_image": fields.Boolean("Require Dropoff Photo"),
        "require_return_image": fields.Boolean("Require Return Photo"),
        "email": fields.Char("Email"), # XXX: deprecated
        "mobile": fields.Char("Mobile"), # XXX: deprecated
        "dest_short": fields.Char("Destination",function="get_dest_short"),
        "eta_short": fields.Char("ETA",function="get_eta_short"),
        "today": fields.Boolean("Today",store=False,function_search="search_today"),
        "today_p1": fields.Boolean("Today+1",store=False,function_search="search_today_p1"),
        "today_p2": fields.Boolean("Today+2",store=False,function_search="search_today_p2"),
        "hide": fields.Boolean("Hidden",function="get_hide"),
        "tags": fields.Many2Many("nd.tag","Tags"),
        "tags_json": fields.Json("Order Tags",function="get_tags_json"), # XXX
        "address_tooltip": fields.Text("Address",function="get_address_tooltip"),
        "dropoff_coords": fields.Char("Drop-off Coords"),
        "poll_answers": fields.One2Many("nd.poll.answer","order_id","Poll Answers"),
        "poll_id": fields.Many2One("nd.poll","Customer Poll"),
        "poll2_id": fields.Many2One("nd.poll","Customer Poll #2"),
        "require_dropoff_coords": fields.Boolean("Require Drop-off Coords"),
        "deliver_perf": fields.Selection([["on_time","On Time"],["late","Late"],["early","Ealy"]],"Delivery Performance",function="get_deliver_perf"),
        "lines": fields.One2Many("nd.order.line","order_id","Delivery Items"),
        "returns": fields.One2Many("nd.order.return","order_id","Returned Products"),
        "customer_id": fields.Many2One("contact","Customer",search=True),
        "returnable_products": fields.Many2Many("product","Returnable Products",function="get_returnable_products"),
        "month": fields.Char("Month",function="get_month"),
        "week": fields.Char("Week",function="get_week"),
        "pickings": fields.One2Many("stock.picking","delivery_id","Stock Pickings"),
        "track_entries": fields.One2Many("account.track.entry","related_id","Track Entries"),
        "notes": fields.Text("Remarks"),
    }
    _order="delivery_date,route_id.round_id.period_id.time_from,route_id.driver_id.sequence,sequence,id"
    _constraints=["check_route_date","check_time_format"]

    def _get_number(self, context={}):
        seq_id = get_model("sequence").find_sequence(type="delivery_order",context=context)
        if not seq_id:
            return None
        while 1:
            num = get_model("sequence").get_next_number(seq_id, context=context)
            if not num:
                return None
            user_id = access.get_active_user()
            access.set_active_user(1)
            res = self.search([["number", "=", num]])
            access.set_active_user(user_id)
            if not res:
                return num
            get_model("sequence").increment_number(seq_id, context=context) 

    _defaults={
        "number": _get_number,
        "order_time": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
        "state": "waiting",
        "delivery_date": lambda *a: time.strftime("%Y-%m-%d"),
    }

    def check_time_format(self,ids,context={}):
        for obj in self.browse(ids):
            if obj.time_from and not re.match("\d\d:\d\d",obj.time_from):
                raise Exception("Invalid time format: %s"%obj.time_from)
            if obj.time_to and not re.match("\d\d:\d\d",obj.time_to):
                raise Exception("Invalid time format: %s"%obj.time_to)

    def write(self,ids,vals,*args,context={},**kw):
        if "state" in vals:
            new_state=vals["state"]
            for obj in self.browse(ids):
                if new_state==obj.state:
                    continue
                ctx={
                    "related_id": "nd.order,%d"%obj.id,
                    "customer_id": obj.customer_id.id,
                    "mobile": obj.customer_id.mobile,
                    "email": obj.customer_id.email,
                    "cust_first_name": obj.customer_id.first_name,
                    "driver_name": obj.route_id.driver_id.name if obj.route_id else None,
                    "order_no": obj.number,
                    "pickup_image_url": URL_PREFIX+obj.pickup_image if obj.pickup_image else None,
                    "dropoff_image_url": URL_PREFIX+obj.dropoff_image if obj.dropoff_image else None,
                }
                tset=obj.template_set_id
                cust=obj.customer_id
                if tset and cust:
                    if obj.state=="waiting" and new_state=="in_progress":
                        if tset.sms_pickup_id and cust.mobile:
                            tset.sms_pickup_id.send_message(context=ctx)
                        if tset.email_pickup_id and cust.email:
                            tset.email_pickup_id.send_message(context=ctx)
                    elif new_state=="done":
                        if tset.sms_delivery_id and cust.mobile:
                            tset.sms_delivery_id.send_message(context=ctx)
                        if tset.email_delivery_id and cust.email:
                            tset.email_delivery_id.send_message(context=ctx)
                    elif new_state=="error":
                        ctx["error_time"]=time.strftime("%H:%M")
                        if tset.sms_error_id and cust.mobile:
                            tset.sms_error_id.send_message(context=ctx)
                        if tset.email_error_id and cust.email:
                            tset.email_error_id.send_message(context=ctx)
        super().write(ids,vals,*args,**kw)
        if "time_from" in vals or "time_to" in vals:
            route_ids=[]
            for obj in self.browse(ids):
                if obj.route_id:
                    route_ids.append(obj.route_id.id)
            route_ids=list(set(route_ids))
            if route_ids:
                get_model("nd.route").calc_times(route_ids)
        if "route_id" in vals:
            for obj in self.browse(ids):
                for pick in obj.pickings:
                    pick.function_store() # route text update

    def set_in_progress(self,ids,context={}):
        obj=self.browse(ids[0])
        obj.write({"state":"in_progress"},context=context)
        if not obj.pickup_time:
            t=time.strftime("%Y-%m-%d %H:%M:%S"),
            obj.write({"pickup_time":t})
        obj.trigger("nd_order_pickup")

    """
    def set_done(self,ids,context={}):
        obj=self.browse(ids[0])
        if obj.require_dropoff_image and not obj.dropoff_image:
            raise Exception("Dropoff photo is required for this order")
        #if obj.require_return_image and not obj.return_image:
        #    raise Exception("Missing return photo")
        coords=context.get("coords")
        if obj.require_dropoff_coords and not coords:
            raise Exception("Dropoff coordinates are required for this order")
        h=time.strftime("%H:%M"),
        obj.write({"state":"done","act_deliver_time":h},context=context)
        addr=obj.ship_address_id
        if coords:
            obj.write({"dropoff_coords":coords})
            addr.write({"coords":coords,"coords_driver_id":obj.route_id.driver_id.id})
        obj.trigger("nd_order_done")
    """

    def set_done(self,ids,context={}):
        for obj in self.browse(ids):
            obj.write({"state":"done"})
            driver=obj.driver_id
            if not driver:
                raise Exception("Missing driver in job %s"%obj.number)
            if obj.cash_collect_amount:
                if not driver.track_id:
                    raise Exception("Missing tracking account in driver %s"%driver.name)
                vals={
                    "track_id": driver.track_id.id,
                    "date": obj.delivery_date,
                    "amount": obj.cash_collect_amount,
                    "description": "Cash collected for delivery order  %s"%obj.number,
                    "related_id": "nd.order,%s"%obj.id,
                }
                get_model("account.track.entry").create(vals)

    def set_error(self,ids,context={}):
        obj=self.browse(ids[0])
        today=time.strftime("%Y-%m-%d")
        if obj.delivery_date!=today:
            raise Exception("Delivery date is not today")
        obj.write({"state":"error"},context=context)
        obj.trigger("nd_order_error")

    def set_waiting(self,ids,context={}):
        obj=self.browse(ids[0])
        obj.write({"state":"waiting"},context=context)

    def seq_up(self,ids,context={}):
        obj=self.browse(ids[0])
        route=obj.route_id
        if not route:
            return
        order_ids=[o.id for o in route.orders]
        i=order_ids.index(obj.id)
        if i<len(order_ids)-1:
            swap_order_id=order_ids[i+1]
            order_ids[i+1]=obj.id
            order_ids[i]=swap_order_id
        seq=1
        for order_id in order_ids:
            self.write([order_id],{"sequence":seq})
            seq+=1

    def seq_down(self,ids,context={}):
        obj=self.browse(ids[0])
        route=obj.route_id
        if not route:
            return
        order_ids=[o.id for o in route.orders]
        i=order_ids.index(obj.id)
        if i>0:
            swap_order_id=order_ids[i-1]
            order_ids[i-1]=obj.id
            order_ids[i]=swap_order_id
        seq=1
        for order_id in order_ids:
            self.write([order_id],{"sequence":seq})
            seq+=1

    def get_est_state(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            st=None
            if obj.est_deliver_time:
                st="on_time"
                if obj.time_to:
                    if obj.est_deliver_time>obj.time_to:
                        st="late"
            vals[obj.id]=st
        return vals

    def get_dest_short(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            s=""
            if obj.sequence is not None:
                s+="%s. "%obj.sequence
            if obj.time_from or obj.time_to:
                s+="%s-%s"%(obj.time_from,obj.time_to)
            else:
                s+="any time"
            s+=", ["+(obj.customer_id.code or "")+"] "+(obj.customer_id.first_name or "")
            vals[obj.id]=s
        return vals

    def get_eta_short(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            vals[obj.id]="ETA %s, Drive %s, Wait %s"%(obj.est_deliver_time,obj.est_drive_duration is not None and "%d min"%int(obj.est_drive_duration) or "N/A",obj.est_wait_duration is not None and "%d min"%int(obj.est_wait_duration) or "N/A")
        return vals

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

    def get_hide(self,ids,context={}):
        vals={}
        route_ids=[]
        for obj in self.browse(ids):
            if obj.route_id:
                route_ids.append(obj.route_id.id)
        route_ids=list(set(route_ids))
        hide={}
        for route in get_model("nd.route").browse(route_ids):
            prev_order=None
            for order in route.orders:
                if route.blind_mode and prev_order and prev_order.state not in ("done","error"):
                    hide[order.id]=True
                else:
                    hide[order.id]=False
                prev_order=order
        for obj in self.browse(ids):
            vals[obj.id]=hide.get(obj.id)
        return vals

    def new_order(self,order_vals,context={}):
        print("new_order",order_vals)
        delivery_date=order_vals.get("delivery_date")
        if not delivery_date:
            raise Exception("Missing delivery date")
        time_from=order_vals.get("time_from")
        if time_from:
            while len(time_from)<5:
                time_from="0"+time_from
        time_to=order_vals.get("time_to")
        if time_to:
            while len(time_to)<5:
                time_to="0"+time_to
        products=order_vals.get("products")
        if not products:
            raise Exception("Missing products description")
        products=products.strip()
        first_name=order_vals.get("first_name")
        if not first_name:
            raise Exception("Missing customer first name")
        last_name=order_vals.get("last_name")
        cust_code=order_vals.get("cust_code")
        if not cust_code:
            raise Exception("Missing customer code")
        postal_code=order_vals.get("postal_code")
        if not postal_code:
            raise Exception("Missing postal code")
        street_address=order_vals.get("street_address")
        if not street_address:
            raise Exception("Missing street address")
        street_address=street_address.strip()
        instructions=order_vals.get("instructions")
        if instructions:
            instructions=instructions.strip()
        email=order_vals.get("email")
        phone=order_vals.get("phone")
        template_set=order_vals.get("template_set")
        poll=order_vals.get("poll")
        poll2=order_vals.get("poll2")
        tags=order_vals.get("tags")
        require_dropoff_image=order_vals.get("require_dropoff_image")
        require_return_image=order_vals.get("require_return_image")
        require_dropoff_coords=order_vals.get("require_dropoff_coords")
        seq=order_vals.get("address_sequence") or order_vals.get("sequence")
        cust_vals={
            "first_name": first_name,
            "last_name": last_name,
            "code": cust_code,
            "email": email,
            "mobile": phone,
        }
        cust_id=get_model("contact").merge_contact(cust_vals,context=context)
        addr_vals={
            "customer_id": cust_id,
            "postal_code": postal_code,
            "street_address": street_address,
        }
        addr_id=get_model("address").merge_address(addr_vals,context=context)
        if seq is not None:
            get_model("address").write([addr_id],{"sequence":seq})
        if template_set:
            res=get_model("nd.template.set").search([["name","=",template_set]])
            if not res:
                raise Exception("Notification template set not found: '%s'"%template_set)
            template_set_id=res[0]
        else:
            template_set_id=None
        if poll:
            res=get_model("nd.poll").search([["name","=",poll]])
            if not res:
                raise Exception("Customer poll not found: '%s'"%poll)
            poll_id=res[0]
        else:
            poll_id=None
        if poll2:
            res=get_model("nd.poll").search([["name","=",poll2]])
            if not res:
                raise Exception("Customer poll not found: '%s'"%poll2)
            poll2_id=res[0]
        else:
            poll2_id=None
        vals={
            "delivery_date": delivery_date,
            "time_from": time_from,
            "time_to": time_to,
            "item_desc": products,
            "customer_id": cust_id,
            "ship_address_id": addr_id,
            "template_set_id": template_set_id,
            "require_dropoff_image": require_dropoff_image,
            "require_return_image": require_return_image,
            "require_dropoff_coords": require_dropoff_coords,
            "poll_id": poll_id,
            "poll2_id": poll2_id,
        }
        if tags:
            tag_ids=[]
            for tag in tags.split(","):
                tag=tag.strip()
                res=get_model("nd.tag").search([["name","=",tag]])
                if not res:
                    raise Exception("Tag not found: '%s'"%tag)
                tag_id=res[0]
                tag_ids.append(tag_id)
            vals["tags"]=[("set",tag_ids)]
        order_id=get_model("nd.order").create(vals,context=context)
        return order_id

    def import_csv_old(self,fname,context={}): # XXX: deprecated
        path=utils.get_file_path(fname)
        line_no=1
        num_orders=0
        headers=["Delivery Date","Time From","Time To","Products","Customer First Name","Customer Last Name","Customer Code","Postal Code","Street Address","Customer Email","Customer Phone","Driver Instructions","Sequence","Notification Template Set","Tags","Require Dropoff Photo","Require Return Photo","Customer Poll","Customer Poll #2","Require Dropoff Coords"]
        with open(path) as f:
            rd=csv.DictReader(f)
            for row in rd:
                try:
                    for h in row:
                        if h not in headers:
                            raise Exception("Invalid header: '%s'"%h)
                    vals={
                        "delivery_date": row.get("Delivery Date"),
                        "time_from": row.get("Time From"),
                        "time_to": row.get("Time To"),
                        "products": row.get("Products"),
                        "first_name": row.get("Customer First Name"),
                        "last_name": row.get("Customer Last Name"),
                        "cust_code": row.get("Customer Code"),
                        "postal_code": row.get("Postal Code"),
                        "street_address": row.get("Street Address"),
                        "email": row.get("Customer Email"),
                        "phone": row.get("Customer Phone"),
                        "instructions": row.get("Driver Instructions"),
                        "sequence": (row.get("Sequence") or "").strip() or None,
                        "template_set": row.get("Notification Template Set"),
                        "tags": row.get("Tags"),
                        "require_dropoff_image": row.get("Require Dropoff Photo") and True or False,
                        "require_return_image": row.get("Require Return Photo") and True or False,
                        "require_dropoff_coords": row.get("Require Dropoff Coords") and True or False,
                        "poll": row.get("Customer Poll"),
                        "poll2": row.get("Customer Poll #2"),
                    }
                    self.new_order(vals,context=context)
                    num_orders+=1
                except Exception as e:
                    raise Exception("Error in CSV file, line %d: %s"%(line_no,e))
                line_no+=1
        return {
            "action": {
                "name": "nd_order",
                "active_tab": 3,
                "message": "%d delivery orders imported successfully"%num_orders,
            },
        }

    def auto_assign(self,context={}):
        n=0
        order_ids=[]
        route_ids=[]
        for obj in self.search_browse([["route_id","=",None]],context=context):
            route_id=None
            seq=obj.ship_address_id.sequence
            if seq:
                cond=[["delivery_date","=",obj.delivery_date]]
                for route in get_model("nd.route").search_browse(cond,order="round_id.period_id.time_from,driver_id.sequence",context=context):
                    if not route.seq_from:
                        continue
                    if not route.seq_to:
                        continue
                    if route.seq_from and seq<route.seq_from:
                        continue
                    if route.seq_to and seq>route.seq_to:
                        continue
                    route_id=route.id
                    break
            if not route_id:
                cond=[["delivery_date","=",obj.delivery_date]]
                for route in get_model("nd.route").search_browse(cond,order="round_id.period_id.time_from,driver_id.sequence",context=context):
                    if route.seq_from:
                        continue
                    if route.seq_to:
                        continue
                    if obj.time_to and obj.time_to<=route.round_id.period_id.time_from:
                        continue
                    if obj.time_from and obj.time_from>=route.round_id.period_id.time_to:
                        continue
                    route_id=route.id
                    break
            if not route_id:
                continue
            obj.write({"route_id":route_id})
            order_ids.append(obj.id)
            route_ids.append(route_id)
            n+=1
        route_ids=list(set(route_ids))
        get_model("nd.route").sort_addr_seq(route_ids)
        return {
            "message": "%d delivery orders auto-assigned"%n,
        }

    def check_route_date(self,ids,context={}):
        for obj in self.browse(ids):
            if not obj.route_id:
                continue
            if obj.route_id.delivery_date!=obj.delivery_date:
                raise Exception("Route date is different than delivery order date (%s)"%obj.number)

    def check_route_round(self,ids,context={}):
        for obj in self.browse(ids):
            if not obj.route_id:
                continue
            if obj.time_from and obj.time_from>obj.route_id.round_id.period_id.time_to:
                raise Exception("Route period is outside delivery order timeslot (%s)"%obj.number)
            if obj.time_to and obj.time_to<obj.route_id.round_id.period_id.time_from:
                raise Exception("Route period is outside delivery order timeslot (%s)"%obj.number)

    def get_deliveries_per_day(self,context={}):
        num_del={}
        num_late={}
        num_early={}
        for obj in self.search_browse([["state","=","done"]],context=context):
            num_del.setdefault(obj.delivery_date,0)
            num_del[obj.delivery_date]+=1
            if obj.act_deliver_time:
                if obj.time_to and obj.act_deliver_time>obj.time_to:
                    num_late.setdefault(obj.delivery_date,0)
                    num_late[obj.delivery_date]+=1
                if obj.time_from and obj.act_deliver_time<obj.time_from:
                    num_early.setdefault(obj.delivery_date,0)
                    num_early[obj.delivery_date]+=1
        data=[]
        data_late=[]
        data_early=[]
        for ds in sorted(num_del):
            d=datetime.strptime(ds,"%Y-%m-%d")
            t=time.mktime(d.timetuple()) * 1000
            data.append([t,num_del[ds]])
            data_late.append([t,num_late.get(ds,0)])
            data_early.append([t,num_early.get(ds,0)])
        return [{
            "name": "Total daily deliveries",
            "data": data,
            "color": "blue",
        },{
            "name": "Late deliveries",
            "data": data_late,
            "color": "red",
        },{
            "name": "Early deliveries",
            "data": data_early,
            "color": "orange",
        }]

    def reset_route(self,ids,context={}):
        self.write(ids,{"route_id":None})
        return {
            "message": "Cleared routes of %d delivery orders"%len(ids),
        }

    def get_tags_json(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            data=[]
            for t in obj.tags:
                data.append({
                    "id": t.id,
                    "name": t.name,
                    "color": t.color,
                })
            vals[obj.id]=data
        return vals

    def get_address_tooltip(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            addr=obj.ship_address_id
            s="Address: %s"%addr.street_address
            if addr.instructions:
                s+="\nInstructions: "+addr.instructions
            vals[obj.id]=s
        return vals

    def set_sequence(self,ids,context={}):
        print("Order.set_sequence",ids)
        order_id=context["order_id"]
        print("order_id",order_id)
        route_id=context["route_id"]
        print("route_id",route_id)
        route_ids=[]
        obj=self.browse(order_id)
        if obj.route_id:
            route_ids.append(obj.route_id.id)
        obj.write({"route_id":route_id})
        if route_id and route_id!=obj.route_id.id:
            route_ids.append(route_id)
        seq=1
        for obj in self.browse(ids):
            obj.write({"sequence":seq})
            seq+=1
        if route_ids:
            get_model("nd.route").calc_times(route_ids)

    def send_feedback(self,ids,context={}):
        obj=self.browse(ids[0])
        poll_option_id=context.get("poll_option_id")
        poll2_option_id=context.get("poll2_option_id")
        if obj.poll_id:
            vals={
                "order_id": obj.id,
                "poll_id": obj.poll_id.id,
                "option_id": poll_option_id,
            }
            get_model("nd.poll.answer").create(vals)
        if obj.poll2_id:
            vals={
                "order_id": obj.id,
                "poll_id": obj.poll2_id.id,
                "option_id": poll2_option_id,
            }
            get_model("nd.poll.answer").create(vals)

    def get_deliver_perf(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            perf=None
            if obj.state=="done" and obj.act_deliver_time:
                perf="on_time"
                if obj.time_to and obj.act_deliver_time>obj.time_to:
                    perf="late"
                elif obj.time_from and obj.act_deliver_time<obj.time_from:
                    perf="early"
            vals[obj.id]=perf
        return vals

    def import_record(self,vals,context={}):
        print("order.import_record",vals)
        customer_id=get_model("contact").import_record(vals["customer_id"],context=context)
        vals["ship_address_id"]["customer_id"]=customer_id
        return super().import_record(vals,context=context)

    def get_returnable_products(self,ids,context={}):
        prod_ids=get_model("product").search([["need_return","=",True]],context=context)
        vals={}
        for obj in self.browse(ids):
            vals[obj.id]=prod_ids
        return vals

    def return_product(self,ids,product_id,context={}):
        obj=self.browse(ids[0])
        vals={
            "order_id": obj.id,
            "product_id": product_id,
            "qty": 1,
        }
        get_model("nd.order.return").create(vals)

    def get_month(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            if obj.delivery_date:
                d=datetime.strptime(obj.delivery_date,"%Y-%m-%d")
                v=d.strftime("%y-%m")
            else:
                v=None
            vals[obj.id]=v
        return vals

    def get_week(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            if obj.delivery_date:
                d=datetime.strptime(obj.delivery_date,"%Y-%m-%d")
                v=d.strftime("%y-%W")
            else:
                v=None
            vals[obj.id]=v
        return vals

Order.register()

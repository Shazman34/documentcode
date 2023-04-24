from netforce.model import Model,fields,get_model
from netforce import database
from netforce import access
from netforce import ipc
import googlemaps
from decimal import *
from datetime import *
import time
import json
import math

API_KEY="AIzaSyAKs3alHGFG4ckYe6b0G67DbViVJX3rgV0"

class Job(Model):
    _name="l2g.job"
    _string="Job"
    _name_field="number"
    _audit_log=True
    _fields={
        "number": fields.Char("Job Number",required=True,search=True),
        "date": fields.Date("Pickup Date",search=True),
        "booking_id": fields.Many2One("l2g.booking","Booking",required=True,on_delete="cascade",search=True),
        "load_addr": fields.Text("Loading Address",search=True,function="_get_related",function_context={"path":"booking_id.load_addr"}),
        "delivery_addr": fields.Text("Delivery Address",search=True,function="_get_related",function_context={"path":"booking_id.delivery_addr"}),
        "customer_id": fields.Many2One("l2g.customer","Customer"),
        "return_trip": fields.Boolean("Return Trip",function="_get_related",function_context={"path":"booking_id.return_trip"}),
        "truck_type_id": fields.Many2One("l2g.truck.type","Truck Type",required=True,search=True),
        "weight_range_id": fields.Many2One("l2g.weight.range","Weight Range",required=True,search=True),
        "driver_id": fields.Many2One("l2g.driver","Driver",condition=[["driver_type","!=","planner"]]),
        "planner_id": fields.Many2One("l2g.driver","Planner",condition=[["driver_type","=","planner"]]),
        "truck_id": fields.Many2One("l2g.truck","Truck"),
        "state": fields.Selection([["pending","Pending"],["accepted","Accepted"],["delivered","Delivered"],["verified","Verified"],["invoiced","Invoiced"],["canceled","Canceled"]],"Status",required=True,search=True),
        "search_upcoming": fields.Boolean("Upcoming",store=False,function_search="search_upcoming"),
        "search_past": fields.Boolean("Past",store=False,function_search="search_past"),
        "trans_id": fields.Many2One("l2g.trans","Transaction"),
        "client_amount": fields.Decimal("Client Price"),
        "driver_amount": fields.Decimal("Driver Price"),
        "orig_client_amount": fields.Decimal("Orig. Client Price",readonly=True),
        "orig_driver_amount": fields.Decimal("Orig. Driver Price",readonly=True),
        "read_user_ids": fields.Array("Read By"),
        "from_province_id": fields.Many2One("l2g.province","Province (Pickup)"),
        "to_province_id": fields.Many2One("l2g.province","Province (Delivery)"),
        "rating": fields.Integer("Rating"),
        "comment": fields.Text("Comment"),
        "customer_cancel_fee": fields.Decimal("Customer Cancel Fee"),
        "driver_cancel_fee": fields.Decimal("Driver Cancel Fee"),
        "hide_price": fields.Boolean("Hide Price",function="get_hide_price"),
        "client_price_diff": fields.Decimal("Client Price Diff",function="get_price_diff",function_multi=True),
        "driver_price_diff": fields.Decimal("Driver Price Diff",function="get_price_diff",function_multi=True),
        "cust_invoice_id": fields.Many2One("account.invoice","Customer Invoice"),
        "supp_invoice_id": fields.Many2One("account.invoice","Supplier Invoice"),
        "do_received": fields.Boolean("DO Received"),
        "track_entries": fields.One2Many("account.track.entry","related_id","Tracking Entries"),
        "group_id": fields.Many2One("l2g.driver.group","Driver Group",search=True),
    }
    _order="id desc"

    def _get_number(self, context={}):
        seq_id = get_model("sequence").find_sequence(name="Job",context=context)
        if not seq_id:
            raise Exception("Missing number sequence for booking")
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
        "state": "pending",
    }

    # XXX: deprecated
    def search_upcoming(self,clause,context={}):
        d=datetime.today().strftime("%Y-%m-%d")
        return ["booking_id.book_date",">=",d]

    # XXX: deprecated
    def search_past(self,clause,context={}):
        d=datetime.today().strftime("%Y-%m-%d")
        return ["booking_id.book_date","<",d]

    def accept_job(self,ids,planner_driver_id=None,context={}):
        obj=self.browse(ids[0])
        user_id=access.get_active_user()
        if not user_id:
            raise Exception("Not logged in")
        res=get_model("l2g.driver").search([["user_id","=",user_id]])
        if not res:
            raise Exception("User is not a driver")
        driver_id=res[0]
        driver=get_model("l2g.driver").browse(driver_id)
        if driver.state!="approved":
            raise Exception("Driver is not approved")
        if driver.driver_type=="planner":
            if not planner_driver_id:
                raise Exception("Please select a driver first.")
            planner_id=driver_id
            driver_id=planner_driver_id
        else:
            planner_id=None
        obj.write({"state":"accepted","driver_id":driver_id,"planner_id":planner_id})
        if driver.driver_type=="planner":
            obj.send_planner_driver_notifs()

    def set_delivered(self,ids,context={}):
        obj=self.browse(ids[0])
        obj.write({"state":"delivered"})
        #obj.create_trans()
        ipc.send_signal("new_event")
        obj.copy_to_track()

    def set_verified(self,ids,rating=None,comment=None,context={}):
        obj=self.browse(ids[0])
        obj.write({"state":"verified","rating":rating,"comment":comment})
        #obj.create_trans()

    def create_trans(self,ids,context={}):
        obj=self.browse(ids[0])
        if not obj.driver_id:
            raise Exception("Missing driver in job")
        desc="Job %s verified"%obj.number
        if obj.planner_id:
            wallet_driver=obj.planner_id
            desc+=" (%s)"%obj.driver_id.full_name
        else:
            wallet_driver=obj.driver_id
        vals={
            "driver_id": wallet_driver.id,
            "amount": math.ceil(obj.driver_amount),
            "description": desc,
        }
        trans_id=get_model("l2g.trans").create(vals)
        obj.write({"trans_id":trans_id})


    def send_notifs(self,ids,context={}):
        for obj in self.browse(ids):
            for driver in get_model("l2g.driver").search_browse([]):
                if obj.group_id and driver.group_id.id!=obj.group_id.id:
                    continue
                if driver.state!="approved":
                    continue
                user=driver.user_id
                if not user:
                    continue
                for dev in user.device_tokens:
                    if dev.app_name!="load2go_driver":
                        continue
                    if driver.hide_price:
                        msg="Job %s: %s, %s %s tons, %s -> %s"%(obj.number,obj.booking_id.book_date,obj.truck_type_id.name,obj.weight_range_id.max_weight,obj.booking_id.from_district,obj.booking_id.to_district)
                    else:
                        msg="Job %s: %s, %s %s tons, RM %s, %s -> %s"%(obj.number,obj.booking_id.book_date,obj.truck_type_id.name,obj.weight_range_id.max_weight,obj.driver_amount,obj.booking_id.from_district,obj.booking_id.to_district)
                    vals={
                        "device_id": dev.id,
                        "title": "New job",
                        "message": msg,
                        "state": "to_send",
                    }
                    notif_id=get_model("push.notif").create(vals)
                    #get_model("push.notif").send([notif_id]) # XXX
        get_model("push.notif").send_notifs_async()

    def send_planner_driver_notifs(self,ids,context={}):
        for obj in self.browse(ids):
            driver=obj.driver_id
            user=driver.user_id
            if not user:
                continue
            for dev in user.device_tokens:
                msg="Job assigned %s: %s, %s %s tons, %s -> %s"%(obj.number,obj.booking_id.book_date,obj.truck_type_id.name,obj.weight_range_id.max_weight,obj.booking_id.load_addr,obj.booking_id.delivery_addr)
                vals={
                    "device_id": dev.id,
                    "title": "New job",
                    "message": msg,
                    "state": "to_send",
                }
                notif_id=get_model("push.notif").create(vals)
                get_model("push.notif").send([notif_id]) # XXX

    def read(self,ids,*args,context={},**kw):
        if not ids:
            return []
        db=database.get_connection()
        res=super().read(ids,*args,context=context,**kw)
        user_id=access.get_active_user()
        if not context.get("no_mark_read") and user_id:
            user_id=int(user_id)
            db.execute("UPDATE l2g_job SET read_user_ids=array_append(read_user_ids,%s) WHERE id IN %s AND (NOT read_user_ids@>ARRAY[%s] OR read_user_ids IS NULL)",user_id,tuple(ids),user_id)
        return res

    def get_num_unread(self,context={}):
        user_id=access.get_active_user()
        if not user_id:
            return 0
        db=database.get_connection()
        res=db.get("SELECT COUNT(*) AS num_unread FROM l2g_job WHERE state='pending' AND (NOT read_user_ids@>ARRAY[%s] OR read_user_ids IS NULL)",user_id)
        return res.num_unread or 0

    def cancel_job(self,ids,context={}):
        for obj in self.browse(ids):
            if obj.state not in ("pending","approved"):
                raise Exception("Can only cancel pending orders")
            obj.write({"state":"canceled"})
            dt=(datetime.strptime(obj.date,"%Y-%m-%d")-datetime.today()).days
            if dt<=1:
                vals={
                    "customer_id": obj.booking_id.customer_id.id,
                    "amount": -obj.customer_cancel_fee or 0,
                    "description": "Job %s canceled"%obj.number,
                }
                trans_id=get_model("l2g.trans").create(vals)
            booking_id=obj.booking_id.id
            booking=get_model("l2g.booking").browse(booking_id)
            cancel_booking=True
            for job in booking.jobs:
                if job.state!="canceled":
                    cancel_booking=False
            if cancel_booking:
                booking.write({"state":"canceled"})

    def cancel_job_driver(self,ids,context={}):
        for obj in self.browse(ids):
            if obj.state!="accepted":
                raise Exception("Can only cancel accepted orders")
            obj.write({"state":"pending"})
            vals={
                "driver_id": obj.driver_id.id,
                "amount": -obj.driver_cancel_fee or 0,
                "description": "Job %s canceled"%obj.number,
            }
            trans_id=get_model("l2g.trans").create(vals)

    def get_rate_job_id(self,context={}):
        user_id=access.get_active_user()
        res=self.search([["state","=","delivered"],["booking_id.customer_id.user_id","=",user_id]])
        if res:
            return res[0]
        return None

    def get_filter(self,access_type,context={}):
        user_id=access.get_active_user()
        if not user_id:
            return False
        if user_id==1:
            return True
        prof_code=access.get_active_profile_code()
        if prof_code!="L2G_DRIVER":
            return True
        res=get_model("l2g.driver").search([["user_id","=",user_id]])
        if not res:
            return False
        driver_id=res[0]
        driver=get_model("l2g.driver").browse(driver_id)
        if driver.state!="approved":
            return False
        return ["or",["group_id","=",None],["group_id","=",driver.group_id.id]]

    def get_hide_price(self,ids,context={}):
        hide=False
        user_id=access.get_active_user()
        prof_code=access.get_active_profile_code()
        if prof_code=="L2G_DRIVER":
            res=get_model("l2g.driver").search([["user_id","=",user_id]])
            if res:
                driver_id=res[0]
                driver=get_model("l2g.driver").browse(driver_id)
                hide=driver.hide_price
        return {id:hide for id in ids}

    def get_price_diff(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            vals[obj.id]={
                "client_price_diff": (obj.client_amount or 0)-(obj.orig_client_amount or 0),
                "driver_price_diff": (obj.driver_amount or 0)-(obj.orig_driver_amount or 0),
            }
        return vals

    def reassign(self,ids,driver_id,context={}):
        obj=self.browse(ids[0])
        if not driver_id:
            raise Exception("Please select a driver first.")
        obj.write({"state":"accepted","driver_id":driver_id})
        obj.send_planner_driver_notifs()

    def copy_to_invoice(self,ids,context={}):
        res=get_model("account.account").search([["code","=","4200"]])
        if not res:
            raise Exception("Sales account not found")
        sale_acc_id=res[0]
        res=get_model("account.account").search([["code","=","5300"]])
        if not res:
            raise Exception("Purchase account not found")
        purch_acc_id=res[0]
        cust_jobs={}
        supp_jobs={}
        for obj in self.browse(ids):
            if obj.state not in ("delivered","verified"):
                raise Exception("Invalid status")
            if obj.cust_invoice_id:
                raise Exception("Customer invoice already created for job %s"%obj.number)
            if obj.supp_invoice_id:
                raise Exception("Supplier invoice already created for job %s"%obj.number)
            booking=obj.booking_id
            if booking.customer_id.company_id:
                booking.customer_id.company_id.copy_to_contact()
                booking=booking.browse()[0]
                cust_id=booking.customer_id.company_id.contact_id.id
            else:
                booking.customer_id.copy_to_contact()
                booking=booking.browse()[0]
                cust_id=booking.customer_id.contact_id.id
            driver=obj.driver_id
            if not driver:
                raise Exception("Missing driver in job %s"%obj.number)
            if driver.transporter_id:
                driver.transporter_id.copy_to_contact()
                driver=driver.browse()[0]
                supp_id=driver.transporter_id.contact_id.id
            else:
                driver.copy_to_contact()
                driver=driver.browse()[0]
                supp_id=driver.contact_id.id
            cust_jobs.setdefault(cust_id,[]).append(obj)
            supp_jobs.setdefault(supp_id,[]).append(obj)
        for cust_id,objs in cust_jobs.items():
            for obj in objs:
                inv_vals={
                    "contact_id": cust_id,
                    "type": "out",
                    "inv_type": "invoice",
                    "due_date": time.strftime("%Y-%m-%d"),
                    "lines": [],
                    "memo": "Job %s"%obj.number,
                }
                line_vals={
                    "description": "Job %s"%obj.number,
                    "qty": 1,
                    "unit_price": obj.client_amount,
                    "amount": obj.client_amount,
                    "account_id": sale_acc_id,
                }
                inv_vals["lines"].append(("create",line_vals))
                inv_id=get_model("account.invoice").create(inv_vals,context={"type":"out","inv_type":"invoice"})
                get_model("account.invoice").post([inv_id])
                obj.write({"cust_invoice_id":inv_id})
        for supp_id,objs in supp_jobs.items():
            for obj in objs:
                inv_vals={
                    "contact_id": supp_id,
                    "type": "in",
                    "inv_type": "invoice",
                    "due_date": time.strftime("%Y-%m-%d"),
                    "lines": [],
                }
                line_vals={
                    "description": "Job %s"%obj.number,
                    "qty": 1,
                    "unit_price": obj.driver_amount,
                    "amount": obj.driver_amount,
                    "account_id": purch_acc_id,
                }
                inv_vals["lines"].append(("create",line_vals))
                inv_id=get_model("account.invoice").create(inv_vals,context={"type":"in","inv_type":"invoice"})
                get_model("account.invoice").post([inv_id])
                obj.write({"supp_invoice_id":inv_id})
        for obj in self.browse(ids):
            obj.write({"state": "invoiced"})

    def copy_to_track(self,ids,context={}):
        res=get_model("product").search([["code","=","DELIVERY"]])
        if not res:
            raise Exception("Product not found")
        prod_id=res[0]
        for obj in self.browse(ids):
            if obj.state not in ("delivered","verified"):
                raise Exception("Invalid status")
            if obj.track_entries:
                raise Exception("Tracking entries already created")
            booking=obj.booking_id
            if booking.customer_id.company_id:
                booking.customer_id.company_id.copy_to_contact()
                booking=booking.browse()[0]
                cust=booking.customer_id.company_id.contact_id
            else:
                booking.customer_id.copy_to_contact()
                booking=booking.browse()[0]
                cust=booking.customer_id.contact_id
            driver=obj.driver_id
            if not driver:
                raise Exception("Missing driver in job %s"%obj.number)
            if driver.transporter_id:
                driver.transporter_id.copy_to_contact()
                driver=driver.browse()[0]
                supp=driver.transporter_id.contact_id
            else:
                driver.copy_to_contact()
                driver=driver.browse()[0]
                supp=driver.contact_id
            cust.write({"customer":True}) # XXX
            supp.write({"supplier":True}) # XXX
            cust_track_id=cust.create_track()
            supp_track_id=supp.create_track()
            vals={
                "track_id": cust_track_id,
                "date": obj.date,
                "product_id": prod_id,
                "description": "Job %s"%obj.number,
                "amount": obj.client_amount,
                "related_id": "l2g.job,%s"%obj.id,
            }
            get_model("account.track.entry").create(vals)
            vals={
                "track_id": supp_track_id,
                "date": obj.date,
                "product_id": prod_id,
                "description": "Job %s"%obj.number,
                "amount": -obj.driver_amount,
                "related_id": "l2g.job,%s"%obj.id,
            }
            get_model("account.track.entry").create(vals)

    def set_do_received(self,ids,context={}):
        for obj in self.browse(ids):
            obj.write({"do_received":True})

    def clear_group(self,ids,context={}):
        for obj in self.browse(ids):
            obj.write({"group_id":None})
            obj.send_notifs()

Job.register()

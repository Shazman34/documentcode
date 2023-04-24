from netforce.model import Model,fields,get_model
from netforce import access
from netforce import ipc
import googlemaps
from decimal import *
from datetime import *
import time
import json
from hashlib import sha256


#API_KEY="AIzaSyAKs3alHGFG4ckYe6b0G67DbViVJX3rgV0"
API_KEY="AIzaSyCo9jZD_iKy95ixF1C8WIpYFoHN2SrKPh8"

class Booking(Model):
    _name="l2g.booking"
    _string="Booking"
    _name_field="number"
    _audit_log=True
    _fields={
        "number": fields.Char("Booking Number",required=True,search=True),
        "device_id": fields.Char("Device ID"),
        "customer_id": fields.Many2One("l2g.customer","Customer",search=True),
        "truck_type_id": fields.Many2One("l2g.truck.type","Truck Type",search=True),
        "weight_range_id": fields.Many2One("l2g.weight.range","Weight Range",search=True),
        "create_date": fields.DateTime("Create Date",search=True),
        "confirm_date": fields.DateTime("Confirm Date",search=True),
        "book_date": fields.Date("Pickup Date",search=True),
        "book_date_week": fields.Char("Booking Week",function="get_date_agg",function_multi=True),
        "book_date_month": fields.Char("Booking Month",function="get_date_agg",function_multi=True),
        "unload_date": fields.Date("Unloading Date",search=True),
        "load_addr": fields.Text("Loading Address",search=True),
        "load_coords": fields.Char("Loading Coordinates"),
        "delivery_addr": fields.Text("Delivery Address",search=True),
        "delivery_coords": fields.Char("Delivery Coordinates"),
        "load_addr_json": fields.Json("Select Loading Addr"),
        "delivery_addr_json": fields.Json("Select Delivery Addr"),
        "state": fields.Selection([["draft","Draft"],["confirmed","Confirmed"],["invoiced","Invoiced"],["paid","Paid"],["canceled","Canceled"]],"Status",required=True,search=True),
        "truck_id": fields.Many2One("l2g.truck","Truck"),
        "distance": fields.Float("Distance (Km)"),
        "distance_incl_return": fields.Float("Distance (incl return)",function="get_distance_incl_return"),
        "route_polyline": fields.Text("Route Polyline"),
        "price_total": fields.Decimal("Client Price Total",function="get_total",function_multi=True),
        "tax_amount": fields.Decimal("Tax Amount",function="get_total",function_multi=True),
        "late_amount": fields.Decimal("Late Booking Amount",function="get_total",function_multi=True),
        "driver_price_total": fields.Decimal("Driver Price Total",function="get_total",function_multi=True),
        "driver_id": fields.Many2One("l2g.driver","Driver",condition=[["driver_type","!=","planner"]]), # XXX: deprecated
        "today": fields.Boolean("Today",store=False,function_search="search_today"),
        "this_week": fields.Boolean("This Week",store=False,function_search="search_this_week"),
        "new": fields.Boolean("New",store=False,function_search="search_new"),
        "search_upcoming": fields.Boolean("Upcoming",store=False,function_search="search_upcoming"),
        "search_past": fields.Boolean("Past",store=False,function_search="search_past"),
        "lines": fields.One2Many("l2g.booking.line","booking_id","Lines"),
        "jobs": fields.One2Many("l2g.job","booking_id","Jobs"),
        "from_loc": fields.Json("From Loc",function="get_locs",function_multi=True),
        "to_loc": fields.Json("To Loc",function="get_locs",function_multi=True),
        "user_id": fields.Many2One("base.user","Created By"),
        "pmt_trans_id": fields.Char("Payment Transaction ID"),
        "pmt_auth_code": fields.Char("Payment Auth Code"),
        "bypass_payment": fields.Boolean("Bypass Payment",function="_get_related",function_context={"path":"customer_id.bypass_payment"}),
        "from_province": fields.Char("Province (Pickup)"),
        "to_province": fields.Char("Province (Delivery)"),
        "from_district": fields.Char("District (Pickup)"),
        "to_district": fields.Char("District (Delivery)"),
        "from_province_id": fields.Many2One("l2g.province","Province (Pickup)",function="get_from_province",store=True,search=True),
        "to_province_id": fields.Many2One("l2g.province","Province (Delivery)",function="get_to_province",store=True,search=True),
        "from_country": fields.Char("From Country"),
        "to_country": fields.Char("To Country"),
        "from_country_id": fields.Many2One("country","From Country",function="get_from_country",store=True,search=True),
        "to_country_id": fields.Many2One("country","To Country",function="get_to_country",store=True,search=True),
        "comments": fields.Text("Comments"),
        "return_trip": fields.Boolean("Return Trip"),
        "labor_load": fields.Boolean("Manpower Loading"),
        "labor_unload": fields.Boolean("Manpower Unloading"),
        "has_custom": fields.Boolean("Has Custom Price",function="get_has_custom"),
        "approve_custom": fields.Boolean("Approve Custom Price"),
        "pricelist_id": fields.Many2One("l2g.pricelist","Pricelist",search=True),
        "show_alert": fields.Boolean("Show Alert",function="get_show_alert"),
        "add_amount": fields.Decimal("Additional Charges",function="get_add_amount"),
        "invoice_id": fields.Many2One("account.invoice","Invoice"),
        "products": fields.One2Many("l2g.booking.product","booking_id","Products"), 
        "product_weight": fields.Decimal("Product Weight",function="get_product_weight"),
        "charge_levy_id": fields.Many2One("l2g.penalty","Levy Charge"),
        "charge_customs_id": fields.Many2One("l2g.penalty","Customs Charge"),
        "agent_company": fields.Char("Agent Company"),
        "agent_contact": fields.Char("Agent Contact"),
        "agent_phone": fields.Char("Agent Phone"),
        "product_type_id": fields.Many2One("l2g.product.type","Product Type"),
        "is_late": fields.Boolean("Late Booking",function="get_late"),
        "late_rate": fields.Decimal("Late Booking Penalty (%)"),
    }
    _order="confirm_date desc,create_date desc,id desc"

    def _get_number(self, context={}):
        seq_id = get_model("sequence").find_sequence(name="Booking",context=context)
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
        "state": "draft",
        "create_date": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    def confirm(self,ids,paid=False,comments=None,send_notifs=True,context={}):
        obj=self.browse(ids[0])
        if not obj.load_addr:
            raise Exception("Missing loading location")
        if not obj.delivery_addr:
            raise Exception("Missing delivery location")
        if not obj.book_date:
            raise Exception("Missing booking date")
        if not obj.unload_date:
            raise Exception("Missing unloading date")
        if obj.unload_date<obj.book_date:
            raise Exception("Unloading date is before pickup date")
        if obj.has_custom and not obj.approve_custom:
            raise Exception("Booking contains custom truck types and has to be approved first")
        if obj.from_country and obj.to_country and obj.from_country != obj.to_country:
            if not obj.charge_levy_id:
                raise Exception("Missing levy")
            if not obj.charge_customs_id:
                raise Exception("Missing customs")
            if obj.charge_customs_id.name=="Own Agent":
                if not obj.agent_company:
                    raise Exception("Missing agent company")
                if not obj.agent_contact:
                    raise Exception("Missing agent contact")
                if not obj.agent_phone:
                    raise Exception("Missing agent phone")
        t=time.strftime("%Y-%m-%d %H:%M:%S")
        obj.write({"state":"confirmed","comments":comments,"confirm_date":t})
        if paid:
            trans_id=context.get("trans_id")
            auth_code=context.get("auth_code")
            obj.write({"state":"paid","pmt_trans_id":trans_id,"pmt_auth_code":auth_code})
        else:
            if not obj.customer_id.bypass_payment:
                raise Exception("Customer not allowed to bypass payment.")
        obj.create_jobs(send_notifs=send_notifs)
        obj.function_store()
        ipc.send_signal("new_event")
        return {
            "booking_number": obj.number,
        }

    def confirm_no_notifs(self,ids,context={}):
        self.confirm(ids,send_notifs=False)

    def create_jobs(self,ids,send_notifs=True,context={}):
        obj=self.browse(ids[0])
        if obj.jobs:
            raise Exception("Jobs already created for booking %s"%obj.number)
        for line in obj.lines:
            for i in range(line.qty):
                if not line.driver_price:
                    raise Exception("Missing driver price")
                vals={
                    "booking_id": obj.id,
                    "date": obj.book_date,
                    "truck_type_id": line.truck_type_id.id,
                    "weight_range_id": line.weight_range_id.id,
                    "client_amount": line.price,
                    "driver_amount": line.driver_price,
                    "orig_client_amount": line.price,
                    "orig_driver_amount": line.driver_price,
                    "state": "pending",
                    "from_province_id": obj.from_province_id.id,
                    "to_province_id": obj.to_province_id.id,
                    "customer_cancel_fee": line.customer_cancel_fee,
                    "driver_cancel_fee": line.driver_cancel_fee,
                }
                if obj.customer_id.group_id:
                    vals["group_id"]=obj.customer_id.group_id.id
                if obj.return_trip:
                    vals["client_amount"]*=Decimal(1.55)
                    vals["driver_amount"]*=Decimal(1.5)
                    vals["orig_client_amount"]*=Decimal(1.55)
                    vals["orig_driver_amount"]*=Decimal(1.5)
                vals["client_amount"]=round(vals["client_amount"])
                vals["driver_amount"]=round(vals["driver_amount"])
                vals["orig_client_amount"]=round(vals["orig_client_amount"])
                vals["orig_driver_amount"]=round(vals["orig_driver_amount"])
                job_id=get_model("l2g.job").create(vals)
                job=get_model("l2g.job").browse(job_id)
                if send_notifs:
                    job.send_notifs()

    def accept_job(self,ids,driver_id,context={}):
        obj=self.browse(ids[0])
        if not driver_id:
            raise Exception("Missing driver")
        obj.write({"state":"accepted","driver_id":driver_id})

    def next_delivered(self,ids,context={}):
        obj=self.browse(ids[0])
        obj.write({"state":"delivered"})

    def back_accepted(self,ids,context={}):
        obj=self.browse(ids[0])
        obj.write({"state":"accepted"})

    def search_today(self,clause,context={}):
        d=datetime.today().strftime("%Y-%m-%d")
        return ["book_date","=",d]

    def search_this_week(self,clause,context={}):
        d0=datetime.today().strftime("%Y-%m-%d")
        d1=(datetime.today()+timedelta(days=7)).strftime("%Y-%m-%d")
        return ["book_date","between",[d0,d1]]

    def search_new(self,clause,context={}):
        d=datetime.today().strftime("%Y-%m-%d")
        return ["book_date",">=",d]

    def search_upcoming(self,clause,context={}):
        d=datetime.today().strftime("%Y-%m-%d")
        return ["book_date",">=",d]

    def search_past(self,clause,context={}):
        d=datetime.today().strftime("%Y-%m-%d")
        return ["book_date","<",d]

    def get_date_agg(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            d=datetime.strptime(obj.book_date,"%Y-%m-%d") if obj.book_date else None
            month=d.strftime("%Y-%m") if d else None
            week=d.strftime("%Y-W%W") if d else None
            vals[obj.id]={
                "book_date_week": week,
                "book_date_month": month,
            }
        return vals

    def add_to_cart(self,ids,truck_type_id,weight_range_id,context={}):
        if not truck_type_id:
            raise Exception("Missing truck type")
        truck_type=get_model("l2g.truck.type").browse(truck_type_id)
        if not weight_range_id:
            raise Exception("Missing weight range")
        weight_range=get_model("l2g.weight.range").browse(weight_range_id)
        user_id=access.get_active_user()
        if not ids:
            vals={
                "user_id": user_id,
            }
            booking_id=self.create(vals)
            obj=self.browse(booking_id)
        else:
            obj=self.browse(ids[0])
        if obj.state!="draft":
            print("Error: can't update confirmed booking: %s"%obj.number)
        if not obj.load_addr:
            raise Exception("Missing loading address")
        if not obj.delivery_addr:
            raise Exception("Missing delivery address")
        if obj.from_province_id and obj.from_province_id.disable_pickup:
            raise Exception("Pickup province is disabled: %s"%obj.from_province_id.name)
        if obj.to_province_id and obj.to_province_id.disable_delivery:
            raise Exception("Delivery province is disabled: %s"%obj.to_province_id.name)
        if truck_type.exclude_from_regions:
            excl_ids=[r.id for r in truck_type.exclude_from_regions]
            if obj.from_province_id and obj.from_province_id.id in excl_ids:
                raise Exception("%s not available in %s"%(truck_type.name,obj.from_province_id.name))
        for mw in truck_type.min_weights:
            if mw.region_id and mw.region_id.id!=obj.from_province_id.id:
                continue
            if weight_range.max_weight<mw.min_weight or 0:
                raise Exception("Minimum weight for %s and %s is %s."%(obj.from_province_id.name,truck_type.name,mw.min_weight))
        vals={
            "booking_id": obj.id,
            "truck_type_id": truck_type_id,
            "weight_range_id": weight_range_id,
        }
        get_model("l2g.booking.line").create(vals)
        obj.update_prices()
        return {
            "booking_id": obj.id,
        }

    def update_prices(self,ids,context={}):
        obj=self.browse(ids[0])
        if obj.state!="draft":
            raise Exception("Error: can't update confirmed booking: %s"%obj.number)
        if obj.approve_custom:
            return
        distance=obj.distance or 0
        for line in obj.lines:
            price=None
            driver_price=None
            if line.truck_type_id and line.weight_range_id and obj.from_province_id and obj.to_province_id:
                found_pl=None
                for pl in get_model("l2g.pricelist").search_browse([]):
                    customer_ids=[c.id for c in pl.customers]
                    if customer_ids and obj.customer_id.id not in customer_ids:
                        continue
                    from_ids=[x.id for x in pl.from_regions]
                    to_ids=[x.id for x in pl.to_regions]
                    if from_ids and obj.from_province_id.id not in from_ids:
                        continue
                    if to_ids and obj.to_province_id.id not in to_ids:
                        continue
                    found_pl=pl
                if found_pl:
                    obj.write({"pricelist_id":found_pl.id})
                weight=line.weight_range_id.max_weight or 0
                found_p=None
                for p in found_pl.prices:
                    if p.truck_type_id and p.truck_type_id.id!=line.truck_type_id.id:
                        continue
                    if p.from_province_id and p.from_province_id.id!=obj.from_province_id.id:
                        continue
                    if p.to_province_id and p.to_province_id.id!=obj.to_province_id.id:
                        continue
                    if p.from_district and p.from_district!=obj.from_district:
                        continue
                    if p.to_district and p.to_district!=obj.to_district:
                        continue
                    if p.min_distance and distance<p.min_distance:
                        continue
                    if p.max_weight and weight!=p.max_weight:
                        continue
                    found_p=p
                if found_p:
                    if found_p.fare_per_km:
                        price=max(found_p.min_fare or 0,(found_p.fare_per_km or 0)*Decimal("%.3f"%distance)*(line.weight_range_id.max_weight or 0))
                    elif found_p.fare_per_ton:
                        price=max(found_p.min_fare or 0,(found_p.fare_per_ton or 0)*(line.weight_range_id.max_weight or 0))
                    else:
                        price=found_p.min_fare or 0
                    price=round(price)
                    if found_p.driver_fare_per_km:
                        driver_price=max(found_p.driver_min_fare or 0,(found_p.driver_fare_per_km or 0)*Decimal("%.3f"%distance)*(line.weight_range_id.max_weight or 0))
                    elif found_p.driver_fare_per_ton:
                        driver_price=max(found_p.driver_min_fare or 0,(found_p.driver_fare_per_ton or 0)*(line.weight_range_id.max_weight or 0))
                    else:
                        driver_price=found_p.driver_min_fare or 0
                    drive_price=round(driver_price)
                    line.write({"price":price,"driver_price":driver_price,"price_id":found_p.id,"customer_cancel_fee":found_p.cancel_fee or 0,"driver_cancel_fee":found_p.driver_cancel_fee or 0})
                else:
                    line.write({"price":None,"driver_price":None})

    def get_add_amount(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            amt=0
            for pen in get_model("l2g.penalty").search_browse([]):
                if pen.type!="penalty":
                    continue
                if not obj.load_addr:
                    continue
                if not obj.delivery_addr:
                    continue
                if pen.from_addr and obj.load_addr.find(pen.from_addr)==-1:
                    continue
                if pen.to_addr and obj.delivery_addr.find(pen.to_addr)==-1:
                    continue
                amt+=pen.fee or 0
            vals[obj.id]=amt
        return vals

    def get_total(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            price=0
            driver_price=0
            for line in obj.lines:
                price+=line.amount or 0
                driver_price+=(line.driver_price or 0)*(line.qty or 1)
            if obj.return_trip:
                price*=Decimal(1.55)
                driver_price*=Decimal(1.5)
            if obj.is_late and not (obj.customer_id and obj.customer_id.bypass_date_check):
                late_rate=obj.late_rate or 20
                late_amount=price*late_rate/Decimal(100)
                price+=late_amount
            else:
                late_amount=0
            if obj.labor_load:
                price+=150
            if obj.labor_unload:
                price+=150
            #tax=price*Decimal(0.06) # XXX
            price+=obj.add_amount
            if obj.from_country and obj.to_country and obj.from_country != obj.to_country:
                if obj.charge_levy_id:
                    price+=obj.charge_levy_id.fee or 0
                if obj.charge_customs_id:
                    price+=obj.charge_customs_id.fee or 0
            tax=0
            vals[obj.id]={
                "tax_amount": tax,
                "late_amount": late_amount,
                "price_total": round(price+tax,0),
                "driver_price_total": driver_price,
            }
        return vals

    def update_distance(self,ids,context={}):
        obj=self.browse(ids[0])
        from_coords=obj.load_coords
        to_coords=obj.delivery_coords
        if not from_coords or not to_coords:
            obj.write({"distance":None,"route_polyline":None})
            return
        client=googlemaps.Client(key=API_KEY)
        res=client.directions(from_coords,to_coords)
        if not res:
            raise Exception("Failed to get distance")
        distance=res[0]["legs"][0]["distance"]["value"]/1000.0
        polyline=res[0]["overview_polyline"]["points"]
        obj.write({"distance":distance,"route_polyline":polyline})

    def update_distance_prices(self,ids,context={}):
        self.update_distance(ids,context=context)
        self.update_prices(ids,context=context)

    def get_locs(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            if obj.load_coords:
                res=obj.load_coords.split(",")
                from_loc={
                    "name": obj.load_addr,
                    "lat": float(res[0]),
                    "lng": float(res[1]),
                }
            else:
                from_loc=None
            if obj.delivery_coords:
                res=obj.delivery_coords.split(",")
                to_loc={
                    "name": obj.delivery_addr,
                    "lat": float(res[0]),
                    "lng": float(res[1]),
                }
            else:
                to_loc=None
            vals[obj.id]={
                "from_loc": from_loc,
                "to_loc": to_loc,
            }
        return vals

    def update_cart(self,ids,vals,set_lines=False,context={}):
        print("#"*80)
        print("update_cart",ids,vals)
        user_id=access.get_active_user()
        if not ids:
            new_vals={
                "user_id": user_id,
            }
            booking_id=self.create(new_vals)
            obj=self.browse(booking_id)
        else:
            obj=self.browse(ids[0])
        if obj.state!="draft":
            print("Error: can't update confirmed booking: %s"%obj.number)
            return {
                "booking_id": None,
            }
        obj.write(vals)
        if set_lines:
            obj.write({"lines":[("delete_all",)]})
            truck_type_id=vals.get("truck_type_id")
            weight_range_id=vals.get("weight_range_id")
            if truck_type_id and weight_range_id:
                obj.add_to_cart(truck_type_id,weight_range_id)
        obj.update_distance()
        obj.function_store()
        obj.update_prices()
        obj.function_store() # XXX
        obj.check_truck_types()
        return {
            "booking_id": obj.id,
        }

    def check_truck_types(self,ids,context={}):
        obj=self.browse(ids[0])
        for line in obj.lines:
            truck_type=line.truck_type_id
            weight_range=line.weight_range_id
            if truck_type.exclude_from_regions:
                excl_ids=[r.id for r in truck_type.exclude_from_regions]
                if obj.from_province_id and obj.from_province_id.id in excl_ids:
                    raise Exception("%s not available in %s"%(truck_type.name,obj.from_province_id.name))
            for mw in truck_type.min_weights:
                if mw.region_id and mw.region_id.id!=obj.from_province_id.id:
                    continue
                if weight_range.max_weight<mw.min_weight or 0:
                    raise Exception("Minimum weight for %s and %s is %s."%(obj.from_province_id.name,truck_type.name,mw.min_weight))

    def get_from_province(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            prov_id=None
            if obj.from_province:
                res=get_model("l2g.province").search(["or",["name","=",obj.from_province],["locations.name","=",obj.from_province]])
                if res:
                    prov_id=res[0]
            vals[obj.id]=prov_id
        return vals

    def get_to_province(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            prov_id=None
            if obj.to_province:
                res=get_model("l2g.province").search(["or",["name","=",obj.to_province],["locations.name","=",obj.to_province]])
                if res:
                    prov_id=res[0]
            vals[obj.id]=prov_id
        return vals

    def get_from_country(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            country_id=None
            if obj.from_country:
                res=get_model("country").search([["name","=",obj.from_country]])
                if res:
                    country_id=res[0]
            vals[obj.id]=country_id
        return vals

    def get_to_country(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            country_id=None
            if obj.to_country:
                res=get_model("country").search([["name","=",obj.to_country]])
                if res:
                    country_id=res[0]
            vals[obj.id]=country_id
        return vals

    def get_has_custom(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            custom=False
            for line in obj.lines:
                if not line.price_id:
                    custom=True
            vals[obj.id]=custom
        return vals

    def get_show_alert(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            show_alert=obj.state=="drafe" and obj.has_custom and not obj.approve_custom
            vals[obj.id]=show_alert
        return vals

    def copy_to_invoice(self,ids,context={}):
        contact_id=None
        lines=[]
        for obj in self.browse(ids):
            if obj.customer_id.company_id:
                obj.customer_id.company_id.copy_to_contact()
                obj=obj.browse()[0]
                cont_id=obj.customer_id.company_id.contact_id.id
            else:
                obj.customer_id.copy_to_contact()
                obj=obj.browse()[0]
                cont_id=obj.customer_id.contact_id.id
            if not contact_id:
                contact_id=cont_id
            else:
                if cont_id!=contact_id:
                    raise Exception("Different customers selected")
            line_vals={
                "description": "Booking %s"%obj.number,
                "qty": 1,
                "unit_price": obj.price_total,
                "amount": obj.price_total,
            }
            lines.append(("create",line_vals))
        vals={
            "contact_id": contact_id,
            "type": "out",
            "inv_type": "invoice",
            "lines": lines,
        }
        inv_id=get_model("account.invoice").create(vals,context={"type":"out","inv_type":"invoice"})
        for obj in self.browse(ids):
            obj.write({"state":"invoiced","invoice_id":inv_id})

    def get_distance_incl_return(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            d=obj.distance or 0
            if obj.return_trip:
                d*=2
            vals[obj.id]=d
        return vals

    def get_product_weight(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            w=0
            for prod in obj.products:
                w+=prod.weight or 0
            vals[obj.id]=w
        return vals

    def onchange_load_addr(self,context={}):
        data=context["data"]
        val=data["load_addr_json"]
        data["load_addr"]=val["name"]
        data["load_coords"]=val["coords"]
        data["from_province"]=val["province"]
        res=get_model("l2g.province").search([["name","=",val["province"]]])
        data["from_province_id"]=res[0] if res else None
        data["from_district"]=val["district"]
        return data

    def onchange_delivery_addr(self,context={}):
        data=context["data"]
        val=data["delivery_addr_json"]
        data["delivery_addr"]=val["name"]
        data["delivery_coords"]=val["coords"]
        data["to_province"]=val["province"]
        res=get_model("l2g.province").search([["name","=",val["province"]]])
        data["to_province_id"]=res[0] if res else None
        data["to_district"]=val["district"]
        return data

    def get_late(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            if obj.confirm_date:
                conf_t=datetime.strptime(obj.confirm_date,"%Y-%m-%d %H:%M:%S")
            else:
                conf_t=datetime.now()
            t=conf_t.strftime("%H:%M")
            if t<"13:00":
                min_date=(conf_t.date()+timedelta(days=1)).strftime("%Y-%m-%d")
            else:
                min_date=(conf_t.date()+timedelta(days=2)).strftime("%Y-%m-%d")
            if obj.book_date and obj.book_date<min_date:
                late=True
            else:
                late=False
            vals[obj.id]=late
        return vals

    def get_payment_url(self,ids,context={}):
        print("get_payment_url",ids)
        obj=self.browse(ids[0])
        url="https://payment.ipay88.com.my/ePayment/entry.asp"
        print("=> url",url)
        params={
            "MerchantCode": "M13041", 
            "PaymentId": "",
            "RefNo": obj.number,
            "Amount": "%.2f"%obj.price_total,
            "Currency": "MYR",
            "ProdDesc": "Booking",
            "UserName": "%s %s"%(obj.customer_id.first_name,obj.customer_id.last_name),
            "UserContact": obj.customer_id.phone,
            "Lang": "UTF-8",
            "SignatureType": "SHA256",
            "ResponseURL": "http://backend.netforce.com/l2g_payment_response",
            "BackendURL": "http://backend.netforce.com/l2g_payment_notif",
        }
        key="D980xrl93o"
        msg=key+params["MerchantCode"]+params["RefNo"]+params["Amount"]+params["Currency"]
        params["Signature"]=sha256(msg.encode("utf-8")).hexdigest()
        print("=> params",params)
        return {
            "url": url,
            "params": params,
        }

Booking.register()

from netforce.model import Model,fields,get_model
from netforce import database
from netforce import access
from netforce import utils
from datetime import *
import time
import random

class Driver(Model):
    _name="l2g.driver"
    _string="Driver"
    _name_field="first_name"
    _fields={
        "first_name": fields.Char("First Name",required=True,search=True),
        "last_name": fields.Char("Last Name",required=True,search=True),
        "full_name": fields.Char("Full Name",function="get_full_name"),
        "phone": fields.Char("Phone",required=True,search=True),
        "photo": fields.File("Photo"),
        "image_id_card": fields.File("ID Card Scan"),
        "image_license": fields.File("Driving License"),
        "image_insurance": fields.File("Car Insurance"),
        "register_date": fields.Date("Register Date",required=True),
        "transporter_id": fields.Many2One("l2g.transporter","Transporter",search=True),
        "last_coords": fields.Char("Last Coords",function="get_last_loc",function_multi=True),
        "last_coords_time": fields.DateTime("Last Coords Time",function="get_last_loc",function_multi=True),
        "truck_id": fields.Many2One("l2g.truck","Truck"),
        "id_no": fields.Char("ID Number",search=True),
        "company": fields.Char("Company",search=True),
        "region_id": fields.Many2One("l2g.province","Region",search=True),
        "user_id": fields.Many2One("base.user","User"),
        "device_token": fields.Char("Device Token"),
        "balance": fields.Decimal("Wallet Balance",function="get_balance"),
        "transactions": fields.One2Many("l2g.trans","driver_id","Transactions"),
        "loc_updates": fields.One2Many("l2g.loc.update","driver_id","Location Updates"),
        "bank_account_no": fields.Char("Bank Account No."),
        "truck_type_id": fields.Many2One("l2g.truck.type","Truck Type",search=True),
        "plate_no": fields.Char("Plate No.",search=True),
        "jobs": fields.One2Many("l2g.job","driver_id","Jobs"),
        "state": fields.Selection([["new","Awaiting Approval"],["pending","Pending"],["approved","Approved"]],"Status"),
        "refer_code": fields.Char("Referral Code"),
        "refer_by_id": fields.Many2One("l2g.driver","Referred By"),
        "refer_drivers": fields.One2Many("l2g.driver","refer_by_id","Referred Drivers"),
        "hide_wallet": fields.Boolean("Hide Wallet"),
        "hide_price": fields.Boolean("Hide Job Price"),
        "device_tokens": fields.Many2Many("device.token","Devices",function="get_devices"),
        "driver_type": fields.Selection([["normal","Normal"],["planner","Planner"],["planner_driver","Driver"]],"Driver Type",search=True),
        "planner_id": fields.Many2One("l2g.driver","Planner",condition=[["driver_type","=","planner"]]), # XXX: deprecated
        "planner_drivers": fields.One2Many("l2g.driver","planner_id","Planner Drivers"), # XXX: deprecated
        "remarks": fields.Text("Remarks"),
        "contact_id": fields.Many2One("contact","Contact"),
        "manual": fields.Boolean("Manual",function="get_manual"),
        "group_id": fields.Many2One("l2g.driver.group","Driver Group",search=True),
    }
    _defaults={
        "register_date": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
        "state": "new",
    }
    _order="register_date desc,id desc"

    def name_get(self,ids,context={}):
        res=[]
        for obj in self.browse(ids):
            name="%s %s (%s)"%(obj.first_name,obj.last_name,obj.phone)
            res.append((obj.id,name))
        return res

    def get_full_name(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            vals[obj.id]="%s %s"%(obj.first_name,obj.last_name)
        return vals

    def register_driver(self,phone,first_name,last_name,id_no,company=None,region_id=None,image_license=None,image_insurance=None,plate_no=None,truck_type_id=None,refer_code=None,context={}):
        access.set_active_user(1)
        res=get_model("profile").search([["code","=","L2G_DRIVER"]])
        if not res:
            raise Exception("User profile not found")
        profile_id=res[0]
        phone=phone.replace(" ","")
        vals={
            "name": "%s %s"%(first_name,last_name),
            "login": phone,
            "password": "1234", # XXX
            "profile_id": profile_id,
        }
        res=get_model("base.user").search([["login","=ilike",phone]])
        if res:
            user_id=res[0]
            get_model("base.user").write([user_id],vals)
        else:
            user_id=get_model("base.user").create(vals),
        if refer_code:
            res=get_model("l2g.driver").search([["refer_code","=ilike",refer_code]])
            if not res: 
                raise Exception("Invalid referral code")
            refer_by_id=res[0]
            refer_driver=get_model("l2g.driver").browse(refer_by_id)
            refer_driver.add_refer_credits(first_name+" "+last_name,phone)
        else:
            refer_by_id=None
        vals={
            "phone": phone,
            "first_name": first_name,
            "last_name": last_name,
            "id_no": id_no,
            "company": company,
            "region_id": region_id,
            "user_id": user_id,
            "image_license": image_license,
            "image_insurance": image_insurance,
            "plate_no": plate_no,
            "truck_type_id": truck_type_id,
            "refer_by_id": refer_by_id,
        }
        if company:
            res=get_model("l2g.transporter").search([["name","=",company]])
            if res:
                trans_id=res[0]
            else:
                trans_vals={
                    "name": company,
                }
                trans_id=get_model("l2g.transporter").create(trans_vals)
                vals["transporter_id"]=trans_id
            vals["transporter_id"]=trans_id
        res=self.search([["phone","=ilike",phone]])
        if res:
            driver_id=res[0]
            self.write([driver_id],vals)
        else:
            driver_id=self.create(vals)
        driver=self.browse(driver_id)
        user_id=driver.user_id.id
        dbname=database.get_active_db()
        token=utils.new_token(dbname,user_id)
        return {
            "driver_id": driver_id,
            "user_id": user_id,
            "token": token,
        }

    def update_coords(self,driver_id,coords,context={}):
        print("update_coords",driver_id,coords)
        vals={
            "last_coords": coords,
            "last_coords_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.write([driver_id],vals)

    def set_device_token(self,ids,token,context={}):
        print("set_device_token",ids,token)
        obj=self.browse(ids[0])
        obj.write({"device_token": token})

    def get_balance(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            contact=obj.contact_id
            if contact and contact.track_id:
                bal=contact.track_id.balance
            else:
                bal=0
            vals[obj.id]=bal
        return vals

    def update_balances(self,ids,context={}):
        obj=self.browse(ids[0])
        cond=[["driver_id","=",obj.id]]
        bal=0
        for trans in get_model("l2g.trans").search_browse(cond,order="time,id"):
            bal+=trans.amount or 0
            trans.write({"balance":bal})

    def get_last_loc(self,ids,context={}):
        min_t=(datetime.now()-timedelta(seconds=60*15)).strftime("%Y-%m-%d %H:%M:%S")
        db=database.get_connection()
        vals={}
        for obj in self.browse(ids):
            res=db.get("SELECT time,coords FROM l2g_loc_update WHERE driver_id=%s ORDER BY time desc LIMIT 1",obj.id)
            if res:
                coords=res.coords
                t=res.time
                if t<min_t:
                    coords=None
            else:
                coords=None
                t=None
            vals[obj.id]={
                "last_coords": coords,
                "last_coords_time": t,
            }
        return vals

    def approve(self,ids,context={}):
        obj=self.browse(ids[0])
        obj.write({"state":"approved"})

    def create(self,vals,context={}):
        new_id=super().create(vals,context=context)
        self.gen_refer_code([new_id])
        return new_id

    def gen_refer_code(self,ids,context={}):
        code="R%.5d"%random.randint(0,10000)
        for obj in self.browse(ids):
            obj.write({"refer_code":code})

    def add_refer_credits(self,ids,name,phone,context={}):
        obj=self.browse(ids[0])
        vals={
            "driver_id": obj.id,
            "amount": 20,
            "description": "New driver referral (%s, %s)"%(name,phone),
        }
        trans_id=get_model("l2g.trans").create(vals)

    def get_devices(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            if not obj.user_id:
                raise Exception("Missing user for driver %s"%obj.first_name)
            dev_ids=[d.id for d in obj.user_id.device_tokens]
            vals[obj.id]=dev_ids
        return vals

    def clear_bal(self,ids,context={}):
        for obj in self.browse(ids):
            vals={
                "driver_id": obj.id,
                "amount": -obj.balance,
                "description": "Paid",
            }
            trans_id=get_model("l2g.trans").create(vals)

    def copy_to_contact(self,ids,context={}):
        for obj in self.browse(ids):
            if not obj.contact_id:
                vals={
                    "type": "person",
                    "first_name": obj.first_name or "/",
                    "last_name": obj.latst_name or "/",
                }
                contact_id=get_model("contact").create(vals)
                obj.write({"contact_id": contact_id})

    def get_manual(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            if not obj.user_id:
                vals[obj.id]=True
            else:
                vals[obj.id]=False
        return vals

Driver.register()

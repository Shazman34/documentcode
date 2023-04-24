from netforce.model import Model,fields,get_model
from netforce import database
from netforce import access
from netforce import utils
import time
import random

class Customer(Model):
    _name="l2g.customer"
    _string="Customer"
    _name_field="first_name"
    _fields={
        "phone": fields.Char("Phone",required=True,search=True),
        "first_name": fields.Char("First Name",required=True,search=True),
        "last_name": fields.Char("Last Name",required=True,search=True),
        "id_no": fields.Char("ID Number",search=True),
        "company": fields.Char("Company",search=True),
        "region_id": fields.Many2One("l2g.province","Region",search=True),
        "register_date": fields.Date("Register Date",required=True),
        "bookings": fields.One2Many("l2g.booking","customer_id","Bookings"),
        "discount_percent": fields.Decimal("Discount (%)"),
        "tos_accepted": fields.Boolean("Terms Accepted"),
        "user_id": fields.Many2One("base.user","User"),
        "device_token": fields.Char("Device Token"),
        "refer_code": fields.Char("Referral Code"),
        "refer_by_id": fields.Many2One("l2g.customer","Referred By"),
        "refer_customers": fields.One2Many("l2g.customer","refer_by_id","Referred Customers"),
        "bypass_payment": fields.Boolean("Bypass Payment"),
        "bypass_date_check": fields.Boolean("Bypass Booking Date Check"),
        "discount_balance": fields.Decimal("Discount Balance"),
        "pay_term_id": fields.Many2One("payment.term","Payment Terms"),
        "transactions": fields.One2Many("l2g.trans","customer_id","Transactions"),
        "balance": fields.Decimal("Wallet Balance",function="get_balance"),
        "device_tokens": fields.Many2Many("device.token","Devices",function="get_devices"),
        "sales_person_id": fields.Many2One("contact","Sales Person",search=True),
        "remarks": fields.Text("Remarks"),
        "company_id": fields.Many2One("l2g.company","Company",search=True),
        "contact_id": fields.Many2One("contact","Contact"),
        "group_id": fields.Many2One("l2g.driver.group","Driver Group",search=True),
    }
    _defaults={
        "register_date": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    _order="register_date desc,id desc"

    def name_get(self,ids,context={}):
        res=[]
        for obj in self.browse(ids):
            name="%s %s (%s)"%(obj.first_name,obj.last_name,obj.phone)
            res.append((obj.id,name))
        return res

    def register_customer(self,phone,first_name,last_name,id_no,company=None,region_id=None,refer_code=None,context={}):
        access.set_active_user(1)
        res=get_model("profile").search([["code","=","L2G_CUSTOMER"]])
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
            res=get_model("l2g.customer").search([["refer_code","=ilike",refer_code]])
            if not res: 
                raise Exception("Invalid referral code")
            refer_by_id=res[0]
            refer_cust=get_model("l2g.customer").browse(refer_by_id)
            refer_cust.write({"discount_balance":(refer_cust.discount_balance or 0)+50})
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
            "refer_by_id": refer_by_id,
        }
        res=self.search([["phone","=ilike",phone]])
        if res:
            cust_id=res[0]
            self.write([cust_id],vals)
        else:
            cust_id=self.create(vals)
        cust=self.browse(cust_id)
        user_id=cust.user_id.id
        dbname=database.get_active_db()
        token=utils.new_token(dbname,user_id)
        return {
            "customer_id": cust_id,
            "user_id": user_id,
            "token": token,
        }

    def accept_tos(self,ids,context={}):
        obj=self.browse(ids[0])
        obj.write({"tos_accepted":True})

    def set_device_token(self,ids,token,context={}):
        print("set_device_token",ids,token)
        obj=self.browse(ids[0])
        obj.write({"device_token": token})

    def create(self,vals,context={}):
        new_id=super().create(vals,context=context)
        self.gen_refer_code([new_id])
        return new_id

    def gen_refer_code(self,ids,context={}):
        code="R%.5d"%random.randint(0,10000)
        for obj in self.browse(ids):
            obj.write({"refer_code":code})

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
        cond=[["customer_id","=",obj.id]]
        bal=0
        for trans in get_model("l2g.trans").search_browse(cond,order="time,id"):
            bal+=trans.amount or 0
            trans.write({"balance":bal})

    def get_devices(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            dev_ids=[d.id for d in obj.user_id.device_tokens]
            vals[obj.id]=dev_ids
        return vals

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

Customer.register()

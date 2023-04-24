from netforce.model import Model,fields,get_model
import time

class Member(Model):
    _name="gf.member"
    _string="Member"
    _name_field="number"
    _fields={
        "number": fields.Char("Member Number",required=True,search=True),
        "first_name": fields.Char("First Name",required=True,search=True,translate=True),
        "last_name": fields.Char("Last Name",required=True,search=True,translate=True),
        "type": fields.Selection([["guest","Guest"],["member","Member"],["vip","VIP"]],"Type"),
        #"guest_member_id": fields.Many2One("gf.member","Guest Member"),
        "member_fee": fields.Decimal("Member Fee"),
        "discount": fields.Decimal("Discount %"),
        "remark": fields.Text("Remark"),
        "id_no": fields.Char("I.D. No."),
        "country_id": fields.Many2One("country","Country"),
        "passport_no": fields.Char("Passport No."),
        "birth_date": fields.Date("Birth Date"),
        "gender": fields.Selection([["m","Male"],["f","Female"]],"Gender"),
        "marital_status": fields.Selection([["single","Single"],["married","Married"],["divorced","Divorced"],["widowed","Widowed"]],"Marital Status"),
        "address": fields.Text("Address"),
        "city": fields.Char("City"),
        "postal_code": fields.Char("Postal Code"),
        "home_phone": fields.Char("Home Tel",search=True),
        "fax": fields.Char("Fax",search=True),
        "mobile": fields.Char("Mobile",search=True),
        "email": fields.Char("Email",search=True),
        "register_date": fields.Date("Register Date",required=True),
        "start_time": fields.Char("Start Time"),
        "shoe_size": fields.Selection([["40","40"],["41","41"]],"Shoe Size"),
        "shirt_size": fields.Selection([["s","S"],["m","M"],["l","L"],["xl","XL"]],"Shirt Size"),
        "friends": fields.Many2Many("gf.member","Member Friends",reltable="m2m_gf_member_friends",relfield="member1_id",relfield_other="member2_id"),
    }
    _defaults={
        "register_date": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    _order="register_date desc,id desc"

Member.register()

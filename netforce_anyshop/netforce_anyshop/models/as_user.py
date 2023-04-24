from netforce.model import Model,fields,get_model
from netforce import access
import time

class User(Model):
    _name="as.user"
    _string="User"
    _name_field="username"
    _fields={
        "date_add": fields.DateTime("Date Added",required=True,search=True),
        "username": fields.Char("Username",required=True,search=True),
        "first_name": fields.Char("First Name",search=True),
        "last_name": fields.Char("Last Name",search=True),
        "country_id": fields.Many2One("as.country","Country"),
        "region_id": fields.Many2One("as.region","Region"),
        "city_id": fields.Many2One("as.city","City"),
        "description": fields.Text("Description"),
        "photo": fields.File("Photo"),
        "password": fields.Char("Password"),
        "email": fields.Char("Email"),
        "mobile": fields.Char("Mobile"),
        "gender": fields.Selection([["male","Male"],["female","Female"]],"Gender"),
        "birthday": fields.Date("Birthday"),
        "shops": fields.One2Many("as.shop","user_id","Shops"), # XXX: change to shop_id
    }
    _defaults={
        "date_add": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    _order="username"

    def sign_up(self,vals,context={}):
        access.set_active_user(1)
        username=vals.get("username")
        if not username:
            raise Exception("Missing username")
        password=vals.get("password")
        if not password:
            raise Exception("Missing password")
        res=self.search([["username","=ilike",username]])
        if res:
            raise Exception("Username is already in use")
        user_vals={
            "username": username,
            "password": password,
        }
        user_id=self.create(user_vals)
        return {
            "user_id": user_id,
        }

    def login(self,vals,context={}):
        access.set_active_user(1)
        username=vals.get("username")
        if not username:
            raise Exception("Missing username")
        password=vals.get("password")
        if not password:
            raise Exception("Missing password")
        res=self.search([["username","=ilike",username]])
        if not res:
            raise Exception("Invalid username")
        user_id=res[0]
        user=self.browse(user_id)
        if user.password!=password:
            raise Exception("Invalid password")
        return {
            "user_id": user_id,
        }

User.register()

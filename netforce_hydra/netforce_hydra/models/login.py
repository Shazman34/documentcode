from netforce.model import Model,fields,get_model
from netforce import access
from netforce import database
from netforce import utils
from netforce.logger import audit_log
import time
import pyotp

class Login(Model):
    _inherit="login"

    def hx_login(self, login, password, otp_code=None, context={}):
        access.set_active_user(None)
        user_id = get_model("base.user").check_password(login, password)
        if not user_id:
            audit_log("Invalid login (%s)" % login)
            db = database.get_connection()
            db.commit()
            raise Exception("Invalid login")
        try:
            print("login ok", login)
            access.set_active_user(1)
            user = get_model("base.user").browse(user_id)
            if user.profile_id.prevent_login or not user.active:
                raise Exception("User not allowed to login")
            if user.profile_id.require_approve and user.state!="approved":
                raise Exception("User is awaiting approval")
            if user.otp_secret:
                if not otp_code:
                    return {
                        "require_otp": True,
                    }
                totp=pyotp.TOTP(user.otp_secret)
                if not totp.verify(otp_code):
                    raise Exception("Invalid 2FA code")
            t = time.strftime("%Y-%m-%d %H:%M:%S")
            user.write({"lastlog": t})
            profile = user.profile_id
            action = profile.home_action or "account_board"
            dbname=database.get_active_db()
            token = utils.new_token(dbname, user_id)
            db = database.get_connection()
            res = db.get("SELECT * FROM pg_class WHERE relname='settings'")
            settings = get_model("settings").browse(1)
            version = settings.version
            company_id = user.company_id.id or profile.login_company_id.id
            if not company_id:
                res = get_model("company").search([["parent_id", "=", None]])
                if not res:
                    raise Exception("No company found")
                company_id = res[0]
            comp = get_model("company").browse(company_id)
            db_key=user.hx_db_key
            if not db_key:
                raise Exception("Missing database key for user %s"%user.login)
            return {
                "user_id": user_id,
                "token": token,
                "db_key": db_key,
                "company_id": company_id,
                "next": {
                    "type": "url",
                    "url": "/action?name="+action,
                },
            }
        finally:
            access.set_active_user(user_id)
            audit_log("Login")

    def hx_signup(self,data,context={}):
        access.set_active_user(1)
        login=data.get("username")
        if not login:
            raise Exception("Missing login")
        login=login.lower()
        email=data.get("email")
        if not email:
            raise Exception("Missing email")
        email=email.lower()
        res=get_model("base.user").search([["login","=",login]])
        if res:
            raise Exception("User already registered with same login")
        res=get_model("base.user").search([["email","=",email]])
        if res:
            raise Exception("User already registered with same email")
        password=data.get("password")
        if not password:
            raise Exception("Missing password")
        if len(password)<6:
            raise Exception("Password must be at least 6 characters")
        first_name=data.get("first_name")
        if not first_name:
            raise Exception("Missing first name")
        last_name=data.get("last_name")
        if not last_name:
            raise Exception("Missing last name")
        birth_date=data.get("birth_date")
        if not birth_date:
            raise Exception("Missing birth date")
        gender=data.get("gender")
        if not gender:
            raise Exception("Missing gender")
        nationality=data.get("nationality")
        if not nationality:
            raise Exception("Missing nationality")
        country=data.get("country")
        if not country:
            raise Exception("Missing country")
        phone=data.get("phone")
        if not phone:
            raise Exception("Missing phone")
        res=get_model("country").search([["code","=",country]])
        if not res:
            raise Exception("Country not found: %s"%country)
        country_id=res[0]
        vals={
            "type": "person",
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "gender": gender,
            "birth_date": birth_date,
            "country_id": country_id,
        }
        contact_id=get_model("contact").create(vals)
        res=get_model("profile").search([["code","=","HX_USER"]])
        if not res:
            raise Exception("Missing profile")
        profile_id=res[0]
        db_key=utils.gen_passwd(20)
        res=get_model("hx.plan").search([["name","=","Free"]])
        if not res:
            raise Exception("Missing plan")
        plan_id=res[0]
        vals={
            "login": login,
            "password": password,
            "email": email,
            "profile_id": profile_id,
            "name": "%s %s"%(first_name,last_name),
            "first_name": first_name,
            "last_name": last_name,
            "contact_id": contact_id,
            "hx_db_key": db_key,
            "hx_plan_id": plan_id,
            "state": "wait_approve",
        }
        user_id=get_model("base.user").create(vals)
        dbname=database.get_active_db()
        token = utils.new_token(dbname, user_id)
        get_model("base.user").trigger([user_id],"signup")
        return {
            "user_id": user_id,
            "token": token,
            "username": login,
            "db_key": db_key,
        }

    def hx_send_reset_code(self,data,context={}):
        print("hx_send_reset_code",data)
        email=data.get("email")
        if not email:
            raise Exception("Missing email")
        self.request_reset_password(email)

    def hx_reset_pass(self,data,context={}):
        email=data.get("email")
        if not email:
            raise Exception("Missing email")
        reset_code=data.get("reset_code")
        if not reset_code:
            raise Exception("Missing reset_code")
        password=data.get("password")
        if not password:
            raise Exception("Missing password")
        self.reset_password(email,reset_code,password)

Login.register()

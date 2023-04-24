from netforce.model import Model,fields,get_model
from netforce import access
import xmlrpc.client
from netforce import database
from netforce import utils
import os
import base64

reserved_domains=["www","mail","admin","erp","auth","backend","app","template"]

class Auth(Model):
    _name="auth.api"
    _store=False

    def sign_up(self,first_name,last_name,email,password,company,domain,context={}):
        print("#"*80)
        print("sign_up",first_name,last_name,email,password,company)
        access.set_active_user(1)
        if not first_name:
            raise Exception("Missing first name")
        if not last_name:
            raise Exception("Missing last name")
        if not email:
            raise Exception("Missing email")
        if not utils.check_email_syntax(email):
            raise Exception("Invalid email syntax")
        if not password:
            raise Exception("Missing password")
        if not company:
            raise Exception("Missing company name")
        if not domain:
            raise Exception("Missing domain")
        if not utils.check_domain_syntax(domain):
            raise Exception("Invalid domain")
        if len(domain)<5:
            raise Exception("Domain has to be at least 5 characters")
        res=get_model("auth.company").search([["domain","=",domain]])
        if res:
            raise Exception("Domain is already in use")
        vals={
            "name": company,
            "domain": domain,
        }
        company_id=get_model("auth.company").create(vals)
        database.set_active_db("template1")
        db=database.get_connection()
        db.execute("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='nfo_template'");
        dbname="nfo_"+domain.replace("-","_")
        db.execute("COMMIT");
        db.execute("CREATE DATABASE %s WITH TEMPLATE nfo_template"%dbname)
        database.set_active_db(dbname)
        with database.Transaction():
            vals={
                "name": first_name+" "+last_name,
                "login": email,
                "password": password,
                "email": email,
            }
            get_model("base.user").write([1],vals)
            vals={
                "name": company,
            }
            get_model("company").write([1],vals)
        token = utils.new_token(dbname,1)
        return {
            "user_id": 1,
            "token": token,
            "company_id": 1,
            "action": "account_board",
        }

Auth.register()

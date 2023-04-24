from netforce.model import Model,fields,get_model
from netforce import access

class Interface(Model):
    _name="xb.interface"
    _store=False

    def sign_up(self,name,email,password,context={}):
        access.set_active_user(1)
        res=get_model("base.user").search([["login","=ilike",email]])
        if res:
            raise Exception("Email is already registered")
        res=get_model("profile").search([["name","=","XBank User"]])
        if not res:
            raise Exception("Profile not found")
        profile_id=res[0]
        vals={
            "name": name,
        }
        acc_id=get_model("xb.account").create(vals)
        vals={
            "name": name,
            "login": email,
            "password": password,
            "email": email,
            "profile_id": profile_id,
            "xb_account_id": acc_id,
        }
        user_id=get_model("base.user").create(vals)
        return {
            "user_id": user_id,
        }

    def login(self,email,password,context={}):
        access.set_active_user(1)
        user_id=get_model("base.user").check_password(email,password)
        if not user_id:
            raise Exception("Invalid login")
        user=get_model("base.user").browse(user_id)
        return {
            "user_id": user_id,
        }

    def withdraw(self,currency,amount,address,context={}):
        user_id=context["user_id"] # XXX
        user=get_model("base.user").browse(user_id)
        vals={
            "account_id": user.xb_account_id.id,
            "currency": currency,
            "amount": amount,
            "address": address,
        }
        access.set_active_user(1)
        wd_id=get_model("xb.withdraw").create(vals)
        get_model("xb.withdraw").confirm([wd_id])
        wd=get_model("xb.withdraw").browse(wd_id)
        return {
            "number": wd.number,
            "txid": wd.txid,
        }

    def new_address(self,currency,context={}):
        user_id=context["user_id"] # XXX
        user=get_model("base.user").browse(user_id)
        acc=user.xb_account_id
        access.set_active_user(1)
        if currency=="xbt":
            addr_id=acc.new_addr_xbt()
        elif currency=="ltc":
            addr_id=acc.new_addr_ltc()
        elif currency=="eth":
            addr_id=acc.new_addr_eth()
        else:
            raise Exception("Invalid currency")
        addr=get_model("xb.address").browse(addr_id)
        return {
            "address": addr.address,
        }

Interface.register()

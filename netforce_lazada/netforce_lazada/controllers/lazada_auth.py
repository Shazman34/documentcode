from netforce.controller import Controller
from netforce.model import  Model, fields, get_model
from netforce import database
from netforce import access
from netforce import config
import json
import requests
import hashlib
import hmac
import time

class Auth(Controller):
    _path="/lazada_auth"

    def get(self):
        print("lazada_auth")
        record_id=int(self.get_argument("record_id"))
        print("record id", record_id)
        database.set_active_db("main_asad")
        access.set_active_user(1)
        with database.Transaction():
            db = database.get_connection()
            account = get_model("lazada.account").search_browse([["id", "=", record_id]])
        app_key = account[0].shop_idno
        app_secret = account[0].auth_code
        print("app_key", app_key)
        print("app_secret", app_secret)
        # code = "0_111458_38XrApiT4XeyKOONjNYp8U5g31476"
        base_url = "https://auth.lazada.com/rest"
        path = "/auth/token/create"
        timest = int(time.time() * 1000)
        app_key = app_key
        app_secret = app_secret
        code=self.get_argument("code")
        sign_method = "sha256"
        base_url = base_url
        path = path
        base_string = "%sapp_key%sapp_secret%scode%ssign_method%stimestamp%s" % (
            path, app_key, app_secret, code, sign_method, timest)
        sign = hmac.new(app_secret.encode(encoding="utf-8"), base_string.encode(encoding="utf-8"),
                        hashlib.sha256).hexdigest().upper()
        headers = {"Content-Type": "application/json"}
        body = {"app_key": app_key, "app_secret": app_secret, "code": code}
        params = "?app_key=%s&app_secret=%s&code=%s&timestamp=%s&sign_method=%s&sign=%s" % (
            app_key, app_secret, code, timest, sign_method, sign)
        url = base_url + path + params
        req = requests.post(url, json=body, headers=headers)
        res = req.json()
        print("response111", res)
        account.write({"token": res["access_token"]})
        account.write({"refresh_token": res["refresh_token"]})
        db.commit()
        redirect_url2 = "http://newfront-dev.smartb.co/action?name=lazada_account"
        self.redirect(redirect_url2)


Auth.register()

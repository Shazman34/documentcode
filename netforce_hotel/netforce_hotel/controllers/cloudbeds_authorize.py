from netforce.controller import Controller
from netforce.model import get_model
from netforce import database
from netforce import access

class Auth(Controller):
    _path="/cloudbeds_authorize"

    def get(self):
        access.set_active_user(1)
        dbname=self.get_argument("db")
        code=self.get_argument("code")
        database.set_active_db(dbname)
        with database.Transaction():
            obj=get_model("ht.sync").browse(1)
            obj.write({"oauth_code": code})
            obj.get_token()
            self.redirect("https://grace.netforce.com/action?name=ht_sync")

Auth.register()

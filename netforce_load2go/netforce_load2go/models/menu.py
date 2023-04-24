from netforce.model import Model,get_model,fields
from netforce import access

class Menu(Model):
    _inherit="menu"

    def get_menu_info(self,context={}):
        # print("M"*80)
        # print("get_menu_info")
        user_id=access.get_active_user()
        # print("user_id",user_id)
        vals=super().get_menu_info()
        n1=get_model("l2g.job").get_num_unread() or 0
        n2=get_model("chat.message").get_num_unread() or 0
        rate_job_id=get_model("l2g.job").get_rate_job_id()
        vals["jobs"]={
            "badge": n1,
            "tooltip": "You have %s unread jobs"%n1,
        }
        vals["chat"]={
            "badge": n2,
            "tooltip": "You have %s unread chat messages"%n2,
        }
        vals["rate_job_id"]=rate_job_id
        vals["user_id"]=user_id
        print("?"*80)
        print("?"*80)
        print("?"*80)
        print("L2G get_menu_info %s"%vals)
        return vals

Menu.register()

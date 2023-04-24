from netforce.model import Model,get_model,fields
from netforce import access

class ChatChannel(Model):
    _inherit="chat.channel"

    """
    def get_filter(self,access_type,context={}):
        user_id=access.get_active_user()
        if not user_id:
            return False
        if user_id==1:
            return True
        prof_code=access.get_active_profile_code()
        if prof_code=="L2G_CUSTOMER":
            return [["code","=","CUSTOMER_SUPPORT"]]
        elif prof_code=="L2G_DRIVER":
            return [["code","in",["DRIVER_SUPPORT","DRIVER_CHAT"]]]
        else:
            return True
    """

ChatChannel.register()

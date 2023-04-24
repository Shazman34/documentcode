from netforce.model import Model,get_model,fields
from netforce import access

class ChatMessage(Model):
    _inherit="chat.message"

    def get_filter(self,access_type,context={}):
        # print("ChatMessage.get_filter",access_type)
        user_id=access.get_active_user()
        # print("user_id",user_id)
        if not user_id:
            return ["id","=",0] # XXX
        if user_id==1:
            return True
        prof_code=access.get_active_profile_code()
        # print("prof_code",prof_code)
        if prof_code=="L2G_CUSTOMER":
            return ["or",["user_id","=",user_id],["to_user_id","=",user_id]]
        elif prof_code=="L2G_DRIVER":
            return ["or",["user_id","=",user_id],["to_user_id","=",user_id],["channel_id.code","=","DRIVER_CHAT"]]
        else:
            return True

    def create(self,vals,context={}):
        new_id=super().create(vals,context=context)
        obj=self.browse(new_id)
        user=obj.to_user_id
        if user:
            for dev in user.device_tokens:
                msg=obj.message or ""
                vals={
                    "device_id": dev.id,
                    "title": "New message",
                    "message": msg,
                    "state": "to_send",
                }
                notif_id=get_model("push.notif").create(vals)
                get_model("push.notif").send([notif_id]) # XXX
        return new_id

ChatMessage.register()

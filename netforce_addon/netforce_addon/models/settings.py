from netforce.model import Model,fields,get_model
from netforce import database
try:
    import stripe
    stripe.api_key="sk_test_u42PxZSuDUEPiBbcP05hsvGb"
except:
    print("WARNING: failed to import stripe")

class Settings(Model):
    _inherit="settings"
    _fields={
        "bill_num_users": fields.Integer("Billable Users",function="get_num_users"),
        "bill_num_addons": fields.Integer("Installed Addons",function="get_num_addons"),
        "bill_plan_id": fields.Many2One("price.plan","Price Plan"),
        "bill_plan_cost": fields.Decimal("Price Plan Cost (USD)",function="get_month_cost",function_multi=True),
        "bill_addon_cost": fields.Decimal("Extra Addon Cost (USD)",function="get_month_cost",function_multi=True),
        "bill_month_cost": fields.Decimal("Total Monthly Cost (USD)",function="get_month_cost",function_multi=True),
        "bill_balance": fields.Decimal("Account Balance (USD)",function="get_bill_balance"),
        "bill_cust_id": fields.Char("Customer ID"),
    }

    def get_num_users(self,ids,context={}):
        obj=self.browse(ids[0])
        vals={}
        res=get_model("base.user").search(["or",["profile_id.prevent_login","=",False],["profile_id.prevent_login","=",None]])
        vals[obj.id]=len(res)
        return vals

    def get_num_addons(self,ids,context={}):
        obj=self.browse(ids[0])
        vals={}
        res=get_model("addon").search([["state","=","installed"]])
        vals[obj.id]=len(res)
        return vals

    def get_month_cost(self,ids,context={}):
        obj=self.browse(ids[0])
        base_price=5
        vals={}
        plan_price=(obj.bill_plan_id.price or 0) if obj.bill_plan_id else 0
        addon_amount=0
        for addon in get_model("addon").search_browse([["state","=","installed"]]):
            addon_amount+=addon.plan_price
        vals[obj.id]={
            "bill_plan_cost": plan_price,
            "bill_addon_cost": addon_amount,
            "bill_month_cost": plan_price+addon_amount,
        }
        return vals

    def get_bill_balance(self,ids,context={}):
        obj=self.browse(ids[0])
        vals={}
        bal=0
        for period in get_model("bill.period").search_browse([]):
            bal+=(period.amount_paid or 0)-(period.amount_bill or 0)
        vals[obj.id]=bal
        return vals

    def change_price_plan(self,ids,context={}):
        settings=self.browse(1)
        if not settings.bill_cust_id:
            self.create_customer()

    def create_customer(self,context={}):
        settings=self.browse(1)
        if settings.bill_cust_id:
            raise Exception("Customer already created")
        schema=database.get_active_schema()
        customer=stripe.Customer.create(description=schema)
        settings.write({"bill_cust_id":customer.id})

Settings.register()

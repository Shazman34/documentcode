from netforce.model import Model,fields,get_model
from netforce import access
from netforce import database
from datetime import *
import time
from decimal import *
import requests

class CustOrder(Model):
    _name="gt.cust.order"
    _string="Customer Order"
    _audit_log=True
    _name_field="number"
    _fields={
        "number": fields.Char("Number",required=True,search=True),
        "create_time": fields.DateTime("Create Time",required=True,search=True,readonly=True),
        "order_time": fields.DateTime("Order Time",required=True,search=True),
        "customer_id": fields.Many2One("gt.customer","Customer",required=True,search=True),
        "type": fields.Selection([["buy","Buy"],["sell","Sell"]],"Order Type",required=True,search=True),
        "execution": fields.Selection([["instant","Instant"],["limit","Limit"],["stop","Stop"]],"Execution",required=True,search=True),
        "product": fields.Selection([["96","96.5%"],["96_mini","96.5% MINI"],["99","99.99% LBMA"]],"Product",required=True,search=True),
        "product_label": fields.Char("Product Label",function="get_product_label"),
        "qty": fields.Decimal("Qty",required=True),
        "uom": fields.Selection([["baht","Bg"],["kg","Kg"]],"UoM",function="get_uom"),
        "unit_price": fields.Decimal("Unit Price",required=True),
        "amount": fields.Decimal("Total Amount",function="get_amount"),
        "state": fields.Selection([["draft","Draft"],["pending","Pending"],["confirmed","Confirmed"],["matched","Matched"],["done","Completed"],["canceled","Canceled"]],"Status",required=True,search=True),
        "confirm_time": fields.DateTime("Confirm Time",readonly=True),
        "done_time": fields.DateTime("Completed Time",readonly=True),
        "cancel_time": fields.DateTime("Cancel Time",readonly=True),
        "payment_id": fields.Many2One("gt.cust.payment","Payment"), # XXX: deprecated
        "delivery_id": fields.Many2One("gt.cust.delivery","Delivery"),
        "float_pl": fields.Decimal("Floating P/L",function="get_float_pl"),
        "match_id": fields.Many2One("gt.cust.match","Match"),
        "late_days": fields.Decimal("Late Payment Days",function="get_late_days"),
        "late_fee": fields.Decimal("Late Payment Fee"),
        "no_late_fee": fields.Boolean("Waive Late Fee"),
        "can_cancel": fields.Boolean("Can Cancel",function="get_can_cancel"),
        "payment_lines": fields.One2Many("gt.cust.payment.line","order_id","Payment Lines"),
        "delivery_lines": fields.One2Many("gt.cust.delivery.line","order_id","Delivery Lines"),
        "amount_paid": fields.Decimal("Paid Amount",function="get_amount_paid",function_multi=True),
        "amount_due": fields.Decimal("Due Amount",function="get_amount_paid",function_multi=True),
        "qty_paid": fields.Decimal("Paid Qty",function="get_amount_paid",function_multi=True),
        "qty_delivered": fields.Decimal("Delivered Qty",function="get_qty_delivered"),
        "spot_price": fields.Decimal("Spot Price",readonly=True),
        "usd_thb_rate": fields.Decimal("USD/THB Rate",readonly=True),
        "due_date": fields.Date("Due Date",function="get_due_date",function_multi=True),
        "overdue": fields.Boolean("Overdue",function="get_due_date",function_multi=True),
        "qty_sign": fields.Decimal("Qty Sign",function="get_qty_sign"),
        "amount_sign": fields.Decimal("Amount Sign",function="get_amount_sign"),
        "expire_time": fields.DateTime("Expire Time",readonly=True),
        "active": fields.Boolean("Active"),
    }
    _order="order_time desc"

    def _get_number(self, context={}):
        settings = get_model("gt.settings").browse(1)        
        seq_id = settings.seq_cust_order_id.id
        if not seq_id:
            return None
        while 1:
            num = get_model("sequence").get_next_number(seq_id, context=context)
            if not num:
                return None
            user_id = access.get_active_user()
            access.set_active_user(1)
            res = self.search([["number", "=", num]])
            access.set_active_user(user_id)
            if not res:
                return num
            get_model("sequence").increment_number(seq_id, context=context)

    _defaults={
        "order_time": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
        "number": _get_number,
        "state": "draft",
        "execution": "instant",
        "active": True,
    }

    def delete(self,ids,context={}):
        if not context.get("force_delete"):
            for obj in self.browse(ids):
                if obj.state not in ("draft","canceled"):
                    raise Exception("Can not delete orders in this state")
        super().delete(ids,context=context)

    def force_delete(self,ids,context={}):
        ctx=context.copy()
        ctx["force_delete"]=True
        super().delete(ids,context=ctx)

    def get_amount(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            if obj.product=="96":
                amt=obj.qty*obj.unit_price
            elif obj.product=="99":
                amt=round(obj.qty*Decimal(65.6)*obj.unit_price)
            elif obj.product=="96_mini":
                amt=obj.qty*obj.unit_price
            else:
                raise Exception("Invalid product")
            vals[obj.id]=amt
        return vals

    def place_order_instant(self,product,order_type,qty,pin,context={}):
        settings=get_model("gt.settings").browse(1)
        if settings.market_state!="open":
            raise Exception("Market is closed")
        if product=="96_mini" and settings.market_state_96_mini!="open":
            raise Exception("Market is closed for 96.5% MINI")
        if not product:
            raise Exception("Missing product")
        if not order_type:
            raise Exception("Missing order type")
        if not qty:
            raise Exception("Missing qty")
        if not pin:
            raise Exception("Missing PIN")
        user_id=access.get_active_user()
        if not user_id:
            raise Exception("Missing user")
        user=get_model("base.user").browse(user_id)
        if not user.pin_code:
            raise Exception("User has no PIN") 
        if pin!=user.pin_code:
            raise Exception("Invalid PIN")
        cust_id=user.gt_customer_id.id
        if not cust_id:
            raise Exception("Customer not found")
        get_model("gt.price").load_prices()
        prices=get_model("gt.price").get_prices()
        if product=="96":
            if order_type=="buy":
                price=prices["cust_96_ask"]
            elif order_type=="sell":
                price=prices["cust_96_bid"]
        elif product=="99":
            if order_type=="buy":
                price=prices["cust_99_ask"]
            elif order_type=="sell":
                price=prices["cust_99_bid"]
        elif product=="96_mini":
            if order_type=="buy":
                price=prices["cust_96_mini_ask"]
            elif order_type=="sell":
                price=prices["cust_96_mini_bid"]
        else:
            raise Exception("Invalid product")
        vals={
            "customer_id": cust_id,
            "product": product,
            "type": order_type,
            "execution": "instant",
            "qty": qty,
            "unit_price": price,
            "state": "draft",
            "confirm_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        order_id=self.create(vals)
        order=self.browse(order_id)
        order.confirm()
        return {
            "order_id": order_id,
            "order_num": order.number,
        }

    def place_order_pending(self,product,price,order_type,execution,qty,pin,context={}):
        settings=get_model("gt.settings").browse(1)
        price=Decimal(price) # XXX
        if settings.market_state!="open":
            raise Exception("Market is closed")
        if product=="96_mini" and settings.market_state_96_mini!="open":
            raise Exception("Market is closed for 96.5% MINI")
        if not product:
            raise Exception("Missing product")
        if not price:
            raise Exception("Missing price")
        if not order_type:
            raise Exception("Missing order type")
        if not execution:
            raise Exception("Missing execution")
        if not qty:
            raise Exception("Missing qty")
        if not pin:
            raise Exception("Missing PIN")
        user_id=access.get_active_user()
        user=get_model("base.user").browse(user_id)
        if not user.pin_code:
            raise Exception("User has no PIN") 
        if pin!=user.pin_code:
            raise Exception("Invalid PIN")
        cust_id=user.gt_customer_id.id
        if not cust_id:
            raise Exception("Customer not found")
        get_model("gt.price").load_prices()
        prices=get_model("gt.price").get_prices()
        if product=="96":
            if order_type=="buy":
                mkt_price=prices["cust_96_ask"]
            elif order_type=="sell":
                mkt_price=prices["cust_96_bid"]
        elif product=="99":
            if order_type=="buy":
                mkt_price=prices["cust_99_ask"]
            elif order_type=="sell":
                mkt_price=prices["cust_99_bid"]
        elif product=="96_mini":
            if order_type=="buy":
                mkt_price=prices["cust_96_mini_ask"]
            elif order_type=="sell":
                mkt_price=prices["cust_96_mini_bid"]
        else:
            raise Exception("Invalid product")
        if order_type=="buy":
            if execution=="limit":
                if price>=mkt_price:
                    raise Exception("Buy limit price should be lower than market price")
            elif execution=="stop":
                if price<=mkt_price:
                    raise Exception("Buy stop price should be higher than market price")
        elif order_type=="sell":
            if execution=="limit":
                if price<=mkt_price:
                    raise Exception("Sell limit price should be higher than market price")
            elif execution=="stop":
                if price>=mkt_price:
                    raise Exception("Sell stop price should be lower than market price")
        vals={
            "customer_id": cust_id,
            "product": product,
            "type": order_type,
            "execution": execution,
            "qty": qty,
            "unit_price": price,
            "state": "draft",
        }
        order_id=self.create(vals)
        order=self.browse(order_id)
        order.pending()
        return {
            "order_id": order_id,
            "order_num": order.number,
        }

    def confirm(self,ids,context={}):
        for obj in self.browse(ids):
            if obj.state not in ("pending","draft"):
                raise Exception("Invalid order state")
            prices=get_model("gt.price").get_prices()
            vals={
                "state": "confirmed",
                "confirm_time":time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            if obj.type=="buy":
                vals["spot_price"]=prices["spot_ask"]
                vals["usd_thb_rate"]=prices["usd_thb_ask"]
            elif obj.type=="sell":
                vals["spot_price"]=prices["spot_bid"]
                vals["usd_thb_rate"]=prices["usd_thb_bid"]
            obj.write(vals)
            obj.customer_id.check_account()
            obj.trigger("confirmed")

    def pending(self,ids,context={}):
        settings=get_model("gt.settings").browse(1)
        for obj in self.browse(ids):
            if obj.state!="draft":
                raise Exception("Invalid order state")
            if obj.execution not in ("limit","stop"):
                raise Exception("Invalid execution type")
            if not settings.pending_cancel_time:
                raise Exception("Missing pending expiry time")
            exp_t=time.strftime("%Y-%m-%d")+" "+settings.pending_cancel_time+":00"
            obj.write({"state": "pending","expire_time":exp_t})
            obj.trigger("new_pending")
            params={
                "method": "create_order",
                "order_no": obj.number,
                "create_time": obj.create_time,
                "product": "TR_"+obj.product,
                "type": obj.type,
                "execution": obj.execution,
                "qty": str(obj.qty),
                "price": str(obj.unit_price),
                "notif_url": "https://trgold-backend.netforce.com/gt_notif_confirm",
            }
            res=requests.post("https://exchange.netforce.com/api",json=params)
            if res.status_code!=200:
                raise Exception("Failed to send order to exchange: %s"%res.text)

    def match(self,ids,context={}):
        cust_id=None
        prod=None
        for obj in self.browse(ids):
            if obj.state!="confirmed":
                raise Exception("Invalid order state")
            if cust_id is None:
                cust_id=obj.customer_id.id
            else:
                if cust_id!=obj.customer_id.id:
                    raise Exception("Orders have different customers")
            if prod is None:
                prod=obj.product
            else:
                if prod!=obj.product:
                    raise Exception("Orders have different products")
        vals={
            "customer_id": cust_id,
            "product": prod,
        }
        match_id=get_model("gt.cust.match").create(vals)
        match=get_model("gt.cust.match").browse(match_id)
        self.write(ids,{"match_id": match_id})
        self.update_state(ids)
        if prod=="96":
            if match.buy_96_qty!=match.sell_96_qty:
                raise Exception("Total buy and sell qty are different (%s / %s)"%(match.buy_96_qty,match.sell_96_qty))
        elif prod=="99":
            if match.buy_99_qty!=match.sell_99_qty:
                raise Exception("Total buy and sell qty are different (%s / %s)"%(match.buy_99_qty,match.sell_99_qty))
        return {
            "flash": "Matched %d orders with PL %.0f"%(len(ids),match.net_thb),
        }

    def set_done(self,ids,context={}):
        cust_ids=[]
        for obj in self.browse(ids):
            if obj.state not in ("confirmed","matched"):
                raise Exception("Invalid order state")
            obj.write({"state": "done"})
            cust_ids.append(obj.customer_id.id)
        cust_ids=list(set(cust_ids))
        if cust_ids and not context.get("no_check_account"):
            get_model("gt.customer").check_account(cust_ids)

    def update_price(self,context={}):
        settings=get_model("gt.settings").browse(1)
        data=context["data"]
        product=data["product"]
        type=data["type"]
        price=None
        if product=="96":
            if type=="buy":
                price=settings.cust_96_ask
            elif type=="sell":
                price=settings.cust_96_bid
        elif product=="99":
            if type=="buy":
                price=settings.cust_99_ask
            elif type=="sell":
                price=settings.cust_99_bid
        data["unit_price"]=price
        return data

    def copy_to_payment(self,ids,context={}):
        cust_id=None
        amt=0
        for obj in self.browse(ids):
            if obj.state not in ("confirmed","matched","done"):
                raise Exception("Invalid order state")
            if cust_id is None:
                cust_id=obj.customer_id.id
            else:
                if cust_id!=obj.customer_id.id:
                    raise Exception("Orders belong to different customers")
            if obj.type=="buy":
                amt+=obj.amount+(obj.late_fee or 0)
            elif obj.type=="sell":
                amt-=obj.amount-(obj.late_fee or 0)
        vals={
            "customer_id": cust_id,
            "direction": amt>0 and "in" or "out",
            "lines": [],
        }
        for obj in self.browse(ids):
            if obj.type=="buy":
                amt=obj.amount+(obj.late_fee or 0)
            else:
                amt=-(obj.amount-(obj.late_fee or 0))
            if vals["direction"]=="out":
                amt=-amt
            line_vals={
                "order_id": obj.id,
                "qty": obj.qty,
                "amount": amt,
            }
            vals["lines"].append(("create",line_vals))
        pmt_id=get_model("gt.cust.payment").create(vals)
        return {
            "next": {
                "name": "gt_cust_payment",
                "mode": "form",
                "active_id": pmt_id,
            },
        }

    def copy_to_delivery(self,ids,context={}):
        cust_id=None
        lines=[]
        order_type=None
        for obj in self.browse(ids):
            if obj.state not in ("confirmed","matched","done"):
                raise Exception("Invalid order state")
            if cust_id is None:
                cust_id=obj.customer_id.id
            else:
                if cust_id!=obj.customer_id.id:
                    raise Exception("Orders belong to different customers")
            if order_type is None:
                order_type=obj.type
            else:
                if order_type!=obj.type:
                    raise Exception("Orders have different types")
            lines.append(("create",{
                "order_id": obj.id,
                "product": obj.product,
                "qty": abs(obj.qty),
            }))
        vals={
            "customer_id": cust_id,
            "direction": order_type=="buy" and "out" or "in",
            "lines": lines,
        }
        deliv_id=get_model("gt.cust.delivery").create(vals)
        return {
            "next": {
                "name": "gt_cust_delivery",
                "mode": "form",
                "active_id": deliv_id,
            },
        }

    def to_draft(self,ids,context={}):
        for obj in self.browse(ids):
            obj.write({"state": "draft"})

    def get_float_pl(self,ids,context={}):
        prices=get_model("gt.price").get_prices()
        vals={}
        for obj in self.browse(ids):
            pl=None
            if obj.state in ("confirmed","matched","done"):
                if obj.type=="buy":
                    if obj.product=="96":
                        pl=(prices["cust_96_bid"]-obj.unit_price)*obj.qty
                    elif obj.product=="99":
                        pl=(prices["cust_99_bid"]-obj.unit_price)*obj.qty*Decimal(65.6)
                elif obj.type=="sell":
                    if obj.product=="96":
                        pl=(obj.unit_price-prices["cust_96_ask"])*obj.qty
                    elif obj.product=="99":
                        pl=(obj.unit_price-prices["cust_99_ask"])*obj.qty*Decimal(65.6)
            vals[obj.id]=pl
        return vals

    def get_late_days(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            if obj.state in ("confirmed","matched") and obj.confirm_time:
                if obj.match_id:
                    match_t=datetime.strptime(obj.match_id.create_time,"%Y-%m-%d %H:%M:%S")
                    days=(match_t.date()-datetime.strptime(obj.confirm_time,"%Y-%m-%d %H:%M:%S").date()).days
                else:
                    days=(datetime.today().date()-datetime.strptime(obj.confirm_time,"%Y-%m-%d %H:%M:%S").date()).days
                payment_days=obj.customer_id.categ_id.payment_days or 0
                late_days=max(0,days-payment_days)
            else:
                late_days=0
            vals[obj.id]=late_days
        return vals

    def update_late_fees(self,context={}):
        print("update_late_fees")
        for obj in self.search_browse([["state","in",["confirmed","matched"]]]):
            late_days=obj.late_days
            if late_days:
                day_fee=obj.customer_id.categ_id.late_pay_fee or 0
                if obj.product=="96":
                    fee=late_days*day_fee*obj.qty
                elif obj.product=="99":
                    fee=round(late_days*day_fee*obj.qty*Decimal("65.6"))
            else:
                fee=0
            if not obj.no_late_fee:
                print("%s => %s"%(obj.number,obj.late_fee))
                obj.write({"late_fee": fee})

    def get_can_cancel(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            vals[obj.id]=obj.state=="pending"
        return vals

    def cancel_order(self,ids,context={}):
        for obj in self.browse(ids):
            if obj.state!="pending":
                raise Exception("Invalid status")
            obj.write({"state":"canceled"})
            params={
                "method": "delete_order",
                "product": "TR_"+obj.product,
                "order_no": obj.number,
            }
            res=requests.post("https://exchange.netforce.com/api",json=params)
            if res.status_code!=200:
                raise Exception("Failed to remove order from exchange: %s"%res.text)

    def get_amount_paid(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            amt_paid=0
            qty_paid=0
            for line in obj.payment_lines:
                if line.payment_id.state=="done":
                    amt_paid+=line.amount
                    qty_paid+=line.qty or 0
            if obj.type=="buy":
                total=obj.amount+(obj.late_fee or 0)
            elif obj.type=="sell":
                total=obj.amount-(obj.late_fee or 0)
            amt_due=total-amt_paid
            vals[obj.id]={
                "amount_paid": amt_paid,
                "amount_due": amt_due,
                "qty_paid": qty_paid,
            }
        return vals

    def get_qty_delivered(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            qty=0
            for line in obj.delivery_lines:
                if line.delivery_id.state=="done":
                    qty+=line.qty
            vals[obj.id]=qty
        return vals

    def get_due_date(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            today=datetime.today()
            days=obj.customer_id.categ_id.payment_days
            if obj.state in ("confirmed","matched") and  obj.confirm_time:
                due_date=(datetime.strptime(obj.confirm_time,"%Y-%m-%d %H:%M:%S")+timedelta(days=int(days))).strftime("%Y-%m-%d")
            else:
                due_date=None
            vals[obj.id]={
                "due_date": due_date,
                "overdue": due_date<today.strftime("%Y-%m-%d") if due_date else None,
            }
        return vals

    def update_state(self,ids,context={}):
        for obj in self.browse(ids):
            if obj.state in ("confirmed","matched","done"):
                if obj.amount_due==0:
                    new_state="done"
                elif obj.match_id:
                    new_state="matched"
                else:
                    new_state="confirmed"
                obj.write({"state": new_state})

    def get_uom(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            uom=None
            if obj.product=="96":
                uom="Bg"
            elif obj.product=="99":
                uom="Kg"
            vals[obj.id]=uom
        return vals

    def get_qty_sign(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            vals[obj.id]=obj.qty if obj.type=="buy" else -obj.qty
        return vals

    def get_amount_sign(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            vals[obj.id]=-obj.amount if obj.type=="buy" else obj.amount
        return vals

    def cancel_expired_pending(self,context={}):
        print("cancel_expired_pending")
        t=time.strftime("%Y-%m-%d %H:%M:%S")
        n=0
        for obj in self.search_browse([["state","=","pending"],["expire_time","<=",t]]):
            obj.cancel_order()
            n+=1
        return "%d pending orders canceled"%n

    def get_orders_per_day(self, context={}):
        db=database.get_connection()
        min_d=(datetime.today()-timedelta(days=90)).strftime("%Y-%m-%d")
        res=db.query("SELECT date_trunc('day',order_time) AS day,COUNT(*) AS num_orders FROM gt_cust_order WHERE order_time>=%s GROUP BY day ORDER BY day",min_d);
        data = []
        for r in res:
            d=datetime.strptime(r.day[:10],"%Y-%m-%d")
            data.append([time.mktime(d.timetuple()) * 1000, r.num_orders])
        return data

    def get_product_label(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            s=None
            if obj.product=="96":
                s="96.5%"
            elif obj.product=="99":
                s="99.99%"
            elif obj.product=="96_mini":
                s="96.5% MINI"
            vals[obj.id]=s
        return vals

CustOrder.register()

from netforce.model import Model, fields, get_model
from netforce import access
from netforce import database
from netforce import config
from netforce import tasks
import requests
import hashlib
import hmac
from datetime import *
import time
import json

class ShopeeOrder(Model):
    _name = "shopee.order"
    _string = "Shopee Order"
    _fields = {
        "sync_records": fields.One2Many("sync.record","related_id","Sync Records"),
        "sync_id": fields.Char("Sync ID",function="get_sync_id",function_search="search_sync_id"),
        "account_id": fields.Many2One("shopee.account","Shopee Account",search=True),
        "order_sn": fields.Char("Order ID",required=True,search=True),
        "order_status": fields.Char("Order Status",required=True, search=True),
        "order_create_time": fields.DateTime("Order Create Time",required=True, search=True),
        "region": fields.Char("Region"),
        "currency": fields.Char("Currency"),
        "cod": fields.Boolean("cod"),
        "total_amount": fields.Decimal("Total Amount"),
        "shipping_carrier": fields.Char("Shipping Carrier",search=True),
        "payment_method": fields.Char("Payment Method"),
        "estimated_shipping_fee": fields.Char("Estimated Shipping Fee"),
        "message_to_seller": fields.Text("Message to Seller"),
        "days_to_ship": fields.Integer("Days to Ship"),
        "ship_by_date": fields.DateTime("Ship By Date"),
        "buyer_user_id": fields.Char("Buyer User ID"),
        "buyer_username": fields.Char("Buyer User Name"),
        "recipient_address_name": fields.Char("Recipient Address Name",search=True),
        "recipient_address_phone": fields.Char("Recipient Address Phone"),
        "recipient_address_town": fields.Char("Recipient Address Town"),
        "recipient_address_district": fields.Char("Recipient Address District"),
        "recipient_address_city": fields.Char("Recipient Address City"),
        "recipient_address_state": fields.Char("Recipient Address State"),
        "recipient_address_region": fields.Char("Recipient Address Region"),
        "recipient_address_zipcode": fields.Char("Recipient Address Zipcode"),
        "recipient_address_full_address": fields.Char("Recipient Address Full Address",search=True),
        "invoice_data_number": fields.Char("Invoice Data Number"),
        "invoice_data_series_number": fields.Char("Invoice Data Series Number"),
        "invoice_data_access_key":  fields.Text("Invoice Data Access Key"),
        "invoice_data_issue_date": fields.DateTime("Invoice Data Issue Date"),
        "invoice_data_total_value": fields.Decimal("Invoice Data Total Value"),
        "invoice_data_products_total_value": fields.Decimal("Invoice Data Products Total Value"),
        "invoice_data_tax_code": fields.Char("Invoice Data Tax Code"),
        "actual_shipping_fee": fields.Decimal("Actual Shipping Fee"),
        "goods_to_declare": fields.Boolean("Goods to Declare"),
        "note": fields.Text("Notes"),
        "note_update_time": fields.DateTime("Note Update Time"),
        "pay_time": fields.DateTime("Pay Time"),
        "dropshipper": fields.Char("Dropshipper"),
        "credit_card_number": fields.Char("Credit Card Number"),
        "dropshipper_phone": fields.Char("Dropshipper Phone"),
        "split_up": fields.Boolean("Split Up"),
        "buyer_cancel_reason": fields.Text("Buyer Cancel Reason"),
        "cancel_by": fields.Char("Cancel By"),
        "cancel_reason": fields.Text("Cancel Reason"),
        "actual_shipping_fee_confirmed": fields.Boolean("Actual Shippingg Fee Confirmed"),
        "buyer_cpf_id": fields.Char("Buyer CPF ID"),
        "fulfillment_flag": fields.Char("Fulfillment Flag"),
        "pickup_done_time": fields.Char("Pickup Done Time"),
        "items": fields.One2Many("shopee.order.item","order_id","Items"),
        "dropoff": fields.Boolean("DropOff",search=True),
        "dropoff_info_needed": fields.Text("DropOff Info Needed"),
        "dropoff_info": fields.Text("DropOff Info"),
        "pickup": fields.Boolean("PickUp",search=True),
        "pickup_info_needed": fields.Text("PickUp Info Needed"),
        "pickup_info": fields.Text("PickUp Info"),
        "non_integrated": fields.Boolean("Non Integrated",search=True),
        "non_integrated_info_needed": fields.Text("Non Integrated Info Needed"),
        "non_integrated_info": fields.Text("Non Integrated Info"),
        "tracking_number": fields.Char("Tracking Number",search=True),
        "package_number": fields.Char("Package Number",search=True),

        # For Shipping Document Info
        "logistics_channel_id": fields.Integer("Logistic Channel ID"),
        "service_code": fields.Char("Service Code"),
        "first_mile_name": fields.Char("First Mile Name"),
        "last_mile_name": fields.Char("Last Mile Name"),
        "zone": fields.Char("Zone"),
        "lane_code": fields.Char("Lane Code"),
        "warehouse_address": fields.Text("Warehouse Address"),
        "warehouse_id": fields.Char("Warehouse ID"),
        "first_recipient_sort_code": fields.Char("First Recipient Sort Code"),
        "second_recipient_sort_code": fields.Char("Second Recipient Sort Code"),
        "third_recipient_sort_code": fields.Char("Third Recipient Sort Code"),
        "first_sender_sort_code": fields.Char("First Sender Sort Code"),
        "second_sender_sort_code": fields.Char("Second Sender Sort Code"),
        "third_sender_sort_code": fields.Char("Third Sender Sort Code"),
        "return_first_sort_code": fields.Char("Return First Sort Code"),

        # For Escrow
        "escrow_release_time": fields.DateTime("Escrow Release Time"),
        "escrow_amount": fields.Decimal("Escrow Amount"),
        "buyer_total_amount": fields.Decimal("Buyer Total Amount"),
        "original_price": fields.Decimal("Original Price"),
        "seller_discount": fields.Decimal("Seller Discount"),
        "shopee_discount": fields.Decimal("Shopee Discount"),
        "voucher_from_seller": fields.Decimal("Voucher From Seller"),
        "voucher_from_shopee": fields.Decimal("Voucher From Shopee"),
        "coins": fields.Decimal("Coins"),
        "buyer_paid_shipping_fee": fields.Decimal("Buyer Paid Shipping Fee"),
        "buyer_transaction_fee": fields.Decimal("Buyer Transaction Fee"),
        "cross_border_tax": fields.Decimal("Cross Border Tax"),
        "payment_promotion": fields.Decimal("Payment Promotion"),
        "commission_fee": fields.Decimal("Commission Fee"),
        "service_fee": fields.Decimal("Decimal Fee"),
        "seller_transaction_fee": fields.Decimal("Seller Transaction Fee"),
        "seller_lost_compensation": fields.Decimal("Seller Lost Compensation"),
        "seller_coin_cash_back": fields.Decimal("Seller Coin Cash Back"),
        "escrow_tax": fields.Decimal("Escrow Tax"),
        "final_shipping_fee": fields.Decimal("Final Shipping Fee"),
        "actual_shipping_fee": fields.Decimal("Actual Shipping Fee"),
        "order_chargeable_weight": fields.Integer("Order Chargeable Weight"),
        "shopee_shipping_rebate": fields.Decimal("Shopee Shipping Rebate"),
        "shopee_fee_discount_from_3pl": fields.Decimal("Shopee Fee Discount From 3PL"),
        "seller_shipping_discount": fields.Decimal("Seller Shipping Discount"),
        #"estimated_shipping_fee": fields.Decimal("Estimated Shipping Fee"),
        "seller_voucher_code": fields.Char("Seller Voucher Code"),
        "drc_adjustable_refund": fields.Decimal("Dispute Resolution Center Adjustable Refund"),
        "cost_of_goods_sold": fields.Decimal("Cost of Goods Sold"),
        "original_cost_of_goods_sold": fields.Decimal("Original Cost of Goods Sold"),
        "original_shopee_discount": fields.Decimal("Original Shopee Discount"),
        "seller_return_refund": fields.Decimal("Seller Return Refund"),
        "escrow_amount_pri": fields.Decimal("Escrow Amount Pri"),
        "buyer_total_amount_pri": fields.Decimal("Buyer Total Amount Pri"),
        "original_price_pri": fields.Decimal("Original Price Pri"),
        "seller_return_refund_pri":fields.Decimal("Seller Return Refund Pri"),
        "commission_fee_pri": fields.Decimal("Commision Fee Pri"),
        "drc_adjustable_refund_pri": fields.Decimal("Dispute Resolution Center Adjustable Refund Pri"),
        "pri_currency": fields.Char("Primary Currency"),
        "aff_currency": fields.Char("Affliate Currency"),
        "exchange_rate": fields.Decimal("Exchange Rate"),
        "reverse_shipping_fee": fields.Decimal("Reverse Shipping Fee"),
        "final_product_protection": fields.Decimal("Final Product Protection"),
        "credit_card_promotion": fields.Decimal("Credit Card Promotion"),
        "credit_card_transaction_fee": fields.Decimal("Credit Card Transaction Fee"),
        "final_product_vat_tax": fields.Decimal("Final Product Value Added Tax"),

        "sale_orders": fields.One2Many("sale.order","related_id","Sale Orders"),
        "pickings": fields.One2Many("stock.picking","related_id","Stock Pickings"),
        "invoices": fields.One2Many("account.invoice","related_id","Invoices"),
        "payments": fields.One2Many("account.payment","related_id","Payments"),
        "weight": fields.Decimal("weight",function="get_weight"),
        "show_warning": fields.Boolean("Show Warning",function="get_show_warning",store=True, search=True),
        "ignore_warning": fields.Boolean("Ignore Warning"),
        "logs": fields.Text("Logs"),
    }
    _order = "order_create_time desc"
    _keys = "account_id, order_sn"
    
     
    def get_sync_id(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            sync_id=None
            for sync in obj.sync_records:
                sync_id=sync.sync_id
                break
            vals[obj.id]=sync_id
            return vals

    def search_sync_id(self, clause, context={}):
        sync_id = clause[2] 
        records = get_model("sync.record").search_browse([["related_id","like",self._name],["sync_id","=",sync_id]])
        ids = [r.related_id.id  for r in records if r.related_id]
        cond = [["id","in",ids]]
        return cond

    def name_get(self, ids, context={}):
        vals = []
        for obj in self.browse(ids):
            vals.append((obj.id,obj.order_sn))
        return vals

    def refresh_order(self, ids, context={}):
        # print("shopee.order.refresh_order",ids)
        db = database.get_connection()
        job_id = context.get("job_id")
        i = 0
        for obj in self.browse(ids):
            if job_id:
                if tasks.is_aborted(job_id):
                    return
                tasks.set_progress(job_id,i/len(ids)*100,"Updating Orders: %s of %s."%(i,len(ids)))
            if not obj.account_id:
                continue
            obj.account_id.get_order(obj.order_sn, context=context) 
            db.commit()
            i += 1
    
    def create_order(self, acc_id, vals, context={}):
        # print("create_order",acc_id,vals)
        settings = get_model("shopee.settings").browse(1)
        create_vals = { key:value for (key,value) in vals.items() if type(value) not in (dict,list) and key in self._fields }
        create_vals["order_create_time"] = create_vals["create_time"]
        create_vals["account_id"] = acc_id
        del create_vals["create_time"] #XXX
        for (k,v) in create_vals.items():
            if isinstance(self._fields[k],fields.DateTime):
                create_vals[k] = datetime.fromtimestamp(v).strftime("%Y-%m-%d %H:%M:%S") if v else None 
        if vals["recipient_address"]:
            create_vals.update({"recipient_address_%s" % key1:value1 for (key1,value1) in vals["recipient_address"].items()})
        if vals["item_list"]:
            create_vals["items"] = [["create",{key2:value2 for (key2,value2) in item.items() if type(value2) not in (dict,list)}] for item in vals["item_list"]] 
        if vals["invoice_data"]:
            create_vals.update({"invoice_data_%s" & key2:value2 for (key2,value2) in vals["invoice_data"].items()})
        create_vals["sync_records"]= [("create",{
            "sync_id": vals["order_sn"],
            "account_id": "shopee.account,%s"%acc_id,
            })]
        order_id = self.create(create_vals)
        self.get_tracking_number([order_id],context=context)
        self.get_shipping_document_info([order_id],context=context)
        self.get_escrow_detail([order_id],context=context)
        if settings.order_auto_copy_to_sale:
            self.copy_to_sale([order_id],context={"skip_error":True})
        if settings.order_auto_copy_to_picking:
            self.copy_to_picking([order_id],context={"skip_error":True})
        if settings.order_auto_copy_to_invoice:
            self.copy_to_invoice([order_id],context={"skip_error":True})
        self.function_store([order_id])
        return order_id

    def update_order(self, ids, acc_id, vals, context={}):
        # print("Update Order: ids:%s, vals:%s"%(ids, vals))
        order = self.browse(ids[0])
        company_id = access.get_active_company()
        if not company_id:
            access.set_active_company(order.account_id.company_id.id)
        update_vals = {key:value for (key, value) in vals.items() if type(value) not in (dict, list) and key in self._fields}
        update_vals["account_id"] = acc_id
        if update_vals["create_time"]:
            update_vals["order_create_time"] = update_vals["create_time"]
            del update_vals["create_time"] #XXX
        for (k,v) in update_vals.items():
            if isinstance(self._fields[k],fields.DateTime):
                update_vals[k] = datetime.fromtimestamp(v).strftime("%Y-%m-%d %H:%M:%S") if v else None
        if vals["recipient_address"]:
            update_vals.update({"recipient_address_%s" % key1:value1 for (key1,value1) in vals["recipient_address"].items() if not ("*" in value1)})
        write_vals = {key2:value2 for (key2, value2) in update_vals.items() if (key2 in self._fields and value2 != getattr(order,key2))}
        if vals["item_list"]:
            if order.items:
                for item in order.items:
                    item.delete()
            write_vals["items"] = [["create",{key2:value2 for (key2,value2) in item.items() if type(value2) not in (dict,list)}] for item in vals["item_list"]] 
        write_vals["sync_records"]= [("create",{
            "sync_id": vals["order_sn"],
            "account_id": "shopee.account,%s"%acc_id,
            })]
        order.write(write_vals)
        settings = get_model("shopee.settings").browse(1)
        if settings.order_auto_copy_to_picking and not order.pickings:
            new_context = context.copy()
            new_context["skip_error"] = True
            order.copy_to_picking(context=new_context)
        self.get_tracking_number([order.id],context=context)
        self.get_shipping_document_info([order.id],context=context)
        self.get_escrow_detail([order.id],context=context)
        if settings.order_auto_copy_to_invoice and not order.invoices:
            new_context = context.copy()
            new_context["skip_error"] = True
            order.copy_to_invoice(context=new_context)
        self.function_store([order.id])


    def get_shipping_parameter(self,ids,context={}):
        for obj in self.browse(ids):
            acc = obj.account_id
            if not acc:
                raise Exception("Missing Shopee Account in Shopee Order: %s" % obj.order_sn)
            if not acc.shop_idno:
                raise Exception("Missing shop ID")
            if not acc.token:
                raise Exception("Missing token")
            path="/api/v2/logistics/get_shipping_parameter"
            url = get_model("shopee.account").generate_url(account_id=acc.id,path=path)
            url += "&order_sn=%s" % obj.order_sn
            # print("url",url)
            req=requests.get(url)
            res=req.json()
            if res.get("error"):
                raise Exception("Sync error: %s"%res)
            # print("res",res)
            resp=res["response"]
            write_vals= {}
            if "dropoff" in resp["info_needed"]:
                write_vals["dropoff"] = True
                write_vals["dropoff_info_needed"] = json.dumps(resp["info_needed"]["dropoff"])
            if "pickup" in resp["info_needed"]:
                write_vals["pickup"] = True
                write_vals["pickup_info_needed"] = json.dumps(resp["info_needed"]["pickup"])
            if "non_integrated" in resp["info_needed"]:
                write_vals["non_integrated"] = True
                write_vals["non_integrated_info_needed"] = json.dumps(resp["info_needed"]["non_integrated"])
            if "dropoff" in resp:
                write_vals["dropoff_info"] = json.dumps(resp["dropoff"])
            if "pickup" in resp:
                write_vals["pickup_info"] = json.dumps(resp["pickup"])
            obj.write(write_vals)

    def ship_order(self,ids,context={}):
        # print("shopee.order.ship_order",ids)
        job_id = context.get("job_id")
        if job_id:
            if tasks.is_aborted(job_id):
                return
            tasks.set_progress(job_id,100,"Step 1/3: Getting Shipping Parameters")
        try:
            self.get_shipping_parameter(ids, context=context)
        except:
            pass
        acc_ids = set()
        i = 0
        for obj in self.browse(ids):
            if job_id:
                if tasks.is_aborted(job_id):
                    return
                tasks.set_progress(job_id,i/len(ids)*100,"Step 2/3: Shipping %s of %s Orders"%(i,len(ids)))
            acc = obj.account_id
            if not acc:
                raise Exception("Missing Shopee Account in Shopee Order: %s" % obj.order_sn)
            path = "/api/v2/logistics/ship_order"
            url = get_model("shopee.account").generate_url(account_id=acc.id,path=path)
            body={"order_sn":obj["order_sn"]}
            if obj.pickup:
                if not obj.pickup_info:
                    raise Exception("No Pickup Info")
                pickup_info = json.loads(obj.pickup_info)
                if not pickup_info["address_list"]:
                    raise Exception("Missing Adress List in Pickup Info")
                address = pickup_info["address_list"][0]
                # print("address: ",address)
                if not address["time_slot_list"]:
                    raise Exception("Order: %s\nMissing Time Slot List in Address"%obj.order_sn)
                body["pickup"] = {
                    "address_id": address["address_id"],
                    "pickup_time_id": address["time_slot_list"][0]["pickup_time_id"]
                }
            elif obj.dropoff:
                body["dropoff"] = {}
            elif obj.non_integrated:
                continue
               # body["non_integrated"] = {}
            headers={"Content-Type":"application/json"}

            # post request and process
            req=requests.post(url,json=body,headers=headers)
            res=req.json()
            # print("res",res)
            if res.get("error"):
                raise Exception(res["message"])
            acc_ids.add(acc.id)
            i += 1
        if job_id:
            if tasks.is_aborted(job_id):
                return
            tasks.set_progress(job_id,100,"Step 3/3: Waiting 20s for Shopee to Update Orders")
        time.sleep(20)
        get_model("shopee.account").get_orders(acc_ids)
        return {
            "alert": "Orders Shipped Successfully"
        }


    def get_tracking_number(self,ids,context={}):
        for obj in self.browse(ids):
            write_vals = {}
            try:
                acc = obj.account_id
                if not acc:
                    raise Exception("Missing Shopee Account in Shopee Order: %s" % obj.order_sn)
                path="/api/v2/logistics/get_tracking_number"
                url = get_model("shopee.account").generate_url(account_id=acc.id,path=path)
                url += "&order_sn=%s" % obj.order_sn
                # print("url",url)
                req=requests.get(url)
                res=req.json()
                if res.get("error"):
                    raise Exception("Sync error: %s"%res)
                # print("res",res)
                resp=res["response"]
                write_vals["tracking_number"]=resp["tracking_number"]
                if obj.pickings:
                    for pick in obj.pickings:
                        pick.write({"ship_tracking":obj.tracking_number})
                else:
                    raise Exception("Stock Picking Not Found")
            except Exception as e:
                if context.get("skip_error"):
                    logs = obj.logs or ""
                    log = "%s : get_tracking_number\n" % datetime.now().strftime("%Y-%m-%d %H-%M-%S")
                    log += str(e) + "\n"
                    log += "-" * 10
                    log += "\n\n"
                    logs = log + logs
                    write_vals["logs"] = logs
            obj.write(write_vals)

    def get_shipping_document_info(self,ids,context={}):
        # print("shopee.order.get_shipping_document_info",ids)
        for obj in self.browse(ids):
            write_vals = {}
            try:
                acc = obj.account_id
                if not acc:
                    raise Exception("Missing Shopee Account in Shopee Order: %s" % obj.order_sn)
                path="/api/v2/logistics/get_shipping_document_info"
                url = get_model("shopee.account").generate_url(account_id=acc.id,path=path)
                url += "&order_sn=%s" % obj.order_sn
                if obj.package_number:
                    url += "&package_number=%s" % obj.package_number
                # print("url",url)
                req=requests.get(url)
                # print("req",req)
                res=req.json()
                if res.get("error"):
                    raise Exception("Sync error: %s"%res)
                # print("res",res)
                resp=res["response"]
                if not resp.get("shipping_document_info"):
                    raise("Missing shipping_document_info in response")
                doc = resp["shipping_document_info"]
                doc_fields = ["logistics_channel_id","service_code","first_mile_name","last_mile_name","zone","lane_code","warehouse_address","warehouse_id"]
                recipient_sort_code_fields = ["first_recipient_sort_code","second_recipient_sort_code","third_recipient_sort_code"]
                sender_sort_code_fields = ["first_sender_sort_code","second_sender_sort_code","third_sender_sort_code"]
                return_sort_code_fields = ["return_first_sort_code"]
                for f in doc_fields:
                    write_vals[f] = doc.get(f)
                if doc.get("recipient_sort_code"):
                    for f in recipient_sort_code_fields:
                        write_vals[f] = doc["recipient_sort_code"].get(f)
                if doc.get("sender_sort_code"):
                    for f in sender_sort_code_fields:
                        write_vals[f] = doc["sender_sort_code"].get(f)
                if doc.get("return_sort_code"):
                    for f in return_sort_code_fields:
                        write_vals[f] = doc["return_sort_code"].get(f)
                # print("write_vals",write_vals)
                if obj.pickings:
                    for pick in obj.pickings:
                        pick.write({"shopee_"+k:v for (k,v) in write_vals.items()})
                else:
                    raise Exception("Stock Picking Not Found")
            except Exception as e:
                # print("Error",e)
                logs = obj.logs or ""
                log = "%s : get_shipping_document_info\n" % datetime.now().strftime("%Y-%m-%d %H-%M-%S")
                log += str(e) + "\n"
                log += "-" * 10
                log += "\n\n"
                logs = log + logs
                write_vals["logs"] = logs
            obj.write(write_vals)

    
    def get_escrow_detail(self,ids,context={}):
        # print("shopee.order.get_escrow_detail",ids)
        for obj in self.browse(ids):
            write_vals = {}
            try:
                acc = obj.account_id
                if not acc:
                    raise Exception("Missing Shopee Account in Shopee Order: %s" % obj.order_sn)
                if not acc.shop_idno:
                    raise Exception("Missing shop ID")
                if not acc.token:
                    raise Exception("Missing token")
                company_id = access.get_active_company()
                if not company_id:
                    access.set_active_company(acc.company_id.id)
                shop_id=int(acc.shop_idno)
                partner_id=int(config.get("shopee_partner_id"))
                partner_key=config.get("shopee_partner_key")
                timest=int(time.time())
                path="/api/v2/payment/get_escrow_detail"
                base_string="%s%s%s%s%s"%(partner_id,path,timest,acc.token,shop_id)
                sign=hmac.new(partner_key.encode(),base_string.encode(),hashlib.sha256).hexdigest()
                #base_url="https://partner.test-stable.shopeemobile.com"
                base_url="https://partner.shopeemobile.com"
                url=base_url+path+"?partner_id=%s&timestamp=%s&sign=%s&shop_id=%s&access_token=%s"%(partner_id,timest,sign,shop_id,acc.token)
                url += "&order_sn=%s" % obj.order_sn
                # print("url",url)
                req=requests.get(url)
                res=req.json()
                if res.get("error"):
                    raise Exception("Sync error: %s"%res)
                resp=res["response"]
                if not resp["order_income"]:
                    raise Exception("No Order Income in Response")
                for k,v in resp["order_income"].items():
                    if type(v) in [list,dict]:
                        continue
                    if k not in self._fields:
                        continue
                    write_vals[k] = v
                # print("write_vals",write_vals)
            except Exception as e:
                logs = obj.logs or ""
                log = "%s : get_escrow_detail\n" % datetime.now().strftime("%Y-%m-%d %H-%M-%S")
                log += str(e) + "\n"
                log += "-" * 10
                log += "\n\n"
                logs = log + logs
                write_vals["logs"] = logs
            obj.write(write_vals)

    def copy_to_sale(self,ids,context={}):
        for obj in self.browse(ids):
            try:
                acc = obj.account_id
                if not acc:
                    raise Exception("No Shopee Account Assigned to Order: %s" % obj.order_sn)
                contact = acc.contact_id
                if not contact:
                    raise Exception("Unable to Create Sales Order without Contact. Please enable contact module in Shopee Settings")
                sale_vals={
                    "contact_id": contact.id,
                    "date": obj.order_create_time,
                    "due_date": obj.ship_by_date,
                    "other_info": obj.note,
                    "lines": [],
                    "related_id": "shopee.order,%s"%obj.id
                }
                for it in obj.items:
                    #res=get_model("product").search([["sync_records.shopee_id","=",it["item_id"]]])
                    res=get_model("sync.record").search([["sync_id","=",str(it.item_id)],["related_id","like","product"],["account_id","=","shopee.account,%s"%acc.id]]) # XXX
                    if not res:
                        raise Exception("Product not found: %s"%it.item_id)
                    sync_id=res[0]
                    sync=get_model("sync.record").browse(sync_id)
                    prod_id=sync.related_id.id
                    line_vals={
                        "product_id": prod_id,
                        "description": it.item_name,
                        "qty": it.model_quantity_purchased,
                        "unit_price": it.model_discounted_price,
                    }
                    sale_vals["lines"].append(("create",line_vals))
                sale_id = get_model("sale.order").create(sale_vals)
            except Exception as e:
                if context.get("skip_error"):
                    continue
                else:
                    raise Exception(e)
        if len(ids) == 1:
            return {
                "next":{
                    "name": "sale",
                    "mode": "form",
                    "active_id": str(sale_id),
                    "target": "new_window",
                }
            }
        else: 
            return {
                "alert": "%s Orders Copied Successfully" % len(ids)
            }

    def match_picking(self,ids,context={}):
        # print("shopee.order.match_picking")
        for obj in self.browse(ids):
            if obj.pickings:
                continue
            pickings = get_model("stock.picking").search_browse([["number","ilike",obj.order_sn],["type","=","out"]])
            if not pickings:
                continue
            elif len(pickings) > 1:
                raise Exception("More than 1 Goods Issue found for Order: %s" % obj.order_sn)
            pickings[0].write({"related_id":"shopee.order,%s"%obj.id})

    
    def copy_to_picking(self,ids,context={}):
        user_id = access.get_active_user()
        if not user_id:
            access.set_active_user(1)
        settings = get_model("shopee.settings").browse(1)
        pick_ids = []
        for obj in self.browse(ids):
            try:
                if obj.pickings:
                    raise Exception("Order already Have picking: %s" % obj.order_sn)
                acc = obj.account_id
                if acc.company_id:
                    access.set_active_company(acc.company_id.id)
                if not acc.stock_journal_id:
                    raise Exception("Missing Stock Journal for Shopee Account: %s" % acc.name)
                if not acc.stock_journal_id.location_from_id:
                    raise Exception("Missing From Location in Stock Journal: %s" % acc.stock_journal_id.name)
                if not acc.stock_journal_id.location_to_id:
                    raise Exception("Missing To Location in Stock Journal: %s" % acc.stock_journal_id.name)
                if obj.invoices:
                    inv_id = obj.invoices[0].id
                else:
                    inv_id = None
                pick_vals={
                    "number": (acc.pick_out_prefix or "") + obj.order_sn,
                    "type": "out",
                    "contact_id": acc.contact_id.id if acc.contact_id else None,
                    "related_id": "shopee.order,%s"%obj.id,
                    "journal_id": acc.stock_journal_id.id,
                    "date": obj.order_create_time,
                    "recipient_first_name": obj.recipient_address_name,
                    "recipient_address": obj.recipient_address_full_address,
                    "recipient_phone": obj.recipient_address_phone,
                    "recipient_postcode": obj.recipient_address_zipcode,
                    "recipient_city": obj.recipient_address_city,
                    "recipient_province": obj.recipient_address_state,
                    "recipient_country": obj.recipient_address_region,
                    "ship_tracking": obj.tracking_number,
                    "invoice_id": inv_id,
                    "lines": [],
                }
                if not obj.shipping_carrier:
                    raise Exception("No Shipping Carrier assigned for order: %s" % obj.order_sn)
                ship_method_res = get_model("ship.method").search([["name","=",obj.shipping_carrier]])
                if not ship_method_res:
                    raise Exception("Shipping Method not found for %s" % obj.shipping_carrier)
                else:
                    ship_method_id = ship_method_res[0]
                pick_vals["ship_method_id"] = ship_method_id
                exp_ship_date = datetime.strftime(datetime.strptime(obj.order_create_time,"%Y-%m-%d %H:%M:%S") + timedelta(days=obj.days_to_ship),"%Y-%m-%d")
                pick_vals["exp_ship_date"] = exp_ship_date
                for it in obj.items:
                    if not it.item_id:
                        raise Exception("Order: %s - Missing Item ID" % obj.order_sn)
                    shopee_prods = get_model("shopee.product").search_browse([["account_id","=",acc.id],["sync_id","=",str(it.item_id)]])
                    if not shopee_prods:
                        get_model("shopee.account").get_products_info(acc.id,[it.item_id])
                        shopee_prods = get_model("shopee.product").search_browse([["account_id","=",acc.id],["sync_id","=",str(it.item_id)]])
                        if not shopee_prods:
                            raise Exception("Order: %s - Shopee Product not found: %s (Sync ID: %s)" % (obj.order_sn, it.item_sku, it.item_id))
                    shopee_prod = shopee_prods[0]
                    if not it.model_id or it.model_id == "0":
                        prod = shopee_prod.product_id
                        if not prod:
                            shopee_prod.map_product()
                            shopee_prod = get_model("shopee.product").browse(shopee_prod.id)
                            prod = shopee_prod.product_id
                            if not prod:
                                raise Exception("Order:  %s - System Product not found for item: %s (Sync ID: %s)" % (obj.order_sn, shopee_prod.item_sku, it.item_id))
                    else:
                        models = get_model("shopee.product.model").search_browse([["shopee_product_id.sync_id","=",str(it.item_id)],["sync_id","=",str(it.model_id)]])
                        if not models:
                            get_model("shopee.account").get_products_info(acc.id,[it.item_id])
                            models = get_model("shopee.product.model").search_browse([["shopee_product_id.sync_id","=",str(it.item_id)],["sync_id","=",str(it.model_id)]])
                            if not models:
                                raise Exception("Order: %s - Shopee Product Model Not Found: (item: %s (Sync ID: %s), model: %s (Sync ID: %s))" % (obj.order_sn, it.item_sku, it.item_id, it.model_name, it.model_id))
                        model = models[0]
                        prod = model.product_id
                        if not prod:
                            shopee_prod.map_product()
                            model = get_model("shopee.product.model").browse(model.id)
                            prod = model.product_id
                            if not prod:
                                raise Exception("Order: %s - System Product not found for: (item: %s (Sync ID: %s), model: %s (Sync ID: %s))" % (obj.order_sn, it.item_sku, it.item_id, it.model_name, it.model_id))
                    line_vals={
                        "product_id": prod.id,
                        "description": it.item_name,
                        "qty": it.model_quantity_purchased,
                        "uom_id": prod.uom_id.id,
                        "location_from_id": acc.stock_journal_id.location_from_id.id,
                        "location_to_id": acc.stock_journal_id.location_to_id.id,
                        "invoice_id": inv_id,
                    }
                    pick_vals["lines"].append(("create",line_vals))
                pick_id = get_model("stock.picking").create(pick_vals,context={"journal_id":acc.stock_journal_id.id})
                pick_ids.append(pick_id)
            except Exception as e:
                if context.get("skip_error"):
                    logs = obj.logs or ""
                    log = "%s : shopee.order.copy_to_picking\n%s\n" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),str(e))
                    log += "(user_id %s, company_id %s)\n" % (access.get_active_user() ,access.get_active_company())
                    log += "-" * 10
                    log += "\n\n"
                    logs = log + logs
                    obj.write({"logs":logs})
                    continue
                else:
                    raise Exception(e)
        if settings.order_auto_complete_picking:
            try:
                get_model("stock.picking").set_done_fast(pick_ids)
            except Exception as e:
                if context.get("skip_error"):
                    pass
                else:
                    raise Exception(e)
        self.get_tracking_number(ids, context=context)
        self.function_store(ids)
        if len(pick_ids) == 1:
            return {
                "next": {
                    "name":"pick_out",
                    "mode":"form",
                    "active_id":pick_id,
                    "target":"new_window",
                }
            }
        else:
            return {
                "alert": "%s orders copied successfully." %len(ids)
            }

    def copy_to_picking_skip_error(self, ids, context={}):
        # context["skip_error"] = True
        # print("print 11111111111")
        self.copy_to_picking(ids, context=context)

    def match_invoice(self,ids,context={}):
        # print("shopee.order.match_invoice")
        for obj in self.browse(ids):
            if obj.invoices:
                continue
            invoices = get_model("account.invoice").search_browse([["number","ilike",obj.order_sn]])
            if not invoices:
                continue
            elif len(invoices) > 1:
                raise Exception("More than 1 Invoice found for Order: %s" % obj.order_sn)
            invoices[0].write({"related_id":"shopee.order,%s"%obj.id})

    def copy_to_invoice(self,ids,context={}):
        settings = get_model("shopee.settings").browse(1)
        inv_ids = []
        for obj in self.browse(ids):
            try:
                if obj.invoices:
                    continue
                acc = obj.account_id
                if not acc:
                    raise Exception("No Shopee Account Assigned to Order: %s" % obj.order_sn)
                contact = acc.contact_id
                if not contact:
                    raise Exception("Unable to Create Invoice without Contact. Please choose default contact in Shopee account")
                vals={
                    "number": (acc.invoice_prefix or "")+obj.order_sn,
                    "type": "out",
                    "inv_type": "invoice",
                    "contact_id": contact.id,
                    "date": obj.order_create_time,
                    "due_date": obj.ship_by_date,
                    "account_id": acc.debtor_account_id.id,
                    "other_info": obj.note,
                    "memo": obj.order_sn,
                    "lines": [],
                    "related_id": "shopee.order,%s"%obj.id,
                }
                for it in obj.items:
                    if not it.item_id:
                        raise Exception("Order: %s - Missing Item ID" % obj.order_sn)
                    shopee_prods = get_model("shopee.product").search_browse([["account_id","=",acc.id],["sync_id","=",str(it.item_id)]])
                    if not shopee_prods:
                        get_model("shopee.account").get_products_info(acc.id,[it.item_id])
                        shopee_prods = get_model("shopee.product").search_browse([["account_id","=",acc.id],["sync_id","=",str(it.item_id)]])
                        if not shopee_prods:
                            raise Exception("Order: %s - Shopee Product not found: %s (Sync ID: %s)" % (obj.order_sn, it.item_sku, it.item_id))
                    shopee_prod = shopee_prods[0]
                    if not it.model_id or it.model_id == "0":
                        prod = shopee_prod.product_id
                        if not prod:
                            shopee_prod.map_product()
                            shopee_prod = get_model("shopee.product").browse(shopee_prod.id)
                            prod = shopee_prod.product_id
                            if not prod:
                                raise Exception("Order:  %s - System Product not found for item: %s (Sync ID: %s)" % (obj.order_sn, shopee_prod.item_sku, it.item_id))
                    else:
                        models = get_model("shopee.product.model").search_browse([["shopee_product_id.sync_id","=",str(it.item_id)],["sync_id","=",str(it.model_id)]])
                        if not models:
                            get_model("shopee.account").get_products_info(acc.id,[it.item_id])
                            models = get_model("shopee.product.model").search_browse([["shopee_product_id.sync_id","=",str(it.item_id)],["sync_id","=",str(it.model_id)]])
                            if not models:
                                raise Exception("Order: %s - Shopee Product Model Not Found: (item: %s (Sync ID: %s), model: %s (Sync ID: %s))" % (obj.order_sn, it.item_sku, it.item_id, it.model_name, it.model_id))
                        model = models[0]
                        prod = model.product_id
                        if not prod:
                            shopee_prod.map_product()
                            model = get_model("shopee.product.model").browse(model.id)
                            prod = model.product_id
                            if not prod:
                                raise Exception("Order: %s - System Product not found for: (item: %s (Sync ID: %s), model: %s (Sync ID: %s))" % (obj.order_sn, it.item_sku, it.item_id, it.model_name, it.model_id))
                    line_vals={
                        "product_id": prod.id,
                        "description": it.item_name,
                        "qty": it.model_quantity_purchased,
                        "unit_price": it.model_discounted_price,
                        "account_id": acc.sale_account_id.id,
                        "track_id": acc.track_id.id,
                        "amount": (it.model_quantity_purchased or 0) * (it.model_discounted_price or 0),
                    }
                    vals["lines"].append(("create",line_vals))
                if obj.buyer_paid_shipping_fee:
                    line_vals={
                        "description": "Shopee Shipping Fee",
                        "account_id": acc.buyer_paid_shipping_fee_account_id.id,
                        "amount": obj.buyer_paid_shipping_fee,
                        "track_id": acc.track_id.id,
                    }
                    vals["lines"].append(("create",line_vals))
                inv_id = get_model("account.invoice").create(vals)
                if obj.pickings:
                    for pick in obj.pickings:
                        pick_vals = {"invoice_id":inv_id,"lines":[]}
                        for l in pick.lines:
                            pick_vals["lines"].append(["write",[l.id],{"invoice_id":inv_id}])
                        pick.write(pick_vals)
                inv_ids.append(inv_id)
            except Exception as e:
                if context.get("skip_error"):
                    logs = obj.logs or ""
                    log = "%s : shopee.order.copy_to_invoice\n%s\n" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),str(e))
                    log += "(user_id %s, company_id %s)\n" % (access.get_active_user() ,access.get_active_company())
                    log += "-" * 10
                    log += "\n\n"
                    logs = log + logs
                    obj.write({"logs":logs})
                    continue
                else:
                    raise Exception(e)
        if settings.order_auto_post_invoice:
            try:
                get_model("account.invoice").post(inv_ids)
            except Exception as e:
                if context.get("skip_error"):
                    pass
                else:
                    raise Exception(e)
        self.function_store(ids)
        if len(ids) == 1 and inv_ids:
            return {
                "next":{
                    "name": "cust_invoice",
                    "mode": "form",
                    "active_id": str(inv_ids[0]),
                    "target": "new_window",
                }
            }
        else: 
            return {
                "alert": "%s Orders Copied Successfully" % len(ids)
            }

    def pay_invoice(self, ids, context={}):
        settings = get_model("shopee.settings").browse(1)
        for obj in self.browse(ids):
            try:
                if not obj.invoices:
                    raise Exception("No Invoice Found for Order")
                inv = obj.invoices[0]
                acc = obj.account_id
                if not acc:
                    raise Exception("No Shopee Account Assigned to Order: %s" % obj.order_sn)
                contact = acc.contact_id
                if not contact:
                    raise Exception("Unable to Create Payment without Contact. Please choose default contact in Shopee account")
                vals={
                    "number": (acc.payment_prefix or "")+obj.order_sn,
                    "invoice_id": inv.id,
                    "type": "in",
                    "pay_type": "invoice",
                    "tax_type": "tax_ex",
                    "contact_id": contact.id,
                    "account_id": acc.ewallet_account_id.id,
                    "date": obj.escrow_release_time,
                    "memo": obj.order_sn,
                    "related_id": "shopee.order,%s"%obj.id,
                    "invoice_lines": [],
                    "adjust_lines": [],
                }
                amount = inv.amount_total
                vals["invoice_lines"].append(("create",{
                    "invoice_id": inv.id,
                    "amount": amount
                }))
                if obj.actual_shipping_fee:
                    vals["adjust_lines"].append(("create",{
                        "account_id": acc.shopee_charged_shipping_fee_account_id.id,
                        "track_id": acc.track_id.id,
                        "amount": -1 * obj.actual_shipping_fee,
                    }))
                    amount -= obj.actual_shipping_fee
                elif obj.estimated_shipping_fee:
                    vals["adjust_lines"].append(("create",{
                        "account_id": acc.shopee_charged_shipping_fee_account_id.id,
                        "track_id": acc.track_id.id,
                        "amount": -1 * obj.estimated_shipping_fee,
                    }))
                    amount -= obj.estimated_shipping_fee
                if amount != obj.escrow_amount:
                    vals["adjust_lines"].append(("create",{
                        "account_id": acc.payment_adjustment_account_id.id,
                        "track_id": acc.track_id.id,
                        "amount": obj.escrow_amount - amount,
                    }))
                payment_id = get_model("account.payment").create(vals)
                get_model("account.payment").post([payment_id])
            except Exception as e:
                if context.get("skip_error"):
                    logs = obj.logs or ""
                    log = "%s : shopee.order.pay_invoice\n%s\n" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),str(e))
                    log += "(user_id %s, company_id %s)\n" % (access.get_active_user() ,access.get_active_company())
                    log += "-" * 10
                    log += "\n\n"
                    logs = log + logs
                    obj.write({"logs":logs})
                    continue
                else:
                    raise Exception(e)

    def get_weight(self, ids, context={}):
        # print("shopee.order.get_weight",ids)
        vals = {}
        for obj in self.browse(ids):
            if not obj.items:
                continue
            weight=0
            for item in obj.items:
                weight += item.weight or 0
            vals[obj.id] = weight
        return vals

    def get_show_warning(self, ids, context={}):
        # print("shopee.order.get_show_warning",ids)
        vals = {}
        for obj in self.browse(ids):
            check = False
            if obj.order_status == "CANCELLED" or obj.ignore_warning:
                vals[obj.id] = False
                continue
            if not obj.pickings:
                check = True
            if obj.account_id.require_invoice and not obj.invoices:
                check = True
            vals[obj.id] = check
        # print("vals", vals)
        return vals

    def ignore_warning(self, ids, context={}):
        # print("shopee.order.ignore_warning",ids)
        self.write(ids,{"ignore_warning":True})
        self.function_store(ids)

    def search_show_warning(self, clause, context={}): #XXX not used
        # print("shopee.order.search_show_warning",clause)
        val = clause[2]
        ids = self.search([])
        res = self.get_show_warning(ids)
        ids2 = [x for x in res if res[x] == val]
        return ["id","in",ids2]


ShopeeOrder.register()

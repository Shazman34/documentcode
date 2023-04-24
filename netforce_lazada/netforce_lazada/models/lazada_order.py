from netforce.model import Model, fields, get_model
from netforce import access
from netforce import config
from netforce import tasks
import requests
import hashlib
import hmac
from datetime import *
import time
import json
from netforce import database

class LazadaOrder(Model):
    _name = "lazada.order"
    _string = "Lazada Order"
    _fields = {
        "sync_records": fields.One2Many("sync.record","related_id","Sync Records"),
        "sync_id": fields.Char("Sync ID",function="get_sync_id",function_search="search_sync_id"),
        "account_id": fields.Many2One("lazada.account","Lazada Account",search=True),
        "order_sn": fields.Char("Order ID",required=True,search=True),
        "order_status": fields.Char("Order Status",required=True, search=True),
        "order_create_time": fields.DateTime("Order Create Time",required=True, search=True),
        "region": fields.Char("Region"),
        "currency": fields.Char("Currency"),
        # "cod": fields.Boolean("cod"),
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
        "items": fields.One2Many("lazada.order.item","order_id","Items"),
        "shipping": fields.One2Many("lazada.order.shipping","order_id","Shipping"),
        "dropoff": fields.Boolean("DropOff"),
        "dropoff_info": fields.Text("DropOff Info"),
        "pickup": fields.Boolean("PickUp"),
        "pickup_info": fields.Text("PickUp Info"),
        "non_integrated": fields.Boolean("Non Integrated"),
        "non_integrated_info": fields.Text("Non Integrated Info"),
        "tracking_number": fields.Char("Tracking Number",search=True),
        "package_number": fields.Char("Package Number",search=True),
        "sale_orders": fields.One2Many("sale.order","related_id","Sale Orders"),
        "pickings": fields.One2Many("stock.picking","related_id","Stock Pickings"),
        "invoices": fields.One2Many("account.invoice","related_id","Invoices"),
        "payments": fields.One2Many("account.payment","related_id","Payments"),
        # "weight": fields.Decimal("weight",function="get_weight"),
        "show_warning": fields.Boolean("Show Warning",function="get_show_warning",store=True, search=True),
        "logs": fields.Text("Logs"),
        "created_at": fields.DateTime("Created Time"),
        "updated_at": fields.DateTime("Updated Time"),
        "qty": fields.Char("Quantity")
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
        print("lazada.order.refresh_order",ids)
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
            i += 1
    
    def create_order(self, acc_id, vals, context={}):
        print("create_order",acc_id,vals)
        settings = get_model("lazada.settings").browse(1)
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
            "account_id": "lazada.account,%s"%acc_id,
            })]
        order_id = self.create(create_vals)
        self.get_tracking_number([order_id],context=context)
        if settings.order_auto_copy_to_sale:
            self.copy_to_sale([order_id],context={"skip_error":True})
        if settings.order_auto_copy_to_picking:
            self.copy_to_picking([order_id],context={"skip_error":True})
        self.function_store([order_id])
        return order_id

    def update_order(self, ids, acc_id, vals, context={}):
        print("Update Order: ids:%s, vals:%s"%(ids, vals))
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
            "account_id": "lazada.account,%s"%acc_id,
            })]
        order.write(write_vals)
        settings = get_model("lazada.settings").browse(1)
        if settings.order_auto_copy_to_picking and not order.pickings:
            new_context = context.copy()
            new_context["skip_error"] = True
            order.copy_to_picking(context=new_context)
        self.get_tracking_number([order.id],context=context)
        self.function_store([order.id])

    def get_shipping_parameter(self,ids,context={}):
        for obj in self.browse(ids):
            acc = obj.account_id
            if not acc:
                raise Exception("Missing Lazada Account in Lazada Order: %s" % obj.order_sn)
            if not acc.shop_idno:
                raise Exception("Missing shop ID")
            if not acc.token:
                raise Exception("Missing token")
            path="/api/v2/logistics/get_shipping_parameter"
            url = get_model("lazada.account").generate_url(account_id=acc.id,path=path)
            url += "&order_sn=%s" % obj.order_sn
            print("url",url)
            req=requests.get(url)
            res=req.json()
            if res.get("error"):
                raise Exception("Sync error: %s"%res)
            print("res",res)
            resp=res["response"]
            write_vals= {}
            if "dropoff" in resp["info_needed"]:
                write_vals["dropoff"] = True
                write_vals["dropoff_info"] = json.dumps(resp["info_needed"]["dropoff"])
            if "pickup" in resp["info_needed"]:
                write_vals["pickup"] = True
                write_vals["pickup_info"] = json.dumps(resp["info_needed"]["pickup"])
            if "non_integrated" in resp["info_needed"]:
                write_vals["non_integrated"] = True
                write_vals["non_integrated_info"] = json.dumps(resp["info_needed"]["non_integrated"])
            obj.write(write_vals)

    def ship_order(self,ids,context={}):
        print("lazada.order.ship_order",ids)
        try:
            self.get_shipping_parameter(ids, context=context)
        except:
            pass
        for obj in self.browse(ids):
            acc = obj.account_id
            if not acc:
                raise Exception("Missing Lazada Account in Lazada Order: %s" % obj.order_sn)
            path = "/api/v2/logistics/ship_order"
            url = get_model("lazada.account").generate_url(account_id=acc.id,path=path)
            body={"order_sn":obj["order_sn"]}
            if obj.pickup:
                body["pickup"] = {}
            if obj.dropoff:
                body["dropoff"] = {}
            if obj.non_integrated:
                body["non_integrated"] = {}
            headers={"Content-Type":"application/json"}

            # post request and process
            req=requests.post(url,json=body,headers=headers)
            res=req.json()
            print("res",res)
            if res.get("error"):
                raise Exception(res["message"])
        return {
            "alert": "Orders Shipped Successfully"
        }

    def get_tracking_number(self,ids,context={}):
        def sign(secret, api, parameters):
            # ===========================================================================
            # @param secret
            # @param parameters
            # ===========================================================================
            sort_dict = sorted(parameters)

            parameters_str = "%s%s" % (api,
                                       str().join('%s%s' % (key, parameters[key]) for key in sort_dict))

            h = hmac.new(secret.encode(encoding="utf-8"), parameters_str.encode(encoding="utf-8"),
                         digestmod=hashlib.sha256)

            return h.hexdigest().upper()
        vals = {}
        for obj in self.browse(ids):
            get_order = get_model("lazada.order").browse(obj.id)
            order_id = get_order.order_sn
            account_id = get_order.account_id.id
            account = get_model("lazada.account").search_browse([["id", "=", account_id]])
            app_key = account[0].shop_idno
            app_secret = account[0].auth_code
            headers = {"Content-Type": "application/json"}
            sign_method = "sha256"
            timest = int(time.time() * 1000)
            base_url = "https://api.lazada.com.my/rest"
            path = "/logistic/order/trace"
            access_token = account[0].token
            params = {
                "app_key": app_key,
                "access_token": access_token,
                "sign_method": sign_method,
                "timestamp": timest,
                "order_id": order_id
            }
            signature = sign(app_secret, path, params)
            params = "?app_key=%s&access_token=%s&order_id=%s&timestamp=%s&sign_method=%s&sign=%s" % (
                    app_key, access_token,order_id ,timest, sign_method, signature)
            url = base_url + path + params
            res = (requests.get(url, headers=headers)).json()
            get_order = get_model("lazada.order").browse(obj.id)
            if 'result' in res:
                tracking_number = res['result']['module'][0]['package_detail_info_list'][0]['tracking_number']
                package_number = res['result']['module'][0]['package_detail_info_list'][0]['ofc_package_id']
                get_order.write({"tracking_number": tracking_number})
                get_order.write({"package_number": package_number})
                get_order_shipping = get_model("lazada.order.shipping")
                for logistic_info in res['result']['module'][0]['package_detail_info_list'][0]['logistic_detail_info_list']:
                    try:
                        title = logistic_info['title']
                    except:
                        title = None
                    try:
                        detail_type = ((logistic_info['detail_type']).replace("_", " ")).title()
                    except:
                        detail_type = None
                    try:
                        description = logistic_info['description']
                    except:
                        description = None
                    try:

                        event_time = (time.ctime(int(logistic_info['event_time'])))[:-6]
                    except:
                        event_time = None
                    get_order_shipping.create({
                        "order_id": obj.id,
                        "title": title,
                        "detail_type": detail_type,
                        "description": description,
                        "event_time": event_time
                    })
            else:
                raise Exception(res['message'])



    def get_invoice_detail(self,ids,context={}):
        def sign(secret, api, parameters):
            # ===========================================================================
            # @param secret
            # @param parameters
            # ===========================================================================
            sort_dict = sorted(parameters)

            parameters_str = "%s%s" % (api,
                                       str().join('%s%s' % (key, parameters[key]) for key in sort_dict))

            h = hmac.new(secret.encode(encoding="utf-8"), parameters_str.encode(encoding="utf-8"),
                         digestmod=hashlib.sha256)

            return h.hexdigest().upper()
        vals = {}
        for obj in self.browse(ids):
            print("print 1")
            get_order = get_model("lazada.order").browse(obj.id)
            order_id = get_order.order_sn
            account_id = get_order.account_id.id
            account = get_model("lazada.account").search_browse([["id", "=", account_id]])
            app_key = account[0].shop_idno
            app_secret = account[0].auth_code
            headers = {"Content-Type": "application/json"}
            sign_method = "sha256"
            timest = int(time.time() * 1000)
            base_url = "https://api.lazada.com.my/rest"
            path = "/finance/transaction/details/get"
            access_token = account[0].token
            params = {
                "app_key": app_key,
                "access_token": access_token,
                "sign_method": sign_method,
                "timestamp": timest,
                "start_time": "2022-07-02",
                "end_time": "2022-10-30"
            }
            signature = sign(app_secret, path, params)
            params = "?app_key=%s&access_token=%s&timestamp=%s&sign_method=%s&sign=%s&start_time=%s&end_time=%s" % (
                    app_key, access_token ,timest, sign_method, signature,"2022-07-02","2022-10-30")
            url = base_url + path + params
            res = (requests.get(url, headers=headers)).json()
            # raise Exception(res['data'][0])
            print("print 2")
            get_order = get_model("lazada.order").browse(obj.id)
            get_order.write({
                "invoice_data_number":res['data'][0]['transaction_number'],
                "invoice_data_total_value":float((res['data'][0]['amount']).replace(",","").replace("-", "")),
                "invoice_data_products_total_value":float((res['data'][0]['amount']).replace(",","").replace("-", ""))
            })
            print("print 3")
            # if 'result' in res:
            #     tracking_number = res['result']['module'][0]['package_detail_info_list'][0]['tracking_number']
            #     package_number = res['result']['module'][0]['package_detail_info_list'][0]['ofc_package_id']
            #     get_order.write({"tracking_number": tracking_number})
            #     get_order.write({"package_number": package_number})
            #     get_order_shipping = get_model("lazada.order.shipping")
            #     for logistic_info in res['result']['module'][0]['package_detail_info_list'][0]['logistic_detail_info_list']:
            #         try:
            #             title = logistic_info['title']
            #         except:
            #             title = None
            #         try:
            #             detail_type = ((logistic_info['detail_type']).replace("_", " ")).title()
            #         except:
            #             detail_type = None
            #         try:
            #             description = logistic_info['description']
            #         except:
            #             description = None
            #         try:
            #
            #             event_time = (time.ctime(int(logistic_info['event_time'])))[:-6]
            #         except:
            #             event_time = None
            #         get_order_shipping.create({
            #             "order_id": obj.id,
            #             "title": title,
            #             "detail_type": detail_type,
            #             "description": description,
            #             "event_time": event_time
            #         })
            # else:
            #     raise Exception(res['message'])

        self.function_store(ids)


    def get_escrow_detail(self,ids,context={}):
        print("lazada.order.get_escrow_detail",ids)
        for obj in self.browse(ids):
            write_vals = {}
            try:
                acc = obj.account_id
                if not acc:
                    raise Exception("Missing Lazada Account in Lazada Order: %s" % obj.order_sn)
                if not acc.shop_idno:
                    raise Exception("Missing shop ID")
                if not acc.token:
                    raise Exception("Missing token")
                company_id = access.get_active_company()
                if not company_id:
                    access.set_active_company(acc.company_id.id)
                shop_id=int(acc.shop_idno)
                partner_id=int(config.get("lazada_partner_id"))
                partner_key=config.get("lazada_partner_key")
                timest=int(time.time())
                path="/api/v2/payment/get_escrow_detail"
                base_string="%s%s%s%s%s"%(partner_id,path,timest,acc.token,shop_id)
                sign=hmac.new(partner_key.encode(),base_string.encode(),hashlib.sha256).hexdigest()
                #base_url="https://partner.test-stable.shopeemobile.com"
                base_url="https://partner.shopeemobile.com"
                url=base_url+path+"?partner_id=%s&timestamp=%s&sign=%s&shop_id=%s&access_token=%s"%(partner_id,timest,sign,shop_id,acc.token)
                url += "&order_sn=%s" % obj.order_sn
                print("url",url)
                req=requests.get(url)
                res=req.json()
                if res.get("error"):
                    raise Exception("Sync error: %s"%res)
                print("res",res)
                resp=res["response"]
            except Exception as e:
                if context.get("skip_error"):
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
                    raise Exception("No Lazada Account Assigned to Order: %s" % obj.order_sn)
                contact = acc.contact_id
                if not contact:
                    raise Exception("Unable to Create Sales Order without Contact. Please enable contact module in Lazada Settings")
                sale_vals={
                    "contact_id": contact.id,
                    "date": obj.order_create_date,
                    "due_date": "2021-05-29",
                    "other_info": obj.note,
                    "lines": [],
                    "related_id": "lazada.order,%s"%obj.id
                }
                for it in obj.items:
                    #res=get_model("product").search([["sync_records.lazada_id","=",it["item_id"]]])
                    res=get_model("sync.record").search([["sync_id","=",str(it.item_id)],["related_id","like","product"],["account_id","=","lazada.account,%s"%acc.id]]) # XXX
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
    
    def copy_to_picking(self,ids,context={}):
        user_id = access.get_active_user()
        if not user_id:
            access.set_active_user(1)
        settings = get_model("lazada.settings").browse(1)
        pick_ids = []
        for obj in self.browse(ids): 
            try:
                if obj.pickings:
                    raise Exception("Order already Have picking: %s" % obj.order_sn)
                acc = obj.account_id
                if acc.company_id:
                    access.set_active_company(acc.company_id.id)
                if not acc.stock_journal_id:
                    raise Exception("Missing Stock Journal for Lazada Account: %s" % acc.name)
                # if not acc.stock_journal_id.location_from_id:
                #     raise Exception("Missing From Location in Stock Journal: %s" % acc.stock_journal_id.name)
                # if not acc.stock_journal_id.location_to_id:
                #     raise Exception("Missing To Location in Stock Journal: %s" % acc.stock_journal_id.name)
                invoice_number = "ZCI-"+str(obj.order_sn)
                get_invoice_ = get_model("account.invoice").search_browse(["number", "=", "%s" %invoice_number])
                try:
                    invoice_idd = get_invoice_[0].id
                except:
                    invoice_idd = None

                if invoice_idd:
                    pick_vals={
                        "type": "out",
                        "contact_id": acc.contact_id.id if acc.contact_id else None,
                        "journal_id": 4,
                        "date": obj.order_create_time,
                        "recipient_first_name": obj.recipient_address_name,
                        "recipient_address": obj.recipient_address_full_address,
                        "recipient_phone": obj.recipient_address_phone,
                        "recipient_postcode": obj.recipient_address_zipcode,
                        "recipient_city": obj.recipient_address_city,
                        "recipient_province": obj.recipient_address_state,
                        "recipient_country": obj.recipient_address_region,
                        "ship_tracking": obj.tracking_number,
                        "lines": [],
                        "number": "GI-"+str(obj.order_sn),
                        "related_id": "account.invoice,%s"%invoice_idd,
                        "invoice_id": invoice_idd,
                        "state": "draft"
                    }
                else:
                    pick_vals = {
                        "type": "out",
                        "contact_id": acc.contact_id.id if acc.contact_id else None,
                        "journal_id": 4,
                        "date": obj.order_create_time,
                        "recipient_first_name": obj.recipient_address_name,
                        "recipient_address": obj.recipient_address_full_address,
                        "recipient_phone": obj.recipient_address_phone,
                        "recipient_postcode": obj.recipient_address_zipcode,
                        "recipient_city": obj.recipient_address_city,
                        "recipient_province": obj.recipient_address_state,
                        "recipient_country": obj.recipient_address_region,
                        "ship_tracking": obj.tracking_number,
                        "lines": [],
                        "number": "GI-" + str(obj.order_sn),
                        "state":"draft"
                    }
                # if settings.use_order_num_for_picking:
                #     pick_vals["number"] = obj.order_sn
                # if not obj.shipping_carrier:
                #     raise Exception("No Shipping Carrier assigned for order: %s" % obj.order_sn)
                # ship_method_res = get_model("ship.method").search([["name","=",obj.shipping_carrier]])
                # if not ship_method_res:
                #     raise Exception("Shipping Method not found for %s" % obj.shipping_carrier)
                # else:
                #     ship_method_id = ship_method_res[0]
                # pick_vals["ship_method_id"] = ship_method_id
                # exp_ship_date = datetime.strftime(datetime.strptime(obj.order_create_time,"%Y-%m-%d %H:%M:%S") + timedelta(days=obj.days_to_ship),"%Y-%m-%d")
                # exp_ship_date = datetime.strptime(obj.order_create_time,"%Y-%m-%d %H:%M:%S")
                # pick_vals["exp_ship_date"] = exp_ship_date
                for it in obj.items:
                    # if not it.item_id:
                    #     raise Exception("Missing Item ID")
                    lazada_prods = get_model("lazada.product").search_browse([["account_id","=",acc.id],["sync_id","=",str(it.item_id)]])
                    # lazada_prods = get_model("lazada.product").search_browse([["account_id","=",acc.id]])
                    if not lazada_prods:
                        raise Exception("Lazada Product not found: %s (Sync ID: %s)" % (it.item_sku, it.item_id))
                    lazada_prod = lazada_prods[0]
                    print("product_id", lazada_prod.product_id)
                    if not it.model_id:
                        prod = lazada_prod.product_id
                        if not prod:
                            raise Exception("System Product not found for item: %s (Sync ID: %s)" % (lazada_prod.item_sku, it.item_id))
                    else:
                        models = get_model("lazada.product.model").search_browse([["lazada_product_id.sync_id","=",str(it.item_id)],["sync_id","=",str(it.model_id)]])
                        if not models:
                            raise Exception("Lazada Product Model Not Found: (item: %s (Sync ID: %s), model: %s (Sync ID: %s))" % (it.item_sku, it.item_id, it.model_name, it.model_id))
                        model = models
                        prod = model.product_id
                        if not prod:
                            raise Exception("System Product not found for: (item: %s (Sync ID: %s), model: %s (Sync ID: %s))" % (it.item_sku, it.item_id, it.model_name, it.model_id))
                    line_vals={
                        "product_id": prod.id,
                        "description": it.item_name,
                        # "qty": it.model_quantity_purchased,
                        "uom_id": prod.uom_id.id,
                        "qty": 1,
                        "location_from_id": acc.stock_journal_id.location_from_id.id,
                        "location_to_id": acc.stock_journal_id.location_to_id.id,

                    }
                    pick_vals["lines"].append(("create",line_vals))
                # pick_id = get_model("stock.picking").create(pick_vals,context={"journal_id":acc.stock_journal_id.id})
                try:
                    get_stock_picking = get_model("stock.picking").search_browse(
                        [["related_id", "=", "lazada.order,%s" % obj.id]])
                    if not get_stock_picking:
                        pick_id = get_model("stock.picking").create(pick_vals)

                        pick_ids.append(pick_id)
                        # try:
                        #     get_model("stock.picking").set_done_fast(pick_ids)
                        # except Exception as e:
                        #     if context.get("skip_error"):
                        #         pass
                        #     else:
                        #         raise Exception(e)
                    else:
                        raise Exception("Already exist")

                except Exception as e:
                    raise Exception(e)

                print("asad print 5")
                get_invoice = get_model("account.invoice").search_browse([["related_id", "=", "lazada.order,%s"%obj.id]])
                if get_invoice:
                    get_model("lazada.order").restore_warning(ids)
                else:
                    print("no invoice")
            except Exception as e:
                print("Asad print 6", e)
                if context.get("skip_error"):
                    logs = obj.logs or ""
                    log = "%s : lazada.order.copy_to_picking\n%s\n" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),str(e))
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
        # self.get_tracking_number(ids, context=context)
        # self.function_store(ids)
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
        self.copy_to_picking(ids, context=context)

    def copy_to_invoice(self,ids,context={}):
        for obj in self.browse(ids):
            try:
                print("print 1")
                acc = obj.account_id
                if not acc:
                    raise Exception("No Lazada Account Assigned to Order: %s" % obj.order_sn)
                contact = acc.contact_id
                if not contact:
                    raise Exception("Unable to Create Invoice without Contact. Please choose default contact in Lazada account")
                defaults = get_model("account.invoice").default_get(context={"inv_type":"invoice","type":"out"})
                vals={
                    "number": "ZCI-"+str(obj.order_sn),
                    "type": "out",
                    "inv_type": "invoice",
                    "contact_id": contact.id,
                    "date": obj.order_create_time,
                    "due_date":obj.order_create_time,
                    "other_info": obj.note,
                    "memo": "Order ID - " + str(obj.order_sn),
                    "state": "waiting_payment",
                    "lines": [],
                    "related_id": "lazada.order,%s"%obj.id
                }
                print(vals)
                for it in obj.items:
                    print("inovice item", it.id)
                    # res=get_model("sync.record").search([["related_id","like","product"],["account_id","=","lazada.account,%s"%acc.id]]) # XXX
                    # if not res:
                    #     raise Exception("Product not found: %s"%it.item_id)
                    # sync_id=res[0]
                    # sync=get_model("sync.record").browse(sync_id)
                    lazada_prods = get_model("lazada.product").search_browse([["account_id","=",acc.id],["sync_id","=",str(it.item_id)]])

                    # lazada_prods = get_model("lazada.product").search_browse([["account_id", "=", acc.id]])
                    if not lazada_prods:
                        raise Exception("Lazada Product not found: %s (Sync ID: %s)" % (it.item_sku, it.item_id))
                    lazada_prod = lazada_prods[0]
                    if not it.model_id:
                        prod = lazada_prod.product_id
                        if not prod:
                            raise Exception("System Product not found for item: %s (Sync ID: %s)" % (
                            lazada_prod.item_sku, it.item_id))
                    else:
                        models = get_model("lazada.product.model").search_browse(
                            [["lazada_product_id.sync_id", "=", str(it.item_id)], ["sync_id", "=", str(it.model_id)]])
                        if not models:
                            raise Exception(
                                "Lazada Product Model Not Found: (item: %s (Sync ID: %s), model: %s (Sync ID: %s))" % (
                                it.item_sku, it.item_id, it.model_name, it.model_id))
                        model = models[0]
                        prod = model.product_id
                        if not prod:
                            raise Exception(
                                "System Product not found for: (item: %s (Sync ID: %s), model: %s (Sync ID: %s))" % (
                                it.item_sku, it.item_id, it.model_name, it.model_id))

                    # prod_id=sync.related_id.id
                    prod_id=prod.id
                    line_vals={
                        "product_id": prod_id,
                        "description": it.item_name,
                        "qty": 1,
                        "unit_price": it.item_price,
                        "account_id": acc.sale_account_id.id,
                        "track_id": acc.track_id.id,
                        # "amount": (it.model_quantity_purchased or 0) * (it.model_discounted_price or 0),
                        "amount": it.item_price
                    }
                    vals["lines"].append(("create",line_vals))
                try:
                    get_stock_picking = get_model("account.invoice").search_browse([["related_id", "=", "lazada.order,%s" % obj.id]])
                    if not get_stock_picking:
                        inv_id = get_model("account.invoice").create(vals)
                        try:
                            get_stock_inv = get_model("stock.picking").search_browse(
                                [["number", "=", "GI-%s" % obj.order_sn]])
                            get_stock_inv.write({"invoice_id": inv_id,"related_id":"lazada.order,%s"%obj.id})
                        except:
                            pass
                    else:
                        raise Exception("Already exist")
                except Exception as e:
                    raise Exception(e)
            except Exception as e:
                if context.get("skip_error"):
                    continue
                else:
                    raise Exception(e)
        # self.function_store(ids)
        get_stock_picking = get_model("stock.picking").search_browse([["number", "=", "GI-%s" % obj.order_sn]])
        if get_stock_picking:
            get_model("lazada.order").restore_warning(ids)
        else:
            print("debugging no invoice")
        if len(ids) == 1:
            return {
                "next":{
                    "name": "cust_invoice",
                    "mode": "form",
                    "active_id": str(inv_id),
                    "target": "new_window",
                }
            }
        else: 
            return {
                "alert": "%s Orders Copied Successfully" % len(ids)
            }

    def get_weight(self, ids, context={}):
        # print("lazada.order.get_weight",ids)
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
        print("lazada.order.get_show_warning",ids)
        vals = {}
        for obj in self.browse(ids):
            check = False
            if obj.order_status == "CANCELLED":
                vals[obj.id] = False
                continue
            if not obj.pickings:
                check = True
            if obj.account_id.require_invoice and not obj.invoices:
                check = True
            vals[obj.id] = check
        print("vals", vals)
        return vals

    def search_show_warning(self, clause, context={}): #XXX not used
        print("lazada.order.search_show_warning",clause)
        val = clause[2]
        ids = self.search([])
        res = self.get_show_warning(ids)
        ids2 = [x for x in res if res[x] == val]
        return ["id","in",ids2]

    def match_invoice(self,ids,context={}):
        print("lazada.order.match_invoice")
        for obj in self.browse(ids):
            if obj.invoices:
                continue
            invoices = get_model("account.invoice").search_browse([["number","ilike",obj.order_sn]])
            if not invoices:
                continue
            elif len(invoices) > 1:
                raise Exception("More than 1 Invoice found for Order: %s" % obj.order_sn)
            invoices[0].write({"related_id":"lazada.order,%s"%obj.id})

    def match_picking(self, ids, context={}):
        print("lazada.order.match_picking")
        for obj in self.browse(ids):
            if obj.pickings:
                continue
            pickings = get_model("stock.picking").search_browse(
                [["number", "ilike", obj.order_sn], ["type", "=", "out"]])
            if not pickings:
                continue
            elif len(pickings) > 1:
                raise Exception("More than 1 Goods Issue found for Order: %s" % obj.order_sn)
            pickings[0].write({"related_id": "lazada.order,%s" % obj.id})

    def start_job(self,method,args=[],opts={},context={}):
        print("hello")
        def sign(secret, api, parameters):
            # ===========================================================================
            # @param secret
            # @param parameters
            # ===========================================================================
            sort_dict = sorted(parameters)

            parameters_str = "%s%s" % (api,
                                       str().join('%s%s' % (key, parameters[key]) for key in sort_dict))

            h = hmac.new(secret.encode(encoding="utf-8"), parameters_str.encode(encoding="utf-8"),
                         digestmod=hashlib.sha256)

            return h.hexdigest().upper()

        if method == "get_orders":
            app_key = "111456"
            app_secret = "Xp5vDjQwAiLQzclVQWddVX3RXq7wh0Xf"
            headers = {"Content-Type": "application/json"}
            sign_method = "sha256"
            timest = int(time.time() * 1000)
            createdafter = '2017-02-10T09:00:00'
            base_url = "https://api.lazada.com.my/rest"
            path = "/orders/get"
            account_id = args[0][0]
            db = database.get_connection()
            get_account = get_model("lazada.account").browse(account_id)
            print("access_token", get_account.token)
            access_token = get_account.token
            params = {
                "access_token": access_token,
                "app_key": app_key,
                "sign_method": sign_method,
                "timestamp": timest,
                "created_after": createdafter
            }
            signature = sign(app_secret, path, params)
            _params = "?app_key=%s&created_after=%s&access_token=%s&timestamp=%s&sign_method=%s&sign=%s" % (
                app_key,createdafter, access_token,timest, sign_method, signature)
            url = base_url + path + _params
            req = requests.get(url, headers=headers)
            res = req.json()
            print("response", res)
            db = database.get_connection()
            get_order = get_model("lazada.order")
            for order in res['data']['orders']:
                try:
                    get_order.create({
                        "account_id": args[0][0],
                        "sync_id" : order['order_id'],
                        "order_sn" : order['order_id'],
                        "order_status" : order['statuses'][0],
                        "order_create_time" : order['created_at'],
                        "region" : order['address_shipping']['country'],
                        "currency" : "Malaysian ringgit",
                        "total_amount" : order['price'],
                        "payment_method" : order['payment_method'],
                        "estimated_shipping_fee" : order['shipping_fee'],
                        "message_to_seller" : order['remarks'],
                        "buyer_username" : order['customer_first_name'],
                        "recipient_address_name" : order['address_shipping']['first_name'],
                        "recipient_address_phone" : order['address_shipping']['phone'],
                        "recipient_address_city" : order['address_shipping']['city'],
                        "recipient_address_region" : order['address_shipping']['country'],
                        "recipient_address_zipcode" : order['address_shipping']['post_code'],
                        "recipient_address_full_address" : order['address_shipping']['address1']
                    })
                    db.commit()
                except Exception as e:
                    print("Exception is", e)
            print("response", res)
        if method == "copy_to_picking_skip_error":
            context["skip_error"] = True
            ids= args[0]
            self.copy_to_picking(ids, context=context)
            print("copy to picking skip error")
        if method == "get_payments":
            app_key = "111456"
            app_secret = "Xp5vDjQwAiLQzclVQWddVX3RXq7wh0Xf"
            headers = {"Content-Type": "application/json"}
            sign_method = "sha256"
            timest = int(time.time() * 1000)
            createdafter = '2017-02-10T09:00:00'
            base_url = "https://api.lazada.com.my/rest"
            path = "/finance/payout/status/get"
            account_id = args[0][0]
            db = database.get_connection()
            get_account = get_model("lazada.account").browse(account_id)
            print("access_token", get_account.token)
            access_token = get_account.token
            params = {
                "access_token": access_token,
                "app_key": app_key,
                "sign_method": sign_method,
                "timestamp": timest,
                "created_after": createdafter
            }
            signature = sign(app_secret, path, params)
            _params = "?app_key=%s&created_after=%s&access_token=%s&timestamp=%s&sign_method=%s&sign=%s" % (
                app_key, createdafter, access_token, timest, sign_method, signature)
            url = base_url + path + _params
            req = requests.get(url, headers=headers)
            res = req.json()
            print("response", res)
            db = database.get_connection()
            get_order = get_model("account.payment")
            for payment in res['data']:
                try:
                    vals = {
                        # "account_id": account_id,
                        "amount_subtotal": float(payment['subtotal1']),
                        "amount_total": float(payment['subtotal1']),
                        "amount_payment": float(payment['closing_balance']),
                        "amount_adjust": float(payment['fees_total']),
                        "currency_id": 1,
                        "type": "in",
                        "transaction_no" : payment['statement_number'],
                        "number" : payment['statement_number'],
                        "state": "posted",
                        # "date": datetime.datetime.fromtimestamp(payment['created_at'][:-6]).strftime("%Y-%m-%d"),
                        "memo": "Lazada",
                    }
                    pmt_id = get_model("account.payment").create(vals)
                    db.commit()
                except Exception as e:
                    print("Exception is", e)
            print("response", res)
        if method == "get_product":
            app_key = "111456"
            app_secret = "Xp5vDjQwAiLQzclVQWddVX3RXq7wh0Xf"
            headers = {"Content-Type": "application/json"}
            sign_method = "sha256"
            timest = int(time.time() * 1000)
            base_url = "https://api.lazada.com.my/rest"
            path = "/products/get"
            account_id = args[0][0]
            db = database.get_connection()
            get_account = get_model("lazada.account").browse(account_id)
            access_token = get_account.token
            params = {
                "app_key": app_key,
                "access_token": access_token,
                "sign_method": sign_method,
                "timestamp": timest
            }
            signature = sign(app_secret, path, params)

            params = "?app_key=%s&access_token=%s&timestamp=%s&sign_method=%s&sign=%s" % (
                app_key, access_token, timest, sign_method, signature)
            url = base_url + path + params
            req = requests.get(url, headers=headers)
            res = req.json()
            db = database.get_connection()
            get_product = get_model("lazada.product")
            for product in res['data']['products']:
                get_product.create({
                    "account_id": args[0][0],
                    "item_name": product['attributes']['name'],
                    "description": product['attributes']['description'],
                    "lazada_create_time":datetime.datetime.fromtimestamp(int(product['created_time'])/1000).strftime('%Y-%m-%d %H:%M:%S'),
                    "lazada_update_time":datetime.datetime.fromtimestamp(int(product['updated_time'])/1000).strftime('%Y-%m-%d %H:%M:%S'),
                    "images": product["images"],
                    "item_sku": product["skus"][0]['SellerSku'],
                    "sync_id" : product['item_id'],
                    "trialProduct": product['trialProduct'],
                    "primary_category":product['primary_category'],
                    "marketImages":product["marketImages"],
                    "attributes":str(product['attributes']),
                    "item_status": product['status']
                })
                db.commit()
            print("response", res)
        if method == "copy_to_invoice":
            ids = args[0]
            self.copy_to_invoice(ids,context=context)
        if method == "match_invoice":
            ids = args[0]
            self.match_invoice(ids, context=context)
        if method == "match_picking":
            ids = args[0]
            self.match_picking(ids, context=context)

    def cancel_order(self, ids, context={}):
        def sign(secret, api, parameters):
            # ===========================================================================
            # @param secret
            # @param parameters
            # ===========================================================================
            sort_dict = sorted(parameters)

            parameters_str = "%s%s" % (api,
                                       str().join('%s%s' % (key, parameters[key]) for key in sort_dict))

            h = hmac.new(secret.encode(encoding="utf-8"), parameters_str.encode(encoding="utf-8"),
                         digestmod=hashlib.sha256)

            return h.hexdigest().upper()

        for obj in self.browse(ids):
            db = database.get_connection()
            account = get_model("lazada.account").search_browse([["id", "=", obj.account_id.id]])
            app_key = account[0].shop_idno
            app_secret = account[0].auth_code
            headers = {"Content-Type": "application/json"}
            sign_method = "sha256"
            timest = int(time.time() * 1000)
            base_url = "https://api.lazada.com.my/rest"
            path = "/order/cancel"
            access_token = account[0].token
            print("order id ", str(obj.order_sn))
            params = {
                "access_token": access_token,
                "app_key": app_key,
                "sign_method": sign_method,
                "timestamp": timest,
                "order_item_id": str(obj.order_sn),
                "reason_id": "5"
            }
            signature = sign(app_secret, path, params)
            _params = "?app_key=%s&access_token=%s&timestamp=%s&sign_method=%s&sign=%s&order_item_id=%s&order_item_id=%s" % (
                app_key, access_token, timest, sign_method, signature, str(obj.order_sn), "5")
            url = base_url + path + _params
            req = requests.post(url, headers=headers)
            res = req.json()
            print(res)
            raise Exception(res)

    def repack_order(self, ids, context={}):
        def sign(secret, api, parameters):
            # ===========================================================================
            # @param secret
            # @param parameters
            # ===========================================================================
            sort_dict = sorted(parameters)

            parameters_str = "%s%s" % (api,
                                       str().join('%s%s' % (key, parameters[key]) for key in sort_dict))

            h = hmac.new(secret.encode(encoding="utf-8"), parameters_str.encode(encoding="utf-8"),
                         digestmod=hashlib.sha256)

            return h.hexdigest().upper()

        for obj in self.browse(ids):
            db = database.get_connection()
            account = get_model("lazada.account").search_browse([["id", "=", obj.account_id.id]])
            app_key = account[0].shop_idno
            app_secret = account[0].auth_code
            headers = {"Content-Type": "application/json"}
            sign_method = "sha256"
            timest = int(time.time() * 1000)
            base_url = "https://api.lazada.com.my/rest"
            path = "/order/repack"
            access_token = account[0].token
            print("order id ", str(obj.package_number))
            params = {
                "access_token": access_token,
                "app_key": app_key,
                "sign_method": sign_method,
                "timestamp": timest,
                "package_id": str(obj.package_number)
            }
            signature = sign(app_secret, path, params)
            _params = "?app_key=%s&access_token=%s&timestamp=%s&sign_method=%s&sign=%s&package_id=%s" % (
                app_key, access_token, timest, sign_method, signature, str(obj.package_number))
            url = base_url + path + _params
            req = requests.post(url, headers=headers)
            res = req.json()
            print(res)
            if "message" in res:
                raise Exception(res['message'])
            else:
                raise Exception(res)



    def ready_to_ship(self, ids, context={}):
        def sign(secret, api, parameters):
            # ===========================================================================
            # @param secret
            # @param parameters
            # ===========================================================================
            sort_dict = sorted(parameters)

            parameters_str = "%s%s" % (api,
                                       str().join('%s%s' % (key, parameters[key]) for key in sort_dict))

            h = hmac.new(secret.encode(encoding="utf-8"), parameters_str.encode(encoding="utf-8"),
                         digestmod=hashlib.sha256)

            return h.hexdigest().upper()

        for obj in self.browse(ids):
            db = database.get_connection()
            account = get_model("lazada.account").search_browse([["id", "=", obj.account_id.id]])
            app_key = account[0].shop_idno
            app_secret = account[0].auth_code
            headers = {"Content-Type": "application/json"}
            sign_method = "sha256"
            timest = int(time.time() * 1000)
            base_url = "https://api.lazada.com.my/rest"
            path = "/order/rts"
            access_token = account[0].token
            print("order id ", str(obj.package_number))
            params = {
                "access_token": access_token,
                "app_key": app_key,
                "sign_method": sign_method,
                "timestamp": timest,
                "delivery_type": "dropship",
                "order_item_ids": [obj.order_sn],
                "shipment_provider": "Drop-off: LEX MY, Delivery: LEX MY",
                "tracking_number": str(obj.tracking_number)

            }
            signature = sign(app_secret, path, params)
            _params = "?app_key=%s&access_token=%s&timestamp=%s&sign_method=%s&sign=%s&package_id=%s" % (
                app_key, access_token, timest, sign_method, signature, str(obj.package_number))
            url = base_url + path + _params
            req = requests.post(url, headers=headers)
            res = req.json()
            print(res)
            if "message" in res:
                raise Exception(res['message'])
            else:
                raise Exception(res)








            path = "/order/cancel"
            access_token = account[0].token
            print("order id ", str(obj.order_sn))
            params = {
                "access_token": access_token,
                "app_key": app_key,
                "sign_method": sign_method,
                "timestamp": timest,
                "order_item_id":str(obj.order_sn),
                "reason_id": "5"
            }
            signature = sign(app_secret, path, params)
            _params = "?app_key=%s&access_token=%s&timestamp=%s&sign_method=%s&sign=%s&order_item_id=%s&reason_id=%s" % (
                app_key, access_token, timest, sign_method, signature,str(obj.order_sn), "5")
            url = base_url + path + _params
            req = requests.post(url, headers=headers)
            res = req.json()
            print(res)

    def order_delivered(self, ids, context={}):
        def sign(secret, api, parameters):
            # ===========================================================================
            # @param secret
            # @param parameters
            # ===========================================================================
            sort_dict = sorted(parameters)

            parameters_str = "%s%s" % (api,
                                       str().join('%s%s' % (key, parameters[key]) for key in sort_dict))

            h = hmac.new(secret.encode(encoding="utf-8"), parameters_str.encode(encoding="utf-8"),
                         digestmod=hashlib.sha256)

            return h.hexdigest().upper()

        for obj in self.browse(ids):
            db = database.get_connection()
            account = get_model("lazada.account").search_browse([["id", "=", obj.account_id.id]])
            app_key = account[0].shop_idno
            app_secret = account[0].auth_code
            headers = {"Content-Type": "application/json"}
            sign_method = "sha256"
            timest = int(time.time() * 1000)
            base_url = "https://api.lazada.com.my/rest"
            path = "/order/sof/delivered"
            access_token = account[0].token
            print("order id ", str(obj.package_number))
            params = {
                "access_token": access_token,
                "app_key": app_key,
                "sign_method": sign_method,
                "timestamp": timest,
                "order_item_ids": [obj.order_sn]
            }
            signature = sign(app_secret, path, params)
            _params = "?app_key=%s&access_token=%s&timestamp=%s&sign_method=%s&sign=%s&order_item_ids=%s" % (
                app_key, access_token, timest, sign_method, signature, [obj.order_sn])
            url = base_url + path + _params
            req = requests.post(url, headers=headers)
            res = req.json()
            print(res)
            if "message" in res:
                raise Exception(res['message'])
            else:
                raise Exception(res)








            path = "/order/cancel"
            access_token = account[0].token
            print("order id ", str(obj.order_sn))
            params = {
                "access_token": access_token,
                "app_key": app_key,
                "sign_method": sign_method,
                "timestamp": timest,
                "order_item_id":str(obj.order_sn),
                "reason_id": "5"
            }
            signature = sign(app_secret, path, params)
            _params = "?app_key=%s&access_token=%s&timestamp=%s&sign_method=%s&sign=%s&order_item_id=%s&reason_id=%s" % (
                app_key, access_token, timest, sign_method, signature,str(obj.order_sn), "5")
            url = base_url + path + _params
            req = requests.post(url, headers=headers)
            res = req.json()
            print(res)

LazadaOrder.register()

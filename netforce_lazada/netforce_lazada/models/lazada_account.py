from netforce.model import Model, fields, get_model
from netforce import config
from netforce import utils
from netforce import database
from netforce import tasks
from netforce import access
import requests
import hashlib
import hmac
from datetime import *
import time
import datetime
import requests
import hashlib
import hmac
import time


class Account(Model):
    _name = "lazada.account"
    _string = "Lazada Account"
    _fields = {
        "name": fields.Char("Shop Name",required=True,search=True),
        "shop_idno": fields.Char("Shop ID",search=True),
        "auth_code": fields.Char("Auth Code"),
        "region": fields.Char("Region"),
        "status": fields.Char("Status"),
        "token": fields.Char("Token"),
        "refresh_token": fields.Char("Refresh Token"),
        "token_expiry_time": fields.DateTime("Token Expiry Time"),
        "sale_channel_id": fields.Many2One("sale.channel","Sales Channel"),
        "sync_records": fields.One2Many("sync.record","account_id","Sync Records"),
        "pricelist_id": fields.Many2One("price.list","Price List"),
        "stock_journal_id": fields.Many2One("stock.journal","Stock Journal"),
        "contact_id": fields.Many2One("contact","Default Contact"),
        "company_id": fields.Many2One("company","Company",search=True),
        "require_invoice": fields.Boolean("Require Invoice"),
        "order_last_update_time": fields.DateTime("Lazada Order Last Update Time"),
        "payment_last_update_time": fields.DateTime("Lazada Payment Last Update Time"),

        # Accounting Fields
        "sale_account_id": fields.Many2One("account.account", "Sales Account"),
        "track_id": fields.Many2One("account.track.categ", "Track-1"),
        "payment_adjustment_account_id": fields.Many2One("account.account", "Payment Adjustment Account"),
        "buyer_paid_shipping_fee_account_id": fields.Many2One("account.account", "Buyer Paid Shipping Fee Account"),
        "lazada_charged_shipping_fee_account_id": fields.Many2One("account.account",
                                                                  "Lazada Charged Shipping Fee Account"),
        "ewallet_account_id": fields.Many2One("account.account", "Lazada E-Wallet Account"),
        "debtor_account_id": fields.Many2One("account.account", "Debtor Account for Invoice"),
    }

    _base_url = "https://partner.shopeemobile.com"

    def generate_url(self,account_id=None,path=None,require_shop_id=True,require_token=True,context={}):
        # Check account
        app_key = "111456"
        app_secret = "Xp5vDjQwAiLQzclVQWddVX3RXq7wh0Xf"
        code = "0_111456_lKHyiw4zNhdZNXZWiOmBjFTh2379"
        base_url = "https://auth.lazada.com/rest"
        path = "/auth/token/create"
        timest = int(time.time() * 1000)
        code = code
        sign_method = "sha256"

        base_url = base_url
        path = path
        base_string = "%sapp_key%sapp_secret%scode%ssign_method%stimestamp%s" % (
            path, app_key, app_secret, code, sign_method, timest)
        print("base string first", base_string)
        sign = hmac.new(app_secret.encode(encoding="utf-8"), base_string.encode(encoding="utf-8"),
                        hashlib.sha256).hexdigest().upper()
        headers = {"Content-Type": "application/json"}
        body = {"app_key": app_key, "app_secret": app_secret, "code": code}
        params = "?app_key=%s&app_secret=%s&code=%s&timestamp=%s&sign_method=%s&sign=%s" % (
            app_key, app_secret, code, timest, sign_method, sign)
        url = base_url + path + params
        req = requests.post(url, json=body, headers=headers)
        res = req.json()
        data = {
            "access_token": res["access_token"],
            "refresh_token": res["refresh_token"],
            "sign": sign,
            "timest": timest
        }

        if not account_id:
            raise Exception("missing account_id")
        obj = self.browse(account_id)
        if not obj:
            raise Exception("Lazada Account not found. (%s)" % account_id)

        #initialize
        base_string = ""
        url = self._base_url
        
        # general info
        if not path:
            raise Exception("missing path")
        url += path
        partner_id=int(config.get("lazada_partner_id"))
        if not partner_id:
            raise Exception("partner_id not found in config")
        timest=int(time.time())
        url += "?partner_id=%s&timestamp=%s" %(partner_id, timest)
        base_string = "%s%s%s" % (partner_id,path,timest)

        #optional info
        if require_token:
            token = obj.token
            if not token:
                raise Exception("Token not found. (%s)" % account_id)
            url += "&access_token=%s" % token
            base_string += token
        if require_shop_id:
            shop_id = int(obj.shop_idno)
            if not shop_id:
                raise Exception("Shop ID not found. (%s)" % account_id)
            url += "&shop_id=%s" % shop_id
            base_string += "%s" % shop_id
        #base_string="%s%s%s%s%s"%(partner_id,path,timest,obj.token,shop_id)

        #generate signature
        partner_key=config.get("lazada_partner_key")
        if not partner_key:
            raise Exception("partner_key not found in config")
        sign=hmac.new(partner_key.encode(),base_string.encode(),hashlib.sha256).hexdigest()
        url += "&sign=%s" % sign
        #url=base_url+path+"?partner_id=%s&timestamp=%s&sign=%s&shop_id=%s&access_token=%s"%(partner_id,timest,sign,shop_id,obj.token)
        return url

    def authorize(self,ids,context={}):
        obj=self.browse(ids[0])
        if not obj.shop_idno:
            raise Exception("Shop ID not found. (%s)" % obj.id)
        path="/api/v2/shop/auth_partner"
        id = str(obj['id'])
        db = database.get_connection()
        get_product = get_model("lazada.account").search_browse([["id","=",id]])
        shop_id = get_product[0].shop_idno
        print("getProduct")
        # url = self.generate_url(account_id=obj.id, path=path, require_shop_id=False, require_token=False)
        #
        # # get redirect_url
        # redirect_url=config.get("lazada_redirect_url")
        # db = database.get_active_db()

        redirect_url = "https://auth.lazada.com/oauth/authorize?response_type=code&force_auth=true&redirect_uri=https://backend-prod2-test.netforce.com/lazada_auth?record_id="+id+"&client_id="+shop_id
        url = redirect_url

        return {
            "next": {
                "type": "url",
                "url": url,
            },
        }

    def get_token(self,ids,context={}):
        obj=self.browse(ids[0])
        path="/api/v2/auth/token/get"
        url = self.generate_url(account_id=obj.id, path=path, require_shop_id=False, require_token=False)
        print("url",url)

        # generate body
        partner_id=int(config.get("lazada_partner_id"))
        if not obj.auth_code:
            raise Exception("Missing auth code")
        shop_id=int(obj.shop_idno)
        body={"shop_id":shop_id,"code":obj.auth_code,"partner_id":partner_id}
        headers={"Content-Type":"application/json"}

        # post request and process
        req=requests.post(url,json=body,headers=headers)
        res=req.json()
        print("res",res)
        if res.get("error"):
            raise Exception(res["message"])
        token=res["access_token"]
        refresh_token=res["refresh_token"]
        expiry_time=(datetime.now() + timedelta(seconds=int(res["expire_in"]))).strftime("%Y-%m-%d %H:%M:%S")
        refresh_time=(datetime.now() + timedelta(seconds=int(res["expire_in"])) - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
        obj.write({"token":token,"refresh_token":refresh_token,"token_expiry_time":expiry_time})
        task_ids = get_model("bg.task").search([["model","=","lazada.account"],["method","=","refresh_access_token"],["args","=",'{"ids":[%s]}'%obj.id],["state","=","waiting"],["date",">",datetime.now().strftime("%Y-%m-%d %H:%M:%S")]])
        if task_ids:
            print("task_ids",task_ids)
            get_model("bg.task").delete(task_ids)
        print("creating bg tasks")
        get_model("bg.task").create({
            "date": refresh_time,
            "model": "lazada.account",
            "method": "refresh_access_token",
            "args": '{"ids":[%s]}'%obj.id,
            "state": "waiting",
        })

    def refresh_access_token(self,ids,context={}):
        for obj in self.browse(ids):
            path="/api/v2/auth/access_token/get"
            url = self.generate_url(account_id=obj.id, path=path, require_shop_id=False, require_token=False)
            print("url",url)

            # generate body
            partner_id=int(config.get("lazada_partner_id"))
            if not obj.shop_idno:
                raise Exception("Missing shop ID")
            if not obj.auth_code:
                raise Exception("Missing auth code")
            shop_id=int(obj.shop_idno)
            body={"shop_id":shop_id,"refresh_token":obj.refresh_token,"partner_id":partner_id}

            headers={"Content-Type":"application/json"}
            req=requests.post(url,json=body,headers=headers)
            res=req.json()
            print("res",res)
            if res.get("error"):
                raise Exception(res["message"])
            token=res["access_token"]
            refresh_token=res["refresh_token"]
            expiry_time=(datetime.now() + timedelta(seconds=int(res["expire_in"]))).strftime("%Y-%m-%d %H:%M:%S")
            refresh_time=(datetime.now() + timedelta(seconds=int(res["expire_in"])) - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
            obj.write({"token":token,"refresh_token":refresh_token,"token_expiry_time":expiry_time})
            print("finish_write")
            task_ids = get_model("bg.task").search([["model","=","lazada.account"],["method","=","refresh_access_token"],["args","=",'{"ids":[%s]}'%obj.id],["state","=","waiting"]])
            if task_ids:
                print("task_ids",task_ids)
                get_model("bg.task").delete(task_ids)
            print("creating bg tasks")
            get_model("bg.task").create({
                "date": refresh_time,
                "model": "lazada.account",
                "method": "refresh_access_token",
                "args": '{"ids":[%s]}'%obj.id,
                "state": "waiting",
            })
        return {
            "alert":"Access Tokens Refreshed Successfully"
        }

    def get_info(self,ids,context={}):
        obj=self.browse(ids[0])
        path="/api/v2/shop/get_shop_info"
        url = self.generate_url(account_id=obj.id, path=path)
        print("url",url)
        req=requests.get(url)
        res=req.json()
        print("res",res)
        vals={
            "name": res["shop_name"],
            "region": res["region"],
            "status": res["status"],
        }
        obj.write(vals)

    def upload_categs(self,ids,context={}):
        obj=self.browse(ids[0])
        path="/api/v2/shop_category/add_shop_category"
        url = self.generate_url(account_id=obj.id, path=path)
        print("url",url)
        db=database.get_connection()
        for categ in get_model("product.categ").search_browse([]):
            if categ.lazada_id:
                continue
            data={
                "name": categ.name,
            }
            #data["name"]="OA_V2_1"
            req=requests.post(url,json=data)
            res=req.json()
            if res.get("error"):
                raise Exception("Sync error: %s"%res)
            print("res",res)
            resp=res["response"]
            categ.write({"lazada_id":resp["shop_category_id"]})
            db.commit()

    def upload_image(self,ids,fname,context={}):
        obj=self.browse(ids[0])
        path="/api/v2/media_space/upload_image"
        url = self.generate_url(account_id=obj.id, path=path)
        path=utils.get_file_path(fname)
        print("path",path)
        f=open(path,"rb")
        files={"image":f}
        req=requests.post(url,files=files)
        res=req.json()
        if res.get("error"):
            raise Exception("Sync error: %s"%res)
        resp=res["response"]
        img_id=resp["image_info"]["image_id"]
        return img_id

    def upload_products(self,ids,context={}):
        obj=self.browse(ids[0])
        for prod in get_model("product").search_browse([["sale_channels.id","=",obj.sale_channel_id.id]]):
            #Chin Added for multiple account
            sync_id = None
            for r in prod.sync_records or []:
                if r.account_id.id == obj.id:
                    sync_id = r.sync_id
                    break
            #if prod.sync_records:
            if sync_id:
                obj.update_product_lazada(prod.id,sync_id)
            else:
                obj.add_product_lazada(prod.id)

    def add_product_lazada(self,ids,prod_id,context={}):
        obj=self.browse(ids[0])
        path="/api/v2/product/add_item"
        url = self.generate_url(account_id=obj.id, path=path)
        print("url",url)
        db=database.get_connection()
        prod=get_model("product").browse(prod_id,context={"pricelist_id":obj.pricelist_id.id})
        prod_lazada_details=get_model("product.lazada.details").search_browse([["product_id","=",prod_id],["account_id","=",obj.id]])
        prod2=prod_lazada_details[0] if len(prod_lazada_details) else None
        print("add product %s"%prod.name)
        name = prod2.name if (prod2 and prod2.name) else prod.name
        description = prod2.description if (prod2 and prod2.description) else prod.description
        if not prod.customer_price:
            raise Exception("Missing sales price for product %s"%prod.code)
        categ=prod2.categ_id if (prod2 and prod2.categ_id) else prod.categ_id
        if not categ:
            raise Exception("Missing category for product %s"%prod.code)
        if not prod.image:
            raise Exception("Missing image for product %s"%prod.code)
        img_id=obj.upload_image(prod.image)
        img_ids=[img_id]
        if not categ.sync_id:
            raise Exception("Missing category sync ID")
        if not prod.ship_methods:
            raise Exception("Missing shipping methods for product %s"%prod.code)
        brand=prod2.brand_id if (prod2 and prod2.brand_id) else prod.brand_id
        if not brand:
            raise Exception("Missing brand")
        if not brand.sync_id:
            raise Exception("Missing brand sync ID")
        ship_methods = prod2.ship_methods if (prod2 and prod2.ship_methods and len(prod2.ship_methods)) else prod.ship_methods
        if not prod.weight:
            raise Exception("Missing weight")
        if not prod.height:
            raise Exception("Missing height")
        if not prod.length:
            raise Exception("Missing length")
        if not prod.width:
            raise Exception("Missing width")
        data={
            "original_price": float(prod.customer_price),
            "description": description or "/",
            "item_name": name,
            "normal_stock": int(prod.stock_qty),
            "weight": float(prod.weight),
            "logistic_info": [],
            "category_id": int(categ.sync_id),
            "image": {
                "image_id_list": img_ids,
            },
            "logistic_info": [{
                "logistic_id": int(m.sync_id),
                "enabled": True,
            } for m in ship_methods if m.sync_id],
            "dimension": {
                "package_height": int(prod.height),
                "package_length": int(prod.length),
                "package_width": int(prod.width),
            },
            "pre_order": {
                "is_pre_order": False,
            },
            "brand": {
                "brand_id": int(brand.sync_id),
                "original_brand_name": brand.name,
            },
        }
        print("data",data)
        req=requests.post(url,json=data)
        res=req.json()
        if res.get("error"):
            raise Exception("Sync error: %s"%res)
        resp=res["response"]
        sync_id=resp["item_id"]
        vals={
            "sync_id": sync_id,
            "account_id": "lazada.account,%s"%obj.id,
            "related_id": "product,%s"%prod.id,
        }
        get_model("sync.record").create(vals)
        db.commit()

    def update_product_lazada(self,ids,prod_id,sync_id,context={}):
        obj=self.browse(ids[0])
        path="/api/v2/product/update_item"
        url = self.generate_url(account_id=obj.id, path=path)
        print("url",url)
        db=database.get_connection()
        prod=get_model("product").browse(prod_id,context={"pricelist_id":obj.pricelist_id.id})
        #sync_id=int(prod.sync_records[0].sync_id)
        print("update product %s"%prod.name)
        if not prod.customer_price:
            raise Exception("Missing sales price for product %s"%prod.code)
        categ=prod.categ_id
        if not categ:
            raise Exception("Missing category for product %s"%prod.code)
        if not prod.image:
            raise Exception("Missing image for product %s"%prod.code)
        img_id=obj.upload_image(prod.image)
        img_ids=[img_id]
        if not categ.sync_id:
            raise Exception("Missing category sync ID")
        if not prod.ship_methods:
            raise Exception("Missing shipping methods for product %s"%prod.code)
        brand=prod.brand_id
        if not brand:
            raise Exception("Missing brand")
        if not brand.sync_id:
            raise Exception("Missing brand sync ID")
        if not prod.weight:
            raise Exception("Missing weight")
        if not prod.height:
            raise Exception("Missing height")
        if not prod.length:
            raise Exception("Missing length")
        if not prod.width:
            raise Exception("Missing width")
        data={
            "item_id": sync_id,
            "original_price": float(prod.customer_price),
            "description": prod.description or "/",
            "item_name": prod.name,
            "normal_stock": int(prod.stock_qty),
            "weight": float(prod.weight),
            "logistic_info": [],
            "category_id": int(categ.sync_id),
            "image": {
                "image_id_list": img_ids,
            },
            "logistic_info": [{
                "logistic_id": int(m.sync_id),
                "enabled": True,
            } for m in prod.ship_methods if m.sync_id],
            "dimension": {
                "package_height": int(prod.height),
                "package_length": int(prod.length),
                "package_width": int(prod.width),
            },
            "pre_order": {
                "is_pre_order": False,
            },
            "brand": {
                "brand_id": int(brand.sync_id),
                "original_brand_name": brand.name,
            },
        }
        print("data",data)
        req=requests.post(url,json=data)
        res=req.json()
        if res.get("error"):
            raise Exception("Sync error: %s"%res)
        resp=res["response"]
        db.commit()

    def get_products(self,ids,context={}):
        print("get products>>>>>>>>>>>>>>>>>>>>>>>")
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

        account = get_model("lazada.account").search_browse([["id", "=", ids[0]]])
        shop_id = account[0].shop_idno
        app_secret = account[0].auth_code
        app_key = shop_id
        app_secret = app_secret
        headers = {"Content-Type": "application/json"}
        sign_method = "sha256"
        timest = int(time.time() * 1000)
        base_url = "https://api.lazada.com.my/rest"
        path = "/products/get"
        total = 0
        job_id = ids[0]
        if job_id:
            if tasks.is_aborted(job_id):
                return
            tasks.set_progress(job_id, 10, "Step 1: Reading Products from Lazada: %s found." % (total))
        access_token = account[0].token
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
        # print("response is", res)
        db = database.get_connection()
        get_product = get_model("lazada.product")
        # print("get_prodcut", get_product)
        total = len(res['data']['products'])
        print("total", total)
        if job_id:
            if tasks.is_aborted(job_id):
                return
            tasks.set_progress(job_id, 50, "Step 1: Reading Products from Lazada: %s found." % (total))

        for product in res['data']['products']:
            if not get_model("lazada.product").search_browse(["sync_id", "=", str(product["item_id"])]):
                save_product = get_product.create({
                    "account_id": ids[0],
                    "sync_id": product["item_id"],
                    "item_name": product['attributes']['name'],
                    "description": product['attributes']['description'],
                    "lazada_create_time": datetime.datetime.fromtimestamp(int(product['created_time']) / 1000).strftime(
                        '%Y-%m-%d %H:%M:%S'),
                    "lazada_update_time": datetime.datetime.fromtimestamp(int(product['updated_time']) / 1000).strftime(
                        '%Y-%m-%d %H:%M:%S'),
                    "images": product["images"],
                    "item_sku": product["skus"][0]['SellerSku'],
                    "trialProduct": product['trialProduct'],
                    "primary_category": product['primary_category'],
                    "marketImages": product["marketImages"],
                    "attributes": str(product['attributes']),
                    "item_status": product['status'],
                    "current_price": product["skus"][0]['price'],
                    "normal_stock": product["skus"][0]['quantity']
                })
                ##Create System product
                if not get_model("product").search_browse(["code", "=", str(product["item_id"])]):
                    print("2222")
                    get_system_product = get_model("product")
                    save_system_product = get_system_product.create({
                        "name": product['attributes']['name'],
                        "code": product["item_id"],
                        "type": "stock",
                        "uom_id": 1,
                    })
                    _get_product = get_model("lazada.product").browse(save_product)
                    _get_product.write({
                        "product_id": save_system_product
                    })
                else:
                    get_system_product = get_model("product").search_browse(["code", "=", str(product["item_id"])])
                    _get_product = get_model("lazada.product").browse(save_product)
                    _get_product.write({
                        "product_id": get_system_product.id
                    })
                ##Create Order Item
                # headers = {"Content-Type": "application/json"}
                # sign_method = "sha256"
                # timest = int(time.time() * 1000)
                # base_url = "https://api.lazada.com.my/rest"
                # path = "/product/item/get"
                # access_token = account[0].token
                # params = {
                #     "access_token": access_token,
                #     "app_key": app_key,
                #     "sign_method": sign_method,
                #     "timestamp": timest,
                #     "item_id": product['item_id'],
                #     "seller_sku": product["skus"][0]['SellerSku']
                # }
                # signature = sign(app_secret, path, params)
                # _params = "?app_key=%s&access_token=%s&timestamp=%s&sign_method=%s&sign=%s&item_id=%s&seller_sku=%s" % (
                #     app_key, access_token, timest, sign_method, signature, product['item_id'],
                #     product["skus"][0]['SellerSku'])
                # url = base_url + path + _params
                # req = requests.get(url, headers=headers)
                # res = req.json()
                # get_order_item = get_model("lazada.product.model")
                # try:
                #     name = res['data']['attributes']['name']
                # except:
                #     name = None
                # try:
                #     created_at = (time.ctime(int(res['data']['created_time'])))[:-6]
                # except:
                #     created_at = None
                # try:
                #     updated_at = (time.ctime(int(res['data']['updated_time'])))[:-6]
                # except:
                #     updated_at = None
                # try:
                #     status = res['data']['status']
                # except:
                #     status = None
                # try:
                #     total_quantity = res['data']['skus'][0]['quantity']
                # except:
                #     total_quantity = None
                # try:
                #     available_quantity = res['data']['skus'][0]['Available']
                # except:
                #     available_quantity = None
                # try:
                #     seller_sku = res['data']['skus'][0]['SellerSku']
                # except:
                #     seller_sku = None
                # try:
                #     shop_sku = res['data']['skus'][0]['ShopSku']
                # except:
                #     shop_sku = None
                # try:
                #     item_skuID = res['data']['skus'][0]['SkuId']
                # except:
                #     item_skuID = None
                # try:
                #     package_width = res['data']['skus'][0]['package_width']
                # except:
                #     package_width = None
                # try:
                #     package_height = res['data']['skus'][0]['package_height']
                # except:
                #     package_height = None
                # try:
                #     package_length = res['data']['skus'][0]['package_length']
                # except:
                #     package_length = None
                # try:
                #     package_weight = res['data']['skus'][0]['package_weight']
                # except:
                #     package_weight = None
                # try:
                #     current_price = res['data']['skus'][0]['price']
                # except:
                #     current_price = None
                # try:
                #     item_id = res['data']['item_id']
                # except:
                #     item_id = None
                # try:
                #     variation = str(res['data']['variation'])
                # except:
                #     variation = None
                # try:
                #     brand = res['data']['attributes']['brand']
                # except:
                #     brand = None
                #
                # try:
                #     warranty_type = res['data']['attributes']['warranty_type']
                # except:
                #     warranty_type = None
                # get_order_item.create({
                #     "name": name,
                #     "lazada_product_id": save_product,
                #     "created_at": created_at,
                #     "updated_at": updated_at,
                #     "status": status,
                #     "total_quantity": total_quantity,
                #     "available_quantity": available_quantity,
                #     "seller_sku": seller_sku,
                #     "shop_sku": shop_sku,
                #     "item_skuID": item_skuID,
                #     "model_sku": item_skuID,
                #     "package_width": package_width,
                #     "package_height": package_height,
                #     "package_length": package_length,
                #     "package_weight": package_weight,
                #     "item_id": item_id,
                #     "current_price": current_price,
                #     "variation": variation,
                #     "brand": brand,
                #     "warranty_type": warranty_type
                # })
                # _get_product = get_model("lazada.product").browse(save_product)
                # _get_product.write({
                #     "has_model": True
                # })
                # db.commit()
        tasks.set_progress(job_id, 100,
                           "Step 2: Writing of %s Products to Database" % (total))
        # print("response", res)

    def get_products_info(self, account_id, item_ids, context={}):
        if len(item_ids) > 50:
            self.get_products_info(account_id, item_ids[0:50], context=context)
            self.get_products_info(account_id, item_ids[50:],context=context)
        settings = get_model("lazada.settings").browse(1)
        if not settings:
            raise Exception("Lazada Settings not found")
        path="/api/v2/product/get_item_base_info"
        url = self.generate_url(account_id=account_id,path=path)
        url += "&item_id_list=%s" % ",".join([str(k) for k in item_ids])
        print("url",url)
        req = requests.get(url)
        res = req.json()
        if res.get("error"):
            raise Exception("Sync error: %s"%res)
        resp = res["response"]
        print("resp",resp)
        for item in resp["item_list"]:
            vals = {
                "account_id": account_id,
                "item_name": item["item_name"],
                "item_sku": item["item_sku"],
                "sync_id": item["item_id"],
                "description": item["description"],
                "condition": item["condition"],
                "item_status": item["item_status"],
                "has_model": item["has_model"],
            }
            vals["lazada_create_time"] = datetime.fromtimestamp(item["create_time"]).strftime("%Y-%m-%d %H:%M:%S")
            vals["lazada_update_time"] = datetime.fromtimestamp(item["update_time"]).strftime("%Y-%m-%d %H:%M:%S")
            if not item["has_model"]:
                if item.get("stock_info"):
                    for si in item["stock_info"]:
                        if si["stock_type"] == 2:
                            vals["normal_stock"] = si["normal_stock"]
                if item.get("price_info"):
                    vals["current_price"] = item["price_info"][0]["current_price"]

            if item["category_id"]:
                categs = get_model("lazada.product.categ").search([["sync_id","=",str(item["category_id"])]])
                vals["category_id"] = categs[0] if categs else None
            prods = get_model("lazada.product").search([["account_id","=",str(account_id)],["sync_id","=",str(item["item_id"])]])
            if not prods:
                prod_id = get_model("lazada.product").create(vals)
            else:
                prod_id = prods[0]
                get_model("lazada.product").write([prod_id],vals)
            prod = get_model("lazada.product").browse(prod_id)
            if item["has_model"]:
                prod.get_model_list()
            prod.map_product()
    
    def get_products_info_old(self, account_id, item_ids, context={}):
        if len(item_ids) > 50:
            self.get_products_info(item_ids[0:50])
            self.get_products_info(item_ids[50:])
        settings = get_model("lazada.settings").browse(1)
        if not settings:
            raise Exception("Lazada Settings not found")
        path="/api/v2/product/get_item_base_info"
        url = self.generate_url(account_id=account_id,path=path)
        url += "&item_id_list=%s" % ",".join([str(k) for k in item_ids])
        print("url",url)
        req = requests.get(url)
        res = req.json()
        if res.get("error"):
            raise Exception("Sync error: %s"%res)
        resp = res["response"]
        print("resp",resp)
        for item in resp["item_list"]:
            vals = get_model("product").default_get()
            if vals.get("company_id"):
                vals["company_id"] = vals["company_id"][0]
            if not vals.get("type"):
                vals["type"] = "stock"
            if settings.default_uom_id:
                vals["uom_id"] = settings.default_uom_id.id
            #vals={}
            if item["item_sku"]:
                vals["code"] = item["item_sku"]
            vals["name"] = item["item_name"]
            if item["category_id"]:
                categs = get_model("product.categ").search([["sync_id","=",item["category_id"]]])
                vals["categ_id"] = categs[0] if categs else None
            vals["description"] = item["description"]
            vals["weight"] = item["weight"]
            # Add iamage here XXX
            if item["brand"]:
                brands= get_model("product.brand").search([["sync_id","=",item["brand"]["brand_id"]]])
                vals["brand_id"] = brands[0] if brands else None
            if item["logistic_info"]:
                logistic_ids = [l["logistic_id"] for l in item["logistic_info"] if l.get("enabled") and l["enabled"]==True]
                method_ids = []
                for lid in logistic_ids:
                    methods = get_model("ship.method").search([["sync_id","=",lid]])
                    if methods:
                        method_ids.append(methods[0])
                vals["ship_methods"] = [["set",method_ids]]
            vals["sync_records"]= [("create",{
                "sync_id": item["item_id"],
                "account_id": "lazada.account,%s"%account_id,
                })]
            prod_sync = get_model("sync.record").search_browse([
                ["account_id","=","lazada.account,%s"%account_id],
                ["related_id","like","product"],
                ["sync_id","=",str(item["item_id"])
                ]])
            prod = None
            if prod_sync:
                prod = prod_sync[0].related_id
                print("prod_sync found: %s"%prod)
            elif item["item_sku"]:
                prods = get_model("product").search_browse([["code","=",item["item_sku"]]])
                prod = prods[0] if prods else None
                print("prod with code found: %s"%prod)
            if prod:
                prod.write(vals)
            else:
                get_model("product").create(vals)

    def get_logis(self,ids,context={}):
        obj=self.browse(ids[0])
        path="/api/v2/logistics/get_channel_list"
        url = self.generate_url(account_id=obj.id, path=path)
        print("url",url)
        #data["name"]="OA_V2_1"
        req=requests.get(url)
        res=req.json()
        if res.get("error"):
            raise Exception("Sync error: %s"%res)
        print("res",res)
        resp=res["response"]
        for r in resp["logistics_channel_list"]:
            method_name = "Lazada - "+r["logistics_channel_name"]
            methods = get_model("ship.method").search_browse([["name","=",method_name]])
            if len(methods) == 0:
                vals={
                    #"name": "Lazada - "+r["logistics_channel_name"],
                    "name": method_name,
                    "sync_records": [("create",{
                        "sync_id": r["logistics_channel_id"],
                        "account_id": "lazada.account,%s"%obj.id,
                    })],
                }
                get_model("ship.method").create(vals)
            else:
                method = methods[0]
                
    def get_categ(self,ids,context={}):
        for acc_id in ids:
            context["account_id"] = acc_id
            get_model("lazada.product.categ").get_categ(context=context)

    def get_shop_categ(self,ids,context={}):
        obj=self.browse(ids[0])
        path="/api/v2/shop_category/get_shop_category_list"
        url = self.generate_url(account_id=obj.id, path=path)
        url+="&page_size=20"
        url+="&page_no=1"
        print("url",url)
        #data["name"]="OA_V2_1"
        req=requests.get(url)
        res=req.json()
        if res.get("error"):
            raise Exception("Sync error: %s"%res)
        print("res",res)
        resp=res["response"]
        db=database.get_connection()
        for r in resp["shop_categorys"]:
            vals={
                "name": "Lazada Shop Categ - "+r["name"],
                "sync_records": [("create",{
                    "sync_id": r["shop_category_id"],
                    "account_id": "lazada.account,%s"%obj.id,
                })],
            }
            print("vals",vals)
            get_model("product.categ").create(vals)
            db.commit()

    def get_brands(self,ids,context={}):
        obj=self.browse(ids[0])
        categ_sync=get_model("sync.record").search_browse([["account_id","=","lazada.account,%s"%obj.id],["related_id","like","product.categ"]])
        job_id = context.get("job_id")
        i=0
        for c in categ_sync:
            if job_id:
                if tasks.is_aborted(job_id):
                    return
                tasks.set_progress(job_id,i/len(categ_sync)*100,"Getting brands for %s of %s Product Categories."%(i+1,len(categ_sync)))
            i += 1
            categ = c.related_id
            print("inspect categ ==>")
            print(categ)
            categ.get_lazada_brands(acc_id=obj.id,context={"skip_error":True})

    def get_orders(self,ids,context={}):
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
        db = database.get_connection()
        account = get_model("lazada.account").search_browse([["id", "=", ids[0]]])
        shop_id = account[0].shop_idno
        app_secret = account[0].auth_code
        app_key = shop_id
        app_secret = app_secret
        headers = {"Content-Type": "application/json"}
        sign_method = "sha256"
        timest = int(time.time() * 1000)
        createdafter = '2022-11-10T09:00:00'
        base_url = "https://api.lazada.com.my/rest"
        path = "/orders/get"
        access_token = account[0].token
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
        save_order_id_list = []
        for order in res['data']['orders']:
                    try:
                        # print("1")
                        if not get_model("lazada.order").search_browse(["order_sn", "=", str(order['order_id'])]):
                            print("print 2")
                            get_order = get_model("lazada.order")
                            order_save = get_order.create({
                                "account_id": ids[0],
                                "sync_id" : order['order_id'],
                                "order_sn" : order['order_id'],
                                "order_status" : (order['statuses'][0]).title(),
                                "created_at" : order['created_at'],
                                "updated_at" : order['updated_at'],
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
                                "recipient_address_full_address" : order['address_shipping']['address1'],
                                "order_create_time" : order['created_at'],
                                "qty" : order['items_count']
                            })
                            save_order_id_list.append(order_save)

                            ##Order Item
                            headers = {"Content-Type": "application/json"}
                            sign_method = "sha256"
                            timest = int(time.time() * 1000)
                            base_url = "https://api.lazada.com.my/rest"
                            path = "/order/items/get"
                            access_token = account[0].token
                            params = {
                                "access_token": access_token,
                                "app_key": app_key,
                                "sign_method": sign_method,
                                "timestamp": timest,
                                "order_id": order['order_id']
                            }
                            signature = sign(app_secret, path, params)
                            _params = "?app_key=%s&access_token=%s&timestamp=%s&sign_method=%s&sign=%s&order_id=%s" % (
                                app_key, access_token, timest, sign_method, signature, order['order_id'])
                            url = base_url + path + _params
                            req = requests.get(url, headers=headers)
                            res = req.json()
                            print("save order id",order_save)
                            for item in res['data']:
                                if not get_model("lazada.order.item").search_browse(["item_id", "=", str(item['order_item_id'])]):
                                    print("print 3",item)
                                    get_order_item = get_model("lazada.order.item")
                                    get_order_item.create({
                                    "item_id": item['product_id'],
                                    "order_id": order_save,
                                    "item_name": item['name'],
                                    "item_sku": item['sku'],
                                    "order_flag": item['order_flag'],
                                    "tax_amount": item['tax_amount'],
                                    "variation": item['variation'],
                                    "product_id": item['product_id'],
                                    "shop_id": item['shop_id'],
                                    "invoice_number": item['invoice_number'],
                                    "product_detail_url": item['product_detail_url'],
                                    "shipping_type": item['shipping_type'],
                                    "shipping_provider_type": item['shipping_provider_type'],
                                    "item_price": item['item_price'],
                                    "shipping_service_cost": item['shipping_service_cost'],
                                    "tracking_code": item['tracking_code'],
                                    "shipping_amount": item['shipping_amount'],
                                    "shipment_provider": item['shipment_provider'],
                                    "voucher_amount": item['voucher_amount'],
                                    "digital_delivery_info": item['digital_delivery_info'],
                                    "extra_attributes": item['extra_attributes']
                                    })
                                get_order = get_model("lazada.order").browse(order_save)
                                try:
                                    pick_up_address = item['pick_up_store_info']['pick_up_store_address']
                                except:
                                    pick_up_address = None
                                get_order.write({
                                    "shipping_carrier": item['shipment_provider'],
                                    "actual_shipping_fee": item['shipping_amount'],
                                    "buyer_user_id": item['buyer_id'],
                                    "pickup_info": pick_up_address,
                                    "invoice_data_number": item['invoice_number']

                                })
                                print("print 4")
                        # db.commit()

                    except Exception as e:
                        print("Exception is", e)
        get_model("lazada.order").function_store(save_order_id_list)
        redirect_url2 = "http://newfront-dev.smartb.co"
        url = redirect_url2 + "/action?name=lazada_order"

        return {
            "next": {
                "type": "url",
                "url": url,
            },
        }

    def get_order(self,ids,order_no,context={}):

        def signtwo(secret, api, parameters):
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

        app_key = "111456"
        app_secret = "Xp5vDjQwAiLQzclVQWddVX3RXq7wh0Xf"

        headers = {"Content-Type": "application/json"}

        sign_method = "sha256"
        timest = int(time.time() * 1000)
        base_url = "https://api.lazada.com.my/rest"
        path = "/order/get"
        # access_token = signature['access_token']
        account_id = ids[0][0]
        db = database.get_connection()
        get_account = get_model("lazada.account").browse(account_id)
        print("access_token", get_account.token)
        access_token = get_account.token
        params = {
            "app_key": app_key,
            "access_token": access_token,
            "sign_method": sign_method,
            "timestamp": timest
        }
        signature = signtwo(app_secret, path, params)

        params = "?app_key=%s&access_token=%s&timestamp=%s&sign_method=%s&sign=%s" % (
            app_key, access_token, timest, sign_method, signature)
        url = base_url + path + params
        req = requests.get(url, headers=headers)
        res = req.json()

















        print("get_order",order_no)
        obj=self.browse(ids[0])
        path="/api/v2/order/get_order_detail"
        url = self.generate_url(account_id=obj.id, path=path)
        url+="&order_sn_list=%s"%order_no
        #url+="&response_optional_fields=buyer_username,buyer_user_id,item_list,recipient_address,create_time.ship_by_date,note"
        url+="&response_optional_fields=buyer_user_id,buyer_username,estimated_shipping_fee,recipient_address,actual_shipping_fee ,goods_to_declare,note,note_update_time,item_list,pay_time,dropshipper,dropshipper_phone,split_up,buyer_cancel_reason,cancel_by,cancel_reason,actual_shipping_fee_confirmed,buyer_cpf_id,fulfillment_flag,pickup_done_time,package_list,shipping_carrier,payment_method,total_amount,buyer_username,invoice_data, checkout_shipping_carrier, reverse_shipping_fee"
        print("url",url)
        #data["name"]="OA_V2_1"
        req=requests.get(url)
        res=req.json()
        if res.get("error"):
            raise Exception("Sync error: %s"%res)
        print("res",res)
        resp=res["response"]
        settings = get_model("lazada.settings").browse(1)
        for o in resp["order_list"]:
            orders = get_model("lazada.order").search_browse([["order_sn","=",str(o["order_sn"])]])
            if not orders:
                order_id=get_model("lazada.order").create_order(obj.id,o,context)
            else:
                order_id=orders[0].id
                orders[0].update_order(obj.id,o,context)
            #res=get_model("sale.order").search([["sync_records.sync_id","=",str(o["order_sn"])]])
            #order_id=res[0] if res else None
            #order_id=None
            #cont_id=None
            #sale_id=None
            #if lazada_settings.include_contact:
            #    cont_id = get_model("contact").get_lazada_contact(obj.id,o,context)
            #    context["cont_id"] = cont_id
            #if lazada_settings.include_sale:
            #    sale_id = get_model("sale.order").get_lazada_order(obj.id,o,context)
            #    context["sale_id"] = sale_id
            #if lazada_settings.include_inventory:
            #    pick_id = get_model("stock.picking").get_lazada_order(obj.id,o,context)
        return order_id

    def sign(self ,app_key, app_secret, code, base_url, path):
        timest = int(time.time() * 1000)
        app_key = app_key
        app_secret = app_secret
        code = code
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
        data = {
            "access_token": res["access_token"],
            "refresh_token": res["refresh_token"],
            "sign": sign
        }
        return data

    def get_payments(self,ids,context={}):
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

        account = get_model("lazada.account").search_browse([["id", "=", ids[0]]])
        contact = account[0].contact_id
        if not contact:
            raise Exception("Please choose default contact in Lazada account")
        shop_id = account[0].shop_idno
        app_secret = account[0].auth_code
        app_key = shop_id
        app_secret = app_secret
        headers = {"Content-Type": "application/json"}
        sign_method = "sha256"
        timest = int(time.time() * 1000)
        createdafter = '2017-02-10T09:00:00'
        base_url = "https://api.lazada.com.my/rest"
        path = "/finance/transaction/details/get"
        account_id = ids[0]
        db = database.get_connection()
        get_account = get_model("lazada.account").browse(account_id)
        print("access_token", get_account.token)
        access_token = get_account.token
        start_time = "2022-07-01"
        end_time = "2022-10-31"
        params = {
            "access_token": access_token,
            "app_key": app_key,
            "sign_method": sign_method,
            "timestamp": timest,
            "start_time": start_time,
            "end_time": end_time
        }
        signature = sign(app_secret, path, params)
        _params = "?app_key=%s&start_time=%s&end_time=%s&access_token=%s&timestamp=%s&sign_method=%s&sign=%s" % (
            app_key, start_time, end_time, access_token, timest, sign_method, signature)
        url = base_url + path + _params
        req = requests.get(url, headers=headers)
        res = req.json()
        print("print 1")
        # raise Exception(res['data'][0])
        db = database.get_connection()
        # get_order = get_model("account.payment")
        for payment in res['data']:
            if not get_model("account.payment").search_browse(
                    ["transaction_no", "=", str(payment['transaction_number'])]):
                try:
                    print("paymenttttt", payment)
                    if payment['paid_status'] == "paid":
                        type = "out"
                    else:
                        type = "in"
                    vals = {
                        "date": payment['transaction_date'],
                        "amount_subtotal": float((payment['amount']).replace(',', '')),
                        "amount_total": float((payment['amount']).replace(',', '')),
                        "amount_payment": float((payment['amount']).replace(',', '')),
                        "ref": payment['reference'],
                        "type": "in",
                        "transaction_no": payment['transaction_number'],
                        "number": "ZRV-"+str(payment['orderItem_no']),
                        "state": 'posted',
                        "memo": "Lazada",
                        "pay_type":"invoice",
                        "contact_id": contact.id,
                        "account_id": account[0].ewallet_account_id.id
                    }
                    print("print 2", payment['order_no'])
                    pmt_id = get_model("account.payment").create(vals)
                    payment_vals = {
                        "payment_id": pmt_id,
                        "amount": float((payment['amount']).replace(',', '')),
                        "description": payment['details'],
                        "type": "Overpayment",
                        "account_id": account[0].ewallet_account_id.id,
                        "track_id": account[0].track_id.id,
                        "invoice_currency_id": 2,
                        "amount_invoice":float((payment['amount']).replace(',', '')),
                        "invoice_iddd":1

                    }
                    payment_line = get_model("account.payment.line").create(payment_vals)
                except Exception as e:
                    print("Exception is", e)
                # payment line

        db.commit()
        redirect_url2 = "http://newfront-dev.smartb.co"
        url = redirect_url2 + "/action?name=payment"

        return {
            "next": {
                "type": "url",
                "url": url,
            },
        }

    def get_products_categories(self, ids, context={}):

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


        account = get_model("lazada.account").search_browse([["id", "=", ids[0]]])
        shop_id = account[0].shop_idno
        app_secret = account[0].auth_code
        app_key = shop_id
        app_secret = app_secret
        headers = {"Content-Type": "application/json"}
        sign_method = "sha256"
        timest = int(time.time() * 1000)
        base_url = "https://api.lazada.com.my/rest"
        path = "/category/tree/get"
        access_token = account[0].token
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
        # raise Exception(res)
        # print("response is", res)
        db = database.get_connection()
        get_product_categ = get_model("lazada.product.categ")
        for product in res['data']:
            if not get_model("lazada.product.categ").search_browse(["sync_id", "=", str(product["category_id"])]):
                save_product_categ = get_product_categ.create({
                    "sync_id": product["category_id"],
                    "original_category_name": product['name'],
                    "display_category_name": product['name']
                })
                print("2222")
                db.commit()

    # def start_job(self,method,args=[],opts={},context={}):
    #     def sign(secret, api, parameters):
    #         # ===========================================================================
    #         # @param secret
    #         # @param parameters
    #         # ===========================================================================
    #         sort_dict = sorted(parameters)
    #
    #         parameters_str = "%s%s" % (api,
    #                                    str().join('%s%s' % (key, parameters[key]) for key in sort_dict))
    #
    #         h = hmac.new(secret.encode(encoding="utf-8"), parameters_str.encode(encoding="utf-8"),
    #                      digestmod=hashlib.sha256)
    #
    #         return h.hexdigest().upper()
    #
    #     if method == "get_orders":
    #         db = database.get_connection()
    #         account = get_model("lazada.account").search_browse([["id", "=", args[0][0]]])
    #         shop_id = account[0].shop_idno
    #         app_secret = account[0].auth_code
    #         app_key = shop_id
    #         app_secret = app_secret
    #         headers = {"Content-Type": "application/json"}
    #         sign_method = "sha256"
    #         timest = int(time.time() * 1000)
    #         createdafter = '2022-11-10T09:00:00'
    #         base_url = "https://api.lazada.com.my/rest"
    #         path = "/orders/get"
    #         access_token = account[0].token
    #         params = {
    #             "access_token": access_token,
    #             "app_key": app_key,
    #             "sign_method": sign_method,
    #             "timestamp": timest,
    #             "created_after": createdafter
    #         }
    #         signature = sign(app_secret, path, params)
    #         _params = "?app_key=%s&created_after=%s&access_token=%s&timestamp=%s&sign_method=%s&sign=%s" % (
    #             app_key,createdafter, access_token,timest, sign_method, signature)
    #         url = base_url + path + _params
    #         req = requests.get(url, headers=headers)
    #         res = req.json()
    #         # print("print 1", res['data']['orders'][0]['order_id'])
    #         # testing = get_model("lazada.order").search_browse(["sync_id", "=", str(res['data']['orders'][0]['order_id'])])
    #         # raise Exception(testing[0].id)
    #         for order in res['data']['orders']:
    #             try:
    #                 # print("1")
    #                 if not get_model("lazada.order").search_browse(["order_sn", "=", str(order['order_id'])]):
    #                     print("print 2")
    #                     get_order = get_model("lazada.order")
    #                     order_save = get_order.create({
    #                         "account_id": args[0][0],
    #                         "sync_id" : order['order_id'],
    #                         "order_sn" : order['order_id'],
    #                         "order_status" : (order['statuses'][0]).title(),
    #                         "created_at" : order['created_at'],
    #                         "updated_at" : order['updated_at'],
    #                         "region" : order['address_shipping']['country'],
    #                         "currency" : "Malaysian ringgit",
    #                         "total_amount" : order['price'],
    #                         "payment_method" : order['payment_method'],
    #                         "estimated_shipping_fee" : order['shipping_fee'],
    #                         "message_to_seller" : order['remarks'],
    #                         "buyer_username" : order['customer_first_name'],
    #                         "recipient_address_name" : order['address_shipping']['first_name'],
    #                         "recipient_address_phone" : order['address_shipping']['phone'],
    #                         "recipient_address_city" : order['address_shipping']['city'],
    #                         "recipient_address_region" : order['address_shipping']['country'],
    #                         "recipient_address_zipcode" : order['address_shipping']['post_code'],
    #                         "recipient_address_full_address" : order['address_shipping']['address1'],
    #                         "order_create_time" : order['created_at'],
    #                         "qty" : order['items_count']
    #                     })
    #
    #                     ##Order Item
    #                     headers = {"Content-Type": "application/json"}
    #                     sign_method = "sha256"
    #                     timest = int(time.time() * 1000)
    #                     base_url = "https://api.lazada.com.my/rest"
    #                     path = "/order/items/get"
    #                     access_token = account[0].token
    #                     params = {
    #                         "access_token": access_token,
    #                         "app_key": app_key,
    #                         "sign_method": sign_method,
    #                         "timestamp": timest,
    #                         "order_id": order['order_id']
    #                     }
    #                     signature = sign(app_secret, path, params)
    #                     _params = "?app_key=%s&access_token=%s&timestamp=%s&sign_method=%s&sign=%s&order_id=%s" % (
    #                         app_key, access_token, timest, sign_method, signature, order['order_id'])
    #                     url = base_url + path + _params
    #                     req = requests.get(url, headers=headers)
    #                     res = req.json()
    #                     print("save order id",order_save)
    #                     for item in res['data']:
    #                         if not get_model("lazada.order.item").search_browse(["item_id", "=", str(item['order_item_id'])]):
    #                             print("print 3")
    #                             get_order_item = get_model("lazada.order.item")
    #                             get_order_item.create({
    #                             "item_id": item['order_item_id'],
    #                             "order_id": order_save,
    #                             "item_name": item['name'],
    #                             "item_sku": item['sku'],
    #                             "order_flag": item['order_flag'],
    #                             "tax_amount": item['tax_amount'],
    #                             "variation": item['variation'],
    #                             "product_id": item['product_id'],
    #                             "shop_id": item['shop_id'],
    #                             "invoice_number": item['invoice_number'],
    #                             "product_detail_url": item['product_detail_url'],
    #                             "shipping_type": item['shipping_type'],
    #                             "shipping_provider_type": item['shipping_provider_type'],
    #                             "item_price": item['item_price'],
    #                             "shipping_service_cost": item['shipping_service_cost'],
    #                             "tracking_code": item['tracking_code'],
    #                             "shipping_amount": item['shipping_amount'],
    #                             "shipment_provider": item['shipment_provider'],
    #                             "voucher_amount": item['voucher_amount'],
    #                             "digital_delivery_info": item['digital_delivery_info'],
    #                             "extra_attributes": item['extra_attributes']
    #                             })
    #                         get_order = get_model("lazada.order").browse(order_save)
    #                         try:
    #                             pick_up_address = item['pick_up_store_info']['pick_up_store_address']
    #                         except:
    #                             pick_up_address = None
    #                         get_order.write({
    #                             "shipping_carrier": item['shipment_provider'],
    #                             "actual_shipping_fee": item['shipping_amount'],
    #                             "buyer_user_id": item['buyer_id'],
    #                             "pickup_info": pick_up_address,
    #                             "invoice_data_number": item['invoice_number']
    #
    #                         })
    #                         print("print 4")
    #                 # db.commit()
    #
    #             except Exception as e:
    #                 print("Exception is", e)
    #     if method == "copy_to_picking_skip_error":
    #         print("copy to picking skip error")
    #     if method == "get_payments":
    #         # db = database.get_connection()
    #         account = get_model("lazada.account").search_browse([["id", "=", args[0][0]]])
    #         shop_id = account[0].shop_idno
    #         app_secret = account[0].auth_code
    #         app_key = shop_id
    #         app_secret = app_secret
    #         headers = {"Content-Type": "application/json"}
    #         sign_method = "sha256"
    #         timest = int(time.time() * 1000)
    #         createdafter = '2017-02-10T09:00:00'
    #         base_url = "https://api.lazada.com.my/rest"
    #         path = "/finance/transaction/details/get"
    #         account_id = args[0][0]
    #         db = database.get_connection()
    #         get_account = get_model("lazada.account").browse(account_id)
    #         print("access_token", get_account.token)
    #         access_token = get_account.token
    #         start_time = "2022-07-01"
    #         end_time = "2022-10-31"
    #         params = {
    #             "access_token": access_token,
    #             "app_key": app_key,
    #             "sign_method": sign_method,
    #             "timestamp": timest,
    #             "start_time": start_time,
    #             "end_time": end_time
    #         }
    #         signature = sign(app_secret, path, params)
    #         _params = "?app_key=%s&start_time=%s&end_time=%s&access_token=%s&timestamp=%s&sign_method=%s&sign=%s" % (
    #             app_key, start_time, end_time,access_token, timest, sign_method, signature)
    #         url = base_url + path + _params
    #         req = requests.get(url, headers=headers)
    #         res = req.json()
    #         print("print 1")
    #         # raise Exception(res['data'][0])
    #         db = database.get_connection()
    #         # get_order = get_model("account.payment")
    #         for payment in res['data']:
    #             if not get_model("account.payment").search_browse(["transaction_no", "=", str(payment['transaction_number'])]):
    #                 try:
    #                     if payment['paid_status'] == "paid":
    #                         type = "out"
    #                     else:
    #                         type = "in"
    #                     vals = {
    #                         "date" : payment['transaction_date'],
    #                         "amount_subtotal": float((payment['amount']).replace(',','')),
    #                         "amount_total": float((payment['amount']).replace(',','')),
    #                         "amount_payment": float((payment['amount']).replace(',','')),
    #                         "ref": payment['reference'],
    #                         "type": type,
    #                         "transaction_no" : payment['transaction_number'],
    #                         "number" : payment['orderItem_no'],
    #                         "state": 'posted',
    #                         "memo": "Lazada",
    #                     }
    #                     print("print 2", payment['order_no'])
    #                     pmt_id = get_model("account.payment").create(vals)
    #                     payment_vals = {
    #                         "payment_id": pmt_id,
    #                         "amount": float((payment['amount']).replace(',','')),
    #                         "description": payment['details']
    #                     }
    #                     payment_line = get_model("account.payment.line").create(payment_vals)
    #                 except Exception as e:
    #                     print("Exception is", e)
    #                 #payment line
    #
    #         db.commit()
    #     if method == "get_products":
    #         # db = database.get_connection()
    #         account = get_model("lazada.account").search_browse([["id", "=", args[0][0]]])
    #         shop_id = account[0].shop_idno
    #         app_secret = account[0].auth_code
    #         app_key = shop_id
    #         app_secret = app_secret
    #         headers = {"Content-Type": "application/json"}
    #         sign_method = "sha256"
    #         timest = int(time.time() * 1000)
    #         base_url = "https://api.lazada.com.my/rest"
    #         path = "/products/get"
    #         offset = 0
    #         limit = context.get("limit") or 10000
    #         loop_limit = 1000
    #         item_ids = []
    #         total = 0
    #         i = 0
    #         job_id = args[0][0]
    #         offset = 0
    #         limit = context.get("limit") or 10000
    #         loop_limit = 1000
    #         item_ids = []
    #         total = 0
    #         i = 0
    #         job_id = 2
    #         if job_id:
    #             if tasks.is_aborted(job_id):
    #                 return
    #             tasks.set_progress(job_id, 50, "Step 1: Reading Products from Shopee: %s found." % (total))
    #         raise Exception("debugging12")
    #         # raise Exception("job_id", job_id)
    #         for x in range(5):
    #             if job_id:
    #                 print("print 1")
    #                 if tasks.is_aborted(job_id):
    #                     print("print 2")
    #                     return
    #                 print("print 3")
    #                 tasks.set_progress(job_id,50,"Step 1: Reading Products from Shopee: %s found."%(total))
    #                 print("print 4")
    #
    #                 raise Exception("debugging")
    #         account_id = args[0][0]
    #         # db = database.get_connection()
    #         # get_account = get_model("lazada.account").browse(account_id)
    #         access_token = account[0].token
    #         params = {
    #             "app_key": app_key,
    #             "access_token": access_token,
    #             "sign_method": sign_method,
    #             "timestamp": timest
    #         }
    #         signature = sign(app_secret, path, params)
    #
    #         params = "?app_key=%s&access_token=%s&timestamp=%s&sign_method=%s&sign=%s" % (
    #             app_key, access_token, timest, sign_method, signature)
    #         url = base_url + path + params
    #         print("url",url)
    #         req = requests.get(url, headers=headers)
    #         res = req.json()
    #         # print("response is", res)
    #         print("print 2")
    #         db = database.get_connection()
    #         get_product = get_model("lazada.product")
    #         # print("get_prodcut", get_product)
    #         for product in res['data']['products']:
    #             print("print 3")
    #             if not get_model("lazada.product").search_browse(["sync_id", "=",str(product["item_id"])]):
    #                 save_product = get_product.create({
    #                     "account_id": args[0][0],
    #                     "sync_id": product["item_id"],
    #                     "item_name": product['attributes']['name'],
    #                     "description": product['attributes']['description'],
    #                     "lazada_create_time":datetime.datetime.fromtimestamp(int(product['created_time'])/1000).strftime('%Y-%m-%d %H:%M:%S'),
    #                     "lazada_update_time":datetime.datetime.fromtimestamp(int(product['updated_time'])/1000).strftime('%Y-%m-%d %H:%M:%S'),
    #                     "images": product["images"],
    #                     "item_sku": product["skus"][0]['SellerSku'],
    #                     "trialProduct": product['trialProduct'],
    #                     "primary_category":product['primary_category'],
    #                     "marketImages":product["marketImages"],
    #                     "attributes":str(product['attributes']),
    #                     "item_status": product['status'],
    #                     "current_price": product["skus"][0]['price'],
    #                     "normal_stock": product["skus"][0]['quantity']
    #                 })
    #                 print("print 4")
    #                 ##Create System product
    #                 if not get_model("product").search_browse(["code", "=", str(product["item_id"])]):
    #                     print("2222")
    #                     get_system_product = get_model("product")
    #                     save_system_product = get_system_product.create({
    #                         "name": product['attributes']['name'],
    #                         "code": product["item_id"],
    #                         "type": "stock",
    #                         "uom_id": 1,
    #                     })
    #                     _get_product = get_model("lazada.product").browse(save_product)
    #                     _get_product.write({
    #                         "product_id": save_system_product
    #                     })
    #                 else:
    #                     get_system_product = get_model("product").search_browse(["code", "=", str(product["item_id"])])
    #                     _get_product = get_model("lazada.product").browse(save_product)
    #                     _get_product.write({
    #                         "product_id": get_system_product.id
    #                     })
    #                 ##Create Order Item
    #                 headers = {"Content-Type": "application/json"}
    #                 sign_method = "sha256"
    #                 timest = int(time.time() * 1000)
    #                 base_url = "https://api.lazada.com.my/rest"
    #                 path = "/product/item/get"
    #                 access_token = account[0].token
    #                 params = {
    #                     "access_token": access_token,
    #                     "app_key": app_key,
    #                     "sign_method": sign_method,
    #                     "timestamp": timest,
    #                     "item_id": product['item_id'],
    #                     "seller_sku": product["skus"][0]['SellerSku']
    #                 }
    #                 signature = sign(app_secret, path, params)
    #                 _params = "?app_key=%s&access_token=%s&timestamp=%s&sign_method=%s&sign=%s&item_id=%s&seller_sku=%s" % (
    #                     app_key, access_token, timest, sign_method, signature, product['item_id'],product["skus"][0]['SellerSku'])
    #                 url = base_url + path + _params
    #                 req = requests.get(url, headers=headers)
    #                 res = req.json()
    #                 print("save product id", save_product)
    #                 get_order_item = get_model("lazada.product.model")
    #                 try:
    #                     name= res['data']['attributes']['name']
    #                 except:
    #                     name= None
    #                 try:
    #                     created_at= (time.ctime(int(res['data']['created_time'])))[:-6]
    #                 except:
    #                     created_at= None
    #                 try:
    #                     updated_at= (time.ctime(int(res['data']['updated_time'])))[:-6]
    #                 except:
    #                     updated_at= None
    #                 try:
    #                     status= res['data']['status']
    #                 except:
    #                     status= None
    #                 try:
    #                     total_quantity= res['data']['skus'][0]['quantity']
    #                 except:
    #                     total_quantity= None
    #                 try:
    #                     available_quantity= res['data']['skus'][0]['Available']
    #                 except:
    #                     available_quantity= None
    #                 try:
    #                     seller_sku= res['data']['skus'][0]['SellerSku']
    #                 except:
    #                     seller_sku= None
    #                 try:
    #                     shop_sku= res['data']['skus'][0]['ShopSku']
    #                 except:
    #                     shop_sku= None
    #                 try:
    #                     item_skuID= res['data']['skus'][0]['SkuId']
    #                 except:
    #                     item_skuID= None
    #                 try:
    #                     package_width= res['data']['skus'][0]['package_width']
    #                 except:
    #                     package_width= None
    #                 try:
    #                     package_height= res['data']['skus'][0]['package_height']
    #                 except:
    #                     package_height= None
    #                 try:
    #                     package_length= res['data']['skus'][0]['package_length']
    #                 except:
    #                     package_length= None
    #                 try:
    #                     package_weight= res['data']['skus'][0]['package_weight']
    #                 except:
    #                     package_weight= None
    #                 try:
    #                     current_price= res['data']['skus'][0]['price']
    #                 except:
    #                     current_price= None
    #                 try:
    #                     item_id= res['data']['item_id']
    #                 except:
    #                     item_id= None
    #                 try:
    #                     variation= str(res['data']['variation'])
    #                 except:
    #                     variation= None
    #                 try:
    #                     brand= res['data']['attributes']['brand']
    #                 except:
    #                     brand= None
    #
    #                 try:
    #                     warranty_type= res['data']['attributes']['warranty_type']
    #                 except:
    #                     warranty_type= None
    #                 get_order_item.create({
    #                     "name": name,
    #                     "lazada_product_id": save_product,
    #                     "created_at": created_at,
    #                     "updated_at": updated_at,
    #                     "status": status,
    #                     "total_quantity": total_quantity,
    #                     "available_quantity": available_quantity,
    #                     "seller_sku": seller_sku,
    #                     "shop_sku": shop_sku,
    #                     "item_skuID": item_skuID,
    #                     "model_sku": item_skuID,
    #                     "package_width": package_width,
    #                     "package_height": package_height,
    #                     "package_length": package_length,
    #                     "package_weight": package_weight,
    #                     "item_id": item_id,
    #                     "current_price": current_price,
    #                     "variation": variation,
    #                     "brand": brand,
    #                     "warranty_type": warranty_type
    #                 })
    #                 _get_product = get_model("lazada.product").browse(save_product)
    #                 _get_product.write({
    #                     "has_model": True
    #                 })
    #                 db.commit()
    #         # print("response", res)
    #     if method == "get_products_categories":
    #         account = get_model("lazada.account").search_browse([["id", "=", args[0][0]]])
    #         shop_id = account[0].shop_idno
    #         app_secret = account[0].auth_code
    #         app_key = shop_id
    #         app_secret = app_secret
    #         headers = {"Content-Type": "application/json"}
    #         sign_method = "sha256"
    #         timest = int(time.time() * 1000)
    #         base_url = "https://api.lazada.com.my/rest"
    #         path = "/category/tree/get"
    #         access_token = account[0].token
    #         params = {
    #             "app_key": app_key,
    #             "access_token": access_token,
    #             "sign_method": sign_method,
    #             "timestamp": timest
    #         }
    #         signature = sign(app_secret, path, params)
    #
    #         params = "?app_key=%s&access_token=%s&timestamp=%s&sign_method=%s&sign=%s" % (
    #             app_key, access_token, timest, sign_method, signature)
    #         url = base_url + path + params
    #         req = requests.get(url, headers=headers)
    #         res = req.json()
    #         # raise Exception(res)
    #         # print("response is", res)
    #         db = database.get_connection()
    #         get_product_categ = get_model("lazada.product.categ")
    #         for product in res['data']:
    #             if not get_model("lazada.product.categ").search_browse(["sync_id", "=", str(product["category_id"])]):
    #                 save_product_categ = get_product_categ.create({
    #                     "sync_id": product["category_id"],
    #                     "original_category_name": product['name'],
    #                     "display_category_name": product['name']
    #                 })
    #                 print("2222")
    #                 db.commit()

Account.register()

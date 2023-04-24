# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

from netforce.model import Model, fields, get_model
from netforce import database, access, config, utils
from netforce.access import get_active_user, set_active_user
from netforce.access import get_active_company
from datetime import *
import time
import requests
import hashlib
import hmac
import json
import datetime

class LazadaProduct(Model):
    _name = "lazada.product"
    _string = "Lazada Product"
    _name_field = "item_name"
    #_multi_company = True
    #_key = ["company_id", "number"]
    _fields = {
        "account_id": fields.Many2One("lazada.account","Lazada Account",search=True),
        "sync_id": fields.Text("Sync ID",search=True), #XXX
        "category_id": fields.Many2One("lazada.product.categ","Product Category",search=True), #XXX
        "item_name": fields.Text("Product Name",search=True),
        "description": fields.Text("Product Description", search=True),
        "images": fields.Text("Product Images", search=True),
        "marketImages": fields.Text("Product Market Images", search=True),
        "attributes": fields.Text("Product Attributes", search=True),
        "trialProduct": fields.Boolean("Has Trial",search=True),
        "item_sku": fields.Text("Parent SKU",search=True),
        "primary_category": fields.Char("Primary Category",search=True),
        "lazada_create_time": fields.DateTime("Lazada Create Time"), #XXX
        "lazada_update_time": fields.DateTime("Lazada Update Time"), #XXX
        "current_price": fields.Decimal("Current Price"),
        "normal_stock": fields.Decimal("Normal Stock"),
        "condition": fields.Selection("Condition",[["NEW","NEW"],["USED","USED"]]),
        # "item_status": fields.Selection([["NORMAL","NORMAL"],["DELETED","DELETED"],["BANNED","BANNED"],["UNLIST","UNLIST"]],"Item Status",search=True),
        "item_status": fields.Char("Item Status",search=True),
        "has_model": fields.Boolean("Has Variants",search=True),
        "tier_variation": fields.One2Many("lazada.product.variation", "lazada_product_id", "Tier Variations"),
        "models": fields.One2Many("lazada.product.model", "lazada_product_id", "Variations"),
        "product_id": fields.Many2One("product","System Product",search=True),
        "show_warning": fields.Boolean("Show Warning", function="get_show_warning", store=True),
        "image": fields.File("Upload Product Image"),

    }
    _order = "account_id, sync_id"

    def write(self, ids, vals, **kw):
        super().write(ids, vals, **kw)
        # self.function_store(ids)

    # def create(self, vals, context={}):
    #     super().create(vals, context)
        # raise Exception(vals)
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
    #     ids = [1]
    #     for obj in self.browse(ids):
    #         account = get_model("lazada.account").search_browse([["id", "=", "1"]])
    #         shop_id = account[0].shop_idno
    #         app_secret = account[0].auth_code
    #         app_key = shop_id
    #         app_secret = app_secret
    #         headers = {"Content-Type": "application/json"}
    #         sign_method = "sha256"
    #         timest = int(time.time() * 1000)
    #         base_url = "https://api.lazada.com.my/rest"
    #         path = "/product/create"
    #         access_token = account[0].token
    #         # payload = "<Request><Product><Skus><Sku><ItemId>2983881255</ItemId><SkuId>14661758508</SkuId><SellerSku>WZT70P</SellerSku><SellableQuantity>20</SellableQuantity></Sku></Skus></Product></Request>"
    #         payload = '{     \"Request\": {         \"Product\": {             \"PrimaryCategory\": \"10002019\",             \"Images\": {                 \"Image\": [                     \"https://my-test-11.slatic.net/shop/4a75fac23a71ae58d20d0478f5ccc7c1.png\"                 ]             },             \"Attributes\": {                 \"name\": \"test 2022 02\",                 \"description\": \"TEST\",                 \"brand\": \"No Brand\",                 \"model\": \"test\",                 \"waterproof\": \"Waterproof\",                 \"warranty_type\": \"International Manufacturer Warranty\",                 \"warranty\": \"1 Month\",                 \"short_description\": \"cm x 1efgtecm<br /><brfwefgtek\",                 \"Hazmat\": \"None\",                 \"material\": \"Leather\",                 \"laptop_size\": \"11 - 12 inches\",                 \"delivery_option_sof\": \"No\"             },             \"Skus\": {                 \"Sku\": [                     {                         \"SellerSku\": \"WZD052\",                         \"quantity\": \"3\",                         \"price\": \"35\",                         \"special_price\": \"33\",                         \"special_from_date\": \"2022-06-20 17:18:31\",                         \"special_to_date\": \"2025-03-15 17:18:31\",                         \"package_height\": \"10\",                         \"package_length\": \"10\",                         \"package_width\": \"10\",                         \"package_weight\": \"0.5\",                         \"package_content\": \"laptop bag\",                         \"Images\": {                             \"Image\": [                                 \"https://my-test-11.slatic.net/shop/4a75fac23a71ae58d20d0478f5ccc7c1.png\"                             ]                         }                     }                 ]             }         }     } }'
    #         # payload = '"%7B+++++%22Request%22%3A+%7B+++++++++%22Product%22%3A+%7B+++++++++++++%22PrimaryCategory%22%3A+%2%22%2C+++++++++++++%22Images%22%3A+%7B+++++++++++++++++%22Image%22%3A+%5B+++++++++++++++++++++%22https://my-test-11.slatic.net/shop/4a75fac23a71ae58d20d0478f5ccc7c1.png%22+++++++++++++++++%5D+++++++++++++%7D%2C+++++++++++++%22Attributes%22%3A+%7B+++++++++++++++++%22name%22%3A+%22test+2022+02%22%2C+++++++++++++++++%22description%22%3A+%22TEST%22%2C+++++++++++++++++%22brand%22%3A+%22No+Brand%22%2C+++++++++++++++++%22model%22%3A+%22test%22%2C+++++++++++++++++%22waterproof%22%3A+%22Waterproof%22%2C+++++++++++++++++%22warranty_type%22%3A+%22Local+seller+warranty%22%2C+++++++++++++++++%22warranty%22%3A+%221+Month%22%2C+++++++++++++++++%22short_description%22%3A+%22cm+x+1efgtecm%3Cbr+%2F%3E%3Cbrfwefgtek%22%2C+++++++++++++++++%22Hazmat%22%3A+%22None%22%2C+++++++++++++++++%22material%22%3A+%22Leather%22%2C+++++++++++++++++%22laptop_size%22%3A+%2211+-+12+inches%22%2C+++++++++++++++++%22delivery_option_sof%22%3A+%22No%22+++++++++++++%7D%2C+++++++++++++%22Skus%22%3A+%7B+++++++++++++++++%22Sku%22%3A+%5B+++++++++++++++++++++%7B+++++++++++++++++++++++++%22SellerSku%22%3A+%22WZD05%22%2C+++++++++++++++++++++++++%22quantity%22%3A+%223%22%2C+++++++++++++++++++++++++%22price%22%3A+%2235%22%2C+++++++++++++++++++++++++%22special_price%22%3A+%2233%22%2C+++++++++++++++++++++++++%22special_from_date%22%3A+%222022-06-20+17%3A18%3A31%22%2C+++++++++++++++++++++++++%22special_to_date%22%3A+%222025-03-15+17%3A18%3A31%22%2C+++++++++++++++++++++++++%22package_height%22%3A+%2210%22%2C+++++++++++++++++++++++++%22package_length%22%3A+%2210%22%2C+++++++++++++++++++++++++%22package_width%22%3A+%2210%22%2C+++++++++++++++++++++++++%22package_weight%22%3A+%220.5%22%2C+++++++++++++++++++++++++%22package_content%22%3A+%22laptop+bag%22%2C+++++++++++++++++++++++++%22Images%22%3A+%7B+++++++++++++++++++++++++++++%22Image%22%3A+%5B+++++++++++++++++++++++++++++++++%22https://my-test-11.slatic.net/shop/4a75fac23a71ae58d20d0478f5ccc7c1.png%22+++++++++++++++++++++++++++++%5D+++++++++++++++++++++++++%7D+++++++++++++++++++++%7D+++++++++++++++++%5D+++++++++++++%7D+++++++++%7D+++++%7D+%7D"'
    #
    #         params = {
    #             "access_token": access_token,
    #             "app_key": app_key,
    #             "sign_method": sign_method,
    #             "timestamp": timest,
    #             "payload": payload
    #         }
    #         signature = sign(app_secret, path, params)
    #         _params = "?app_key=%s&access_token=%s&timestamp=%s&sign_method=%s&sign=%s&payload=%s" % (
    #             app_key, access_token, timest, sign_method, signature, payload)
    #         url = base_url + path + _params
    #         req = requests.post(url, headers=headers)
    #         res = req.json()
    #         if "message" in res:
    #             raise Exception(res)
    #         else:
    #             raise Exception(res)
    # def sign(secret, api, parameters):
    #     # ===========================================================================
    #     # @param secret
    #     # @param parameters
    #     # ===========================================================================
    #     sort_dict = sorted(parameters)
    #
    #     parameters_str = "%s%s" % (api,
    #                                str().join('%s%s' % (key, parameters[key]) for key in sort_dict))
    #
    #     h = hmac.new(secret.encode(encoding="utf-8"), parameters_str.encode(encoding="utf-8"),
    #                  digestmod=hashlib.sha256)
    #
    #     return h.hexdigest().upper()

    def get_model_list(self, ids, context={}):
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
        print("lazada.product.get_model_list",ids)
        app_key = "111456"
        app_secret = "Xp5vDjQwAiLQzclVQWddVX3RXq7wh0Xf"
        headers = {"Content-Type": "application/json"}
        sign_method = "sha256"
        timest = int(time.time() * 1000)
        base_url = "https://api.lazada.com.my/rest"
        path = "/product/item/get"
        order_id = ids[0]
        id = order_id
        db = database.get_connection()
        get_product = get_model("lazada.product").browse(id)
        item_id = get_product.sync_id
        account_id = get_product.account_id.id
        # db = database.get_connection()
        get_account = get_model("lazada.account").browse(account_id)
        access_token = get_account.token
        params = {
            "app_key": app_key,
            "access_token": access_token,
            "sign_method": sign_method,
            "timestamp": timest,
            "item_id": item_id
        }
        signature = sign(app_secret, path, params)

        params = "?app_key=%s&access_token=%s&item_id=%s&timestamp=%s&sign_method=%s&sign=%s" % (
            app_key, access_token,item_id, timest, sign_method, signature)
        url = base_url + path + params
        req = requests.get(url, headers=headers)
        res = req.json()
        if len(res['data']['variation']) > 0:
            db = database.get_connection()
            get_product = get_model("lazada.product").browse(id)
            get_product.write({"has_model": True})
            db.commit()
            db = database.get_connection()
            get_product_variants = get_model("lazada.product.variation")
            index=0
            for vairation in res['data']['variation']:
                vairation= res['data']['variation'][vairation]
                index+=1
                vairation_id = get_product_variants.create({
                    "name": vairation['name'],
                    "lazada_product_id": get_product.id,
                    "index": index

                })
                get_product_variants_options = get_model("lazada.product.variation.option")
                index_option = 0
                for options in vairation['options']:
                    index_option +=1
                    get_product_variants_options.create({
                        "variation_id" : vairation_id,
                        "value": options,
                        "index": index_option
                    })
                db.commit()
        else:
            db = database.get_connection()
            get_product = get_model("lazada.product").browse(id)
            get_product.write({"has_model": False})
            db.commit()
    def map_product(self, ids, context={}):
        for obj in self.browse(ids):
            if obj.has_model:
                for model in obj.models:
                    if not model.model_sku:
                        continue

                    prod_ids = get_model("product").search([["code","=",model.model_sku.strip()]])
                    if prod_ids:
                        get_product = get_model("lazada.product").browse(obj.id)
                        get_product.write({"product_id":prod_ids[0],"sync_id":model.model_sku.strip()})

            else:
                prod_ids = get_model("product").search([["code","=",obj.item_sku]])
                if prod_ids:
                    get_product = get_model("lazada.product").browse(obj.id)
                    get_product.write({"product_id": prod_ids[0],"sync_id":obj.item_sku})
    def update_stock(self, ids, context={}):
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
            account = get_model("lazada.account").search_browse([["id", "=", obj.account_id.id]])
            shop_id = account[0].shop_idno
            app_secret = account[0].auth_code
            app_key = shop_id
            app_secret = app_secret
            headers = {"Content-Type": "application/json"}
            sign_method = "sha256"
            timest = int(time.time() * 1000)
            base_url = "https://api.lazada.com.my/rest"
            path = "/product/stock/sellable/adjust"
            access_token = account[0].token
            payload = "<Request><Product><Skus><Sku><ItemId>2983881255</ItemId><SkuId>14661758508</SkuId><SellerSku>WZT70P</SellerSku><SellableQuantity>20</SellableQuantity></Sku></Skus></Product></Request>"
            params = {
                "access_token": access_token,
                "app_key": app_key,
                "sign_method": sign_method,
                "timestamp": timest,
                "payload": payload
            }
            signature = sign(app_secret, path, params)
            _params = "?app_key=%s&access_token=%s&timestamp=%s&sign_method=%s&sign=%s&payload=%s" % (
                app_key, access_token, timest, sign_method, signature, payload)
            url = base_url + path + _params
            req = requests.post(url, headers=headers)
            res = req.json()
            raise Exception(res)
    def get_show_warning(self, ids, context={}):
        print("lazada.product.get_show_warning",ids)
        vals = {}
        for obj in self.browse(ids):
            if not obj.has_model:
                if obj.product_id:
                    vals[obj.id] = False
                else:
                    vals[obj.id] = True
            else:
                model_ids = [m.id for m in obj.models]
                get_model("lazada.product.model").function_store(model_ids)
                vals[obj.id] = False
                for m in obj.models:
                    if m.show_warning:
                        vals[obj.id] = True
        return vals

    def create_on_lazada(self,ids, context={}):
        # raise Exception(ids[0])
        # obj = self.browse(ids[0])
        # raise Exception(obj.item_name)
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
        for obj in self.browse([ids[0]]):
            account = get_model("lazada.account").search_browse([["id", "=", "1"]])
            shop_id = account[0].shop_idno
            app_secret = account[0].auth_code
            app_key = shop_id
            app_secret = app_secret
            headers = {"Content-Type": "application/json"}
            sign_method = "sha256"
            timest = int(time.time() * 1000)
            base_url = "https://api.lazada.com.my/rest"
            path = "/product/create"
            access_token = account[0].token
            # raise Exception(obj.item_name)
            payload = '{\"Request\": {\"Product\": {\"PrimaryCategory\": \"10002019\",\"Images\": {' \
                      '\"Image\": [\"https://my-test-11.slatic.net/shop/4a75fac23a71ae58d20d0478f5ccc7c1.png\"' \
                      ']},\"Attributes\": {\"name\": \"test Product\",\"description\": \"TEST\",' \
                      '\"brand\": \"No Brand\",\"model\": \"test\",\"waterproof\": \"Waterproof\",' \
                      '\"warranty_type\": \"International Manufacturer Warranty\",\"warranty\": \"1 Month\",' \
                      '\"short_description\": \"cm x 1efgtecm<br /><brfwefgtek\",\"Hazmat\": \"None\",' \
                      '\"material\": \"Leather\",\"laptop_size\": \"11 - 12 inches\",' \
                      '\"delivery_option_sof\": \"No\"},\"Skus\": {\"Sku\": [{\"SellerSku\": \"WZD056\",' \
                      '\"quantity\": \"3\",\"price\": \"35\",\"special_price\": \"33\",' \
                      '\"special_from_date\": \"2022-06-20 17:18:31\",\"special_to_date\": \"2025-03-15 17:18:31\",' \
                      '\"package_height\": \"10\",\"package_length\": \"10\",\"package_width\": \"10\",' \
                      '\"package_weight\": \"0.5\",\"package_content\": \"laptop bag\",\"Images\": {' \
                      '\"Image\": [\"https://my-test-11.slatic.net/shop/4a75fac23a71ae58d20d0478f5ccc7c1.png\"' \
                      ']}}]}}}}'

            params = {
                "access_token": access_token,
                "app_key": app_key,
                "sign_method": sign_method,
                "timestamp": timest,
                "payload": payload
            }
            signature = sign(app_secret, path, params)
            _params = "?app_key=%s&access_token=%s&timestamp=%s&sign_method=%s&sign=%s&payload=%s" % (
                app_key, access_token, timest, sign_method, signature, payload)
            url = base_url + path + _params
            req = requests.post(url, headers=headers)
            res = req.json()
            if "message" in res:
                raise Exception(res)
            else:
                raise Exception(res)

    def sync_lazada_product(self,ids, context={}):
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

        for obj in self.browse([ids[0]]):
            account = get_model("lazada.account").search_browse([["id", "=", str(obj.account_id.id)]])
            shop_id = account[0].shop_idno
            app_secret = account[0].auth_code
            app_key = shop_id
            app_secret = app_secret
            headers = {"Content-Type": "application/json"}
            sign_method = "sha256"
            timest = int(time.time() * 1000)
            base_url = "https://api.lazada.com.my/rest"
            path = "/products/get"
            # db = database.get_connection()
            # get_account = get_model("lazada.account").browse(account_id)
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
            print("url", url)
            req = requests.get(url, headers=headers)
            res = req.json()
            # print("response is", res)
            print("print 2")
            db = database.get_connection()
            get_product = get_model("lazada.product")
            # print("get_prodcut", get_product)
            for product in res['data']['products']:
                print("print 3")
                if get_model("lazada.product").search_browse(["sync_id", "=", str(product["item_id"])]):
                    get_product = get_model("lazada.product").search_browse(["sync_id", "=", str(product["item_id"])])
                    save_product = get_product.write({
                        "account_id": account[0].id,
                        "sync_id": product["item_id"],
                        "item_name": product['attributes']['name'],
                        "description": product['attributes']['description'],
                        "lazada_create_time": datetime.datetime.fromtimestamp(
                            int(product['created_time']) / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                        "lazada_update_time": datetime.datetime.fromtimestamp(
                            int(product['updated_time']) / 1000).strftime('%Y-%m-%d %H:%M:%S'),
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
                    print("print 4")

                    ##Create Order Item
                    headers = {"Content-Type": "application/json"}
                    sign_method = "sha256"
                    timest = int(time.time() * 1000)
                    base_url = "https://api.lazada.com.my/rest"
                    path = "/product/item/get"
                    access_token = account[0].token
                    params = {
                        "access_token": access_token,
                        "app_key": app_key,
                        "sign_method": sign_method,
                        "timestamp": timest,
                        "item_id": product['item_id'],
                        "seller_sku": product["skus"][0]['SellerSku']
                    }
                    signature = sign(app_secret, path, params)
                    _params = "?app_key=%s&access_token=%s&timestamp=%s&sign_method=%s&sign=%s&item_id=%s&seller_sku=%s" % (
                        app_key, access_token, timest, sign_method, signature, product['item_id'],
                        product["skus"][0]['SellerSku'])
                    url = base_url + path + _params
                    req = requests.get(url, headers=headers)
                    res = req.json()
                    get_order_item = get_model("lazada.product.model")
                    try:
                        name = res['data']['attributes']['name']
                    except:
                        name = None
                    try:
                        created_at = (time.ctime(int(res['data']['created_time'])))[:-6]
                    except:
                        created_at = None
                    try:
                        updated_at = (time.ctime(int(res['data']['updated_time'])))[:-6]
                    except:
                        updated_at = None
                    try:
                        status = res['data']['status']
                    except:
                        status = None
                    try:
                        total_quantity = res['data']['skus'][0]['quantity']
                    except:
                        total_quantity = None
                    try:
                        available_quantity = res['data']['skus'][0]['Available']
                    except:
                        available_quantity = None
                    try:
                        seller_sku = res['data']['skus'][0]['SellerSku']
                    except:
                        seller_sku = None
                    try:
                        shop_sku = res['data']['skus'][0]['ShopSku']
                    except:
                        shop_sku = None
                    try:
                        item_skuID = res['data']['skus'][0]['SkuId']
                    except:
                        item_skuID = None
                    try:
                        package_width = res['data']['skus'][0]['package_width']
                    except:
                        package_width = None
                    try:
                        package_height = res['data']['skus'][0]['package_height']
                    except:
                        package_height = None
                    try:
                        package_length = res['data']['skus'][0]['package_length']
                    except:
                        package_length = None
                    try:
                        package_weight = res['data']['skus'][0]['package_weight']
                    except:
                        package_weight = None
                    try:
                        current_price = res['data']['skus'][0]['price']
                    except:
                        current_price = None
                    try:
                        item_id = res['data']['item_id']
                    except:
                        item_id = None
                    try:
                        variation = str(res['data']['variation'])
                    except:
                        variation = None
                    try:
                        brand = res['data']['attributes']['brand']
                    except:
                        brand = None

                    try:
                        warranty_type = res['data']['attributes']['warranty_type']
                    except:
                        warranty_type = None
                    if get_model("lazada.product.model").search_browse(["item_id", "=", str(item_id)]):
                        get_order_item = get_model("lazada.product.model").search_browse(["item_id", "=", str(item_id)])

                        get_order_item.write({
                            "name": name,
                            "created_at": created_at,
                            "updated_at": updated_at,
                            "status": status,
                            "total_quantity": total_quantity,
                            "available_quantity": available_quantity,
                            "seller_sku": seller_sku,
                            "shop_sku": shop_sku,
                            "item_skuID": item_skuID,
                            "model_sku": item_skuID,
                            "package_width": package_width,
                            "package_height": package_height,
                            "package_length": package_length,
                            "package_weight": package_weight,
                            "item_id": item_id,
                            "current_price": current_price,
                            "variation": variation,
                            "brand": brand,
                            "warranty_type": warranty_type
                        })
                        print("print 5")
                        db.commit()
        self.function_store(ids)

LazadaProduct.register()

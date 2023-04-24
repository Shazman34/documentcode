from netforce.model import Model,fields,get_model
from netforce import database
from datetime import *
import time
import requests
import json
import boto3
import boto3.session
from netforce.utils import json_dumps
import math
from decimal import *
import re
from pprint import pprint

def date_to_timestamp(t):
    return int((t-datetime(1970,1,1)).total_seconds()*1000)

class Price(Model):
    _name="xb.price"
    _string="Price"
    _fields={
        "time": fields.DateTime("Time",required=True),
        "product": fields.Selection([["btc_usd","BTC / USD"],["ltc_usd","LTC / USD"],["eth_usd","ETH / USD"],["btc_eur","BTC / EUR"],["ltc_eur","LTC / EUR"],["eth_eur","ETH / EUR"],["ltc_btc","LTC / BTC"],["eth_btc","ETH / BTC"],["btc_thb","BTC / THB"],["ltc_thb","LTC / THB"],["eth_thb","ETH / THB"],["usd_thb","USD / THB"],["gold96_thb","Gold 96.5% / THB"],["gold96_btc","Gold 96.5% / BTC"]],"Product",required=True),
        "source": fields.Selection([["bitstamp","Bitstamp"],["btce","BTC-E"],["gatecoin","Gatecoin"],["bxth","BX.in.th"],["sgb","SGB"],["scb","SCB"],["kasikorn","Kasikorn"],["bkkbank","BangkokBank"],["xbank","XBank"]],"Source",required=True),
        "bid": fields.Decimal("Bid",scale=6,required=True),
        "ask": fields.Decimal("Ask",scale=6,required=True),
    }
    _defaults={
        "time": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    _order="time desc"

    def import_bitstamp(self,context={}):
        print("import_bitstamp")
        url="https://www.bitstamp.net/api/ticker/"
        url+="?n=%s"%time.time()
        req=requests.get(url,timeout=5)
        data=json.loads(req.text)
        bid=data["bid"]
        ask=data["ask"]
        db=database.get_connection()
        t=time.strftime("%Y-%m-%d %H:%M:%S")
        db.execute("INSERT INTO xb_price (time,product,source,bid,ask) VALUES (%s,%s,%s,%s,%s)",t,"btc_usd","bitstamp",bid,ask)

    def import_btce(self,context={}):
        print("import_btce")
        url="https://btc-e.com/api/3/ticker/btc_usd"
        url+="?n=%s"%time.time()
        req=requests.get(url,timeout=5)
        data=json.loads(req.text)
        bid=data["btc_usd"]["sell"]
        ask=data["btc_usd"]["buy"]
        db=database.get_connection()
        t=time.strftime("%Y-%m-%d %H:%M:%S")
        db.execute("INSERT INTO xb_price (time,product,source,bid,ask) VALUES (%s,%s,%s,%s,%s)",t,"btc_usd","btce",bid,ask)

        url="https://btc-e.com/api/3/ticker/ltc_usd"
        url+="?n=%s"%time.time()
        req=requests.get(url,timeout=5)
        data=json.loads(req.text)
        bid=data["ltc_usd"]["sell"]
        ask=data["ltc_usd"]["buy"]
        db=database.get_connection()
        t=time.strftime("%Y-%m-%d %H:%M:%S")
        db.execute("INSERT INTO xb_price (time,product,source,bid,ask) VALUES (%s,%s,%s,%s,%s)",t,"ltc_usd","btce",bid,ask)

        url="https://btc-e.com/api/3/ticker/ltc_btc"
        url+="?n=%s"%time.time()
        req=requests.get(url,timeout=5)
        data=json.loads(req.text)
        bid=data["ltc_btc"]["sell"]
        ask=data["ltc_btc"]["buy"]
        db=database.get_connection()
        t=time.strftime("%Y-%m-%d %H:%M:%S")
        db.execute("INSERT INTO xb_price (time,product,source,bid,ask) VALUES (%s,%s,%s,%s,%s)",t,"ltc_btc","btce",bid,ask)

    def import_gatecoin(self,context={}):
        print("import_gatecoin")
        url="https://gatecoin.com/publicHttp.aspx?Url=Public/LiveTicker/ETHBTC&method=GET"
        url+="&n=%s"%time.time()
        req=requests.get(url,timeout=5)
        data=json.loads(req.text)
        bid=data["ticker"]["bid"]
        ask=data["ticker"]["ask"]
        db=database.get_connection()
        t=time.strftime("%Y-%m-%d %H:%M:%S")
        db.execute("INSERT INTO xb_price (time,product,source,bid,ask) VALUES (%s,%s,%s,%s,%s)",t,"eth_btc","gatecoin",bid,ask)

        url="https://gatecoin.com/publicHttp.aspx?Url=Public/LiveTicker/ETHEUR&method=GET"
        url+="&n=%s"%time.time()
        req=requests.get(url,timeout=5)
        data=json.loads(req.text)
        bid=data["ticker"]["bid"]
        ask=data["ticker"]["ask"]
        db=database.get_connection()
        t=time.strftime("%Y-%m-%d %H:%M:%S")
        db.execute("INSERT INTO xb_price (time,product,source,bid,ask) VALUES (%s,%s,%s,%s,%s)",t,"eth_eur","gatecoin",bid,ask)

        url="https://gatecoin.com/publicHttp.aspx?Url=Public/LiveTicker/BTCUSD&method=GET"
        url+="&n=%s"%time.time()
        req=requests.get(url,timeout=5)
        data=json.loads(req.text)
        bid=data["ticker"]["bid"]
        ask=data["ticker"]["ask"]
        db=database.get_connection()
        t=time.strftime("%Y-%m-%d %H:%M:%S")
        db.execute("INSERT INTO xb_price (time,product,source,bid,ask) VALUES (%s,%s,%s,%s,%s)",t,"btc_usd","gatecoin",bid,ask)

        url="https://gatecoin.com/publicHttp.aspx?Url=Public/LiveTicker/BTCEUR&method=GET"
        url+="&n=%s"%time.time()
        req=requests.get(url,timeout=5)
        data=json.loads(req.text)
        bid=data["ticker"]["bid"]
        ask=data["ticker"]["ask"]
        db=database.get_connection()
        t=time.strftime("%Y-%m-%d %H:%M:%S")
        db.execute("INSERT INTO xb_price (time,product,source,bid,ask) VALUES (%s,%s,%s,%s,%s)",t,"btc_eur","gatecoin",bid,ask)

    def import_bxth(self,context={}):
        print("import_bxth")
        url="https://bx.in.th/api/"
        url+="?n=%s"%time.time()
        req=requests.get(url,timeout=5)
        data=json.loads(req.text)
        bid=data["1"]["orderbook"]["bids"]["highbid"]
        ask=data["1"]["orderbook"]["asks"]["highbid"]
        db=database.get_connection()
        t=time.strftime("%Y-%m-%d %H:%M:%S")
        db.execute("INSERT INTO xb_price (time,product,source,bid,ask) VALUES (%s,%s,%s,%s,%s)",t,"btc_thb","bxth",bid,ask)

    def import_sgb(self,context={}):
        print("import_sgb")
        url="https://price.shininggold.com/get_current_prices"
        url+="?n=%s"%time.time()
        req=requests.get(url,timeout=5)
        data=json.loads(req.text)
        bid=data["rate_bid"]
        ask=data["rate_ask"]
        db=database.get_connection()
        t=time.strftime("%Y-%m-%d %H:%M:%S")
        db.execute("INSERT INTO xb_price (time,product,source,bid,ask) VALUES (%s,%s,%s,%s,%s)",t,"usd_thb","sgb",bid,ask)
        bid=data["g96_bid"]
        ask=data["g96_ask"]
        db.execute("INSERT INTO xb_price (time,product,source,bid,ask) VALUES (%s,%s,%s,%s,%s)",t,"gold96_thb","sgb",bid,ask)

    def import_scb(self,context={}):
        print("import_scb")
        url="http://www.scb.co.th/scb_api/index.jsp"
        url+="?n=%s"%time.time()
        req=requests.get(url,timeout=5)
        m=re.search(">USD<.*?>([\d\.]+)<.*?>([\d\.]+)<.*?>([\d\.]+)<.*?>([\d\.]+)<.*?>([\d\.]+)<",req.text,re.DOTALL)
        if not m:
            raise Exception("Invalid page data")
        #print("match",m.group(0))
        bid=Decimal(m.group(3))
        ask=Decimal(m.group(1))
        print("bid=%s ask=%s"%(bid,ask))
        db=database.get_connection()
        req=requests.get(url,timeout=5)
        t=time.strftime("%Y-%m-%d %H:%M:%S")
        db.execute("INSERT INTO xb_price (time,product,source,bid,ask) VALUES (%s,%s,%s,%s,%s)",t,"usd_thb","scb",bid,ask)

    def import_kasikorn(self,context={}):
        print("import_kasikorn")
        url="http://www.kasikornbank.com/EN/RatesAndFees/ForeignExchange/Pages/ForeignExchange.aspx"
        url+="?n=%s"%time.time()
        req=requests.get(url,timeout=5)
        m=re.search(">USD 50-100<.*?>([\d\.]+)\s*<.*?>([\d\.]+)\s*<.*?>([\d\.]+)\s*<.*?>([\d\.]+)\s*<.*?>([\d\.]+)\s*<.*?>([\d\.]+)\s*<",req.text,re.DOTALL)
        if not m:
            raise Exception("Invalid page data")
        #print("match",m.group(0))
        bid=Decimal(m.group(4))
        ask=Decimal(m.group(5))
        print("bid=%s ask=%s"%(bid,ask))
        db=database.get_connection()
        req=requests.get(url,timeout=5)
        t=time.strftime("%Y-%m-%d %H:%M:%S")
        db.execute("INSERT INTO xb_price (time,product,source,bid,ask) VALUES (%s,%s,%s,%s,%s)",t,"usd_thb","kasikorn",bid,ask)

    def import_bkkbank(self,context={}):
        print("import_bkkbank")
        url="http://www.bangkokbank.com/UserControls/ExchangeRates/ExchangeRates.asmx/Getfxrates"
        d=datetime.today()
        params={
            "dd": d.day,
            "mm": d.month,
            "yyyy": d.year,
            "upd": 1,
            "Lang": "Eng",
        }
        #print("params",params)
        req=requests.post(url,json=params,timeout=5)
        data=json.loads(req.text)
        bid=ask=None
        for r in data["d"]:
            if r["Family"]=="USD50":
                bid=r["TT"].strip()
                ask=r["Bill_DD_TT"].strip()
                break
        if not bid or not ask:
            raise Exception("Invalid price data")
        print("bid=%s ask=%s"%(bid,ask))
        db=database.get_connection()
        req=requests.get(url,timeout=5)
        t=time.strftime("%Y-%m-%d %H:%M:%S")
        db.execute("INSERT INTO xb_price (time,product,source,bid,ask) VALUES (%s,%s,%s,%s,%s)",t,"usd_thb","bkkbank",bid,ask)

    def update_xb_price(self,context={}):
        print("#"*80)
        print("update_xb_price")
        settings=get_model("xb.settings").browse(1)
        db=database.get_connection()
        res=db.get("SELECT time,bid,ask FROM xb_price WHERE product='btc_usd' AND source='bitstamp' ORDER BY time DESC LIMIT 1")
        btc_usd_bid=res.bid
        btc_usd_ask=res.ask
        res=db.get("SELECT time,bid,ask FROM xb_price WHERE product='usd_thb' AND source='bkkbank' ORDER BY time DESC LIMIT 1")
        usd_thb_bid=res.bid
        usd_thb_ask=res.ask
        res=db.get("SELECT time,bid,ask FROM xb_price WHERE product='ltc_usd' AND source='btce' ORDER BY time DESC LIMIT 1")
        ltc_usd_bid=res.bid
        ltc_usd_ask=res.ask
        res=db.get("SELECT time,bid,ask FROM xb_price WHERE product='ltc_btc' AND source='btce' ORDER BY time DESC LIMIT 1")
        sup_ltc_btc_bid=res.bid
        sup_ltc_btc_ask=res.ask
        res=db.get("SELECT time,bid,ask FROM xb_price WHERE product='eth_btc' AND source='gatecoin' ORDER BY time DESC LIMIT 1")
        sup_eth_btc_bid=res.bid
        sup_eth_btc_ask=res.ask
        res=db.get("SELECT time,bid,ask FROM xb_price WHERE product='gold96_thb' AND source='sgb' ORDER BY time DESC LIMIT 1")
        gold96_thb_bid=res.bid
        gold96_thb_ask=res.ask

        t=time.strftime("%Y-%m-%d %H:%M:%S")
        btc_thb_bid=math.floor(btc_usd_bid*usd_thb_bid-settings.btc_thb_discount)
        btc_thb_ask=math.ceil(btc_usd_ask*usd_thb_ask+settings.btc_thb_premium)
        db.execute("INSERT INTO xb_price (time,product,source,bid,ask) VALUES (%s,%s,%s,%s,%s)",t,"btc_thb","xbank",btc_thb_bid,btc_thb_ask)
        ltc_thb_bid=(ltc_usd_bid*usd_thb_bid-settings.btc_thb_discount).quantize(Decimal("0.01"),rounding=ROUND_DOWN)
        ltc_thb_ask=(ltc_usd_ask*usd_thb_ask+settings.btc_thb_premium).quantize(Decimal("0.01"),rounding=ROUND_UP)
        db.execute("INSERT INTO xb_price (time,product,source,bid,ask) VALUES (%s,%s,%s,%s,%s)",t,"ltc_thb","xbank",ltc_thb_bid,ltc_thb_ask)
        eth_thb_bid=(btc_thb_bid*sup_eth_btc_bid).quantize(Decimal("0.01"),rounding=ROUND_DOWN)
        eth_thb_ask=(btc_thb_ask*sup_eth_btc_ask).quantize(Decimal("0.01"),rounding=ROUND_UP)
        db.execute("INSERT INTO xb_price (time,product,source,bid,ask) VALUES (%s,%s,%s,%s,%s)",t,"eth_thb","xbank",eth_thb_bid,eth_thb_ask)
        ltc_btc_bid=sup_ltc_btc_bid.quantize(Decimal("0.00001"),rounding=ROUND_DOWN)
        ltc_btc_ask=sup_ltc_btc_ask.quantize(Decimal("0.00001"),rounding=ROUND_UP)
        db.execute("INSERT INTO xb_price (time,product,source,bid,ask) VALUES (%s,%s,%s,%s,%s)",t,"ltc_btc","xbank",ltc_btc_bid,ltc_btc_ask)
        eth_btc_bid=sup_eth_btc_bid.quantize(Decimal("0.00001"),rounding=ROUND_DOWN)
        eth_btc_ask=sup_eth_btc_ask.quantize(Decimal("0.00001"),rounding=ROUND_UP)
        db.execute("INSERT INTO xb_price (time,product,source,bid,ask) VALUES (%s,%s,%s,%s,%s)",t,"eth_btc","xbank",eth_btc_bid,eth_btc_ask)
        gold96_btc_bid=(gold96_thb_bid/btc_thb_ask-settings.gold96_btc_discount).quantize(Decimal("0.0001"),rounding=ROUND_DOWN)
        gold96_btc_ask=(gold96_thb_ask/btc_thb_bid+settings.gold96_btc_premium).quantize(Decimal("0.0001"),rounding=ROUND_UP)
        db.execute("INSERT INTO xb_price (time,product,source,bid,ask) VALUES (%s,%s,%s,%s,%s)",t,"gold96_btc","xbank",gold96_btc_bid,gold96_btc_ask)

    def upload_s3(self,context={}):
        print("upload_s3")
        settings=get_model("xb.settings").browse(1)
        db=database.get_connection()
        data={}
        res=db.get("SELECT time,bid,ask FROM xb_price WHERE product='btc_thb' AND source='xbank' ORDER BY time DESC LIMIT 1")
        data["btc_thb_bid"]=res.bid
        data["btc_thb_ask"]=res.ask
        res=db.get("SELECT time,bid,ask FROM xb_price WHERE product='ltc_thb' AND source='xbank' ORDER BY time DESC LIMIT 1")
        data["ltc_thb_bid"]=res.bid
        data["ltc_thb_ask"]=res.ask
        res=db.get("SELECT time,bid,ask FROM xb_price WHERE product='eth_thb' AND source='xbank' ORDER BY time DESC LIMIT 1")
        data["eth_thb_bid"]=res.bid
        data["eth_thb_ask"]=res.ask
        res=db.get("SELECT time,bid,ask FROM xb_price WHERE product='ltc_btc' AND source='xbank' ORDER BY time DESC LIMIT 1")
        data["ltc_xbt_bid"]=res.bid
        data["ltc_xbt_ask"]=res.ask
        res=db.get("SELECT time,bid,ask FROM xb_price WHERE product='eth_btc' AND source='xbank' ORDER BY time DESC LIMIT 1")
        data["eth_xbt_bid"]=res.bid
        data["eth_xbt_ask"]=res.ask
        res=db.get("SELECT time,bid,ask FROM xb_price WHERE product='gold96_btc' AND source='xbank' ORDER BY time DESC LIMIT 1")
        data["gold96_btc_bid"]=res.bid
        data["gold96_btc_ask"]=res.ask
        data["time"]=time.strftime("%Y-%m-%d %H:%M:%S"),
        session=boto3.session.Session(aws_access_key_id=settings.aws_key,aws_secret_access_key=settings.aws_secret)
        s3=session.resource("s3")
        body="callback1(%s);"%json_dumps(data)
        s3.Object("xbank","current_prices.jsonp").put(Body=body)

    def upload_chart_s3(self,context={}):
        print("upload_chart_s3")
        db=database.get_connection()
        dt=timedelta(minutes=5)
        t0=datetime.now()-timedelta(days=1)
        res=db.query("SELECT time,bid,ask FROM xb_price WHERE product='btc_thb' AND source='xbank' AND time>=%s ORDER BY time",t0.strftime("%Y-%m-%d %H:%M:%S"))
        #print("%d prices"%len(res))
        t1=t0+dt
        data=[]
        period=None
        for r in res:
            p=r["ask"]
            while r["time"]>=t1.strftime("%Y-%m-%d %H:%M:%S"):
                if period:
                    data.append(period)
                    period=None
                t1+=dt
            if period is None:
                t0=t1-dt
                period=[date_to_timestamp(t0),p,p,p,p]
            else:
                if p>period[2]: period[2]=p
                if p<period[3]: period[3]=p
                period[4]=p
        data.append(period)
        #print("price chart data:",data)
        print("%d periods"%len(data))
        settings=get_model("xb.settings").browse(1)
        session=boto3.session.Session(aws_access_key_id=settings.aws_key,aws_secret_access_key=settings.aws_secret)
        s3=session.resource("s3")
        body="callback2(%s);"%json_dumps(data)
        s3.Object("xbank","price_chart.jsonp").put(Body=body)

Price.register()

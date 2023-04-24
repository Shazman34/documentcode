from netforce.model import Model,fields,get_model
from netforce import database
from netforce import utils
import time
import random
import subprocess

class Swap(Model):
    _name="hx.swap"
    _string="Swap"
    _name_field="number"
    _fields={
        "time": fields.DateTime("Time",required=True),
        "number": fields.Char("Number",required=True),
        "rfq_id": fields.Many2One("hx.rfq","RFQ"),
        "quote_id": fields.Many2One("hx.quote","Quote"),
        "from_user_id": fields.Many2One("base.user","From User",required=True),
        "from_asset": fields.Char("From Asset",required=True),
        "from_qty": fields.Decimal("From Qty",scale=8,required=True),
        "to_user_id": fields.Many2One("base.user","To User",required=True),
        "to_asset": fields.Char("To Asset",required=True),
        "to_qty": fields.Decimal("To Qty",scale=8,required=True),
        "from_user_receive_addr": fields.Char("From User Receive Addr"),
        "to_user_receive_addr": fields.Char("To User Receive Addr"),
        "from_user_transfer_addr": fields.Char("From User Transfer Addr"),
        "to_user_transfer_addr": fields.Char("To User Transfer Addr"),
        "state": fields.Selection([["draft","Draft"],["in_progress","In Progress"],["done","Done"]],"Status",required=True),
        "status_message": fields.Text("Status Message"),
        "contract_tx_hash": fields.Char("Contract Transaction"),
        "contract_addr": fields.Char("Contract Address"),
        "from_deposit_qty": fields.Decimal("From Deposit Qty",scale=8),
        "to_deposit_qty": fields.Decimal("To Deposit Qty",scale=8),
        "release_tx_hash": fields.Char("Release Transaction"),
    }
    _order="time desc"
    _defaults={
        "time": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
        "number": lambda *a: "SW-%.6d"%random.randint(0,1000000),
        "state": "draft",
        "status_message": "Awaiting maker and taker recipient addresses",
    }

    def set_to_user_receive_addr(self,ids,addr,context={}):
        print("Swap.set_to_user_receive_addr",ids,addr)
        obj=self.browse(ids[0])
        if not addr:
            raise Exception("Missing address")
        if obj.state!="draft":
            raise Exception("Invalid status")
        if obj.to_user_receive_addr:
            raise Exception("Address already recorded")
        obj.write({"to_user_receive_addr":addr})
        obj.next_step()
        obj.update_status()

    def set_from_user_receive_addr(self,ids,addr,context={}):
        print("Swap.set_from_user_receive_addr",ids,addr)
        obj=self.browse(ids[0])
        if not addr:
            raise Exception("Missing address")
        if obj.state!="draft":
            raise Exception("Invalid status")
        if obj.from_user_receive_addr:
            raise Exception("Address already recorded")
        obj.write({"from_user_receive_addr":addr})
        obj.next_step()
        obj.update_status()

    def create_contract(self,ids,context={}):
        print("Swap.create_contract",ids)
        obj=self.browse(ids[0])
        if not obj.from_user_receive_addr:
            raise Exception("Missing taker receive addr")
        if not obj.to_user_receive_addr:
            raise Exception("Missing maker receive addr")
        if obj.to_asset!="HXT" or obj.from_asset!="ETH":
            raise Exception("Contract creation only works for HXT/ETH for now (testing)")
        script_path="/home/datrus/modules/netforce_hydra/netforce_hydra/scripts/create_contract.js"
        args=[script_path,str(obj.from_qty),str(obj.to_qty),obj.from_user_receive_addr,obj.to_user_receive_addr]
        p=subprocess.Popen(args,stdout=subprocess.PIPE)
        res=p.stdout.readline()
        if not res:
            raise Exception("Failed to create contract")
        tx_hash=res.decode("utf-8").strip()
        obj.write({"contract_tx_hash": tx_hash})
        obj.update_status()

    def get_contract_addr(self,ids,context={}):
        print("Swap.get_contract_addr",ids)
        obj=self.browse(ids[0])
        if not obj.contract_tx_hash:
            raise Exception("Missing contract transaction")
        script_path="/home/datrus/modules/netforce_hydra/netforce_hydra/scripts/get_contract_addr.js"
        args=[script_path,obj.contract_tx_hash]
        p=subprocess.Popen(args,stdout=subprocess.PIPE)
        res=p.stdout.readline()
        if not res:
            raise Exception("Failed to get contract address")
        addr=res.decode("utf-8").strip()
        obj.write({"contract_addr": addr, "from_user_transfer_addr": addr, "to_user_transfer_addr": addr})
        obj.update_status()

    def get_deposit_bals(self,ids,context={}):
        print("Swap.get_deposit_bals",ids)
        obj=self.browse(ids[0])
        if not obj.contract_addr:
            raise Exception("Missing contract address")
        script_path="/home/datrus/modules/netforce_hydra/netforce_hydra/scripts/get_deposit_bals.js"
        args=[script_path,obj.contract_addr]
        p=subprocess.Popen(args,stdout=subprocess.PIPE)
        res=p.stdout.readline()
        if not res:
            raise Exception("Failed to get deposit balances")
        vals=res.decode("utf-8").split(" ")
        from_deposit=vals[0]
        to_deposit=vals[1]
        obj.write({"from_deposit_qty":from_deposit,"to_deposit_qty":to_deposit})
        obj.update_status()

    def release_funds(self,ids,context={}):
        print("Swap.release_funds",ids)
        obj=self.browse(ids[0])
        if not obj.contract_addr:
            raise Exception("Missing contract address")
        script_path="/home/datrus/modules/netforce_hydra/netforce_hydra/scripts/release_funds.js"
        args=[script_path,obj.contract_addr]
        p=subprocess.Popen(args,stdout=subprocess.PIPE)
        res=p.stdout.readline()
        if not res:
            raise Exception("Failed to release funds")
        tx_hash=res.decode("utf-8").strip()
        obj.write({"release_tx_hash": tx_hash})
        obj.update_status()

    def update_status(self,ids,context={}):
        print("Swap.update_status",ids)
        obj=self.browse(ids[0])
        if not obj.from_user_receive_addr and not obj.to_user_receive_addr:
            msg="Awaiting recipient address of %s and %s"%(obj.to_user_id.login,obj.from_user_id.login)
        elif not obj.from_user_receive_addr:
            msg="Awaiting recipient address of %s"%obj.from_user_id.login
        elif not obj.to_user_receive_addr:
            msg="Awaiting recipient address of %s"%obj.to_user_id.login
        elif not obj.contract_tx_hash:
            msg="Deploying contract"
        elif not obj.contract_addr:
            msg="Awaiting contract address"
        elif (obj.from_deposit_qty or 0)<obj.from_qty and (obj.to_deposit_qty or 0)<obj.to_qty:
            msg="Awaiting funds transfer from %s and %s"%(obj.to_user_id.login,obj.from_user_id.login)
        elif (obj.from_deposit_qty or 0)<obj.from_qty:
            msg="Awaiting funds transfer from %s"%obj.from_user_id.login
        elif (obj.to_deposit_qty or 0)<obj.to_qty:
            msg="Awaiting funds transfer from %s"%obj.to_user_id.login
        elif not obj.release_tx_hash:
            msg="Releasing funds"
        else:
            msg="Funds released"
        obj.write({"status_message": msg})

    def next_step(self,ids,context={}):
        print("Swap.next_step",ids)
        obj=self.browse(ids[0])
        if obj.from_user_receive_addr and obj.to_user_receive_addr and not obj.contract_tx_hash:
            obj.create_contract()
        elif obj.contract_tx_hash and not obj.contract_addr:
            obj.get_contract_addr()
        elif obj.contract_addr and not obj.release_tx_hash and ((obj.from_deposit_qty or 0)<obj.from_qty or (obj.to_deposit_qty or 0)<obj.to_qty):
            obj.get_deposit_bals()
        elif (obj.from_deposit_qty or 0)>=obj.from_qty and (obj.to_deposit_qty or 0)>=obj.to_qty and not obj.release_tx_hash:
            obj.release_funds()
        else:
            print("nothing to do")
            obj.update_status()

Swap.register()

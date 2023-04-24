#!/usr/bin/env node
var Web3=require("web3");
var PrivateKeyProvider = require("truffle-privatekey-provider");

var priv_key="3C2309BD5B8949BD0555B72CC57FEE46ADF532FE7A42D3B618F27856A348D343";

var account_address="0x893DCF0eE0a6979B8Ae246134Dc329Af66042f85"; // XXX

var contract_build=require("./HydraContractExchangeEthToken.json");

const gas_price = '20000000000';

var hydra_token="0x656a5f1d52a7fb2da3e00f973349c48b6d201b0f";

var get_deposit_bals=async contract_addr=>{
    var provider = new PrivateKeyProvider(priv_key, "https://ropsten.infura.io/v3/fcdbc05e44a84542a85beff327904450");
    var rpc = new Web3(provider);
    const contract = new rpc.eth.Contract(contract_build.abi,contract_addr);
    var deposit_amount_eth=await contract.methods.get_deposit_amount_eth().call();
    var deposit_amount_token=await contract.methods.get_deposit_amount_token().call();
    return {
        deposit_amount_eth: rpc.utils.fromWei(deposit_amount_eth,"ether"),
        deposit_amount_token: deposit_amount_token/100.0, // XXX
    }
};

var addr=process.argv[2];
if (!addr) throw "Missing contract addr";

get_deposit_bals(addr).then(res=>{
    console.log(res.deposit_amount_eth+" "+res.deposit_amount_token);
}).catch(err=>{
    console.error("Error: "+err);
});

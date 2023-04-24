#!/usr/bin/env node
var Web3=require("web3");
var PrivateKeyProvider = require("truffle-privatekey-provider");

var priv_key="3C2309BD5B8949BD0555B72CC57FEE46ADF532FE7A42D3B618F27856A348D343";

var account_address="0x893DCF0eE0a6979B8Ae246134Dc329Af66042f85"; // XXX

var contract_build=require("./HydraContractExchangeEthToken.json");

const gas_price = '20000000000';

var hydra_token="0x656a5f1d52a7fb2da3e00f973349c48b6d201b0f";

var get_contract_addr=async tx_hash=>{
    //console.log("get_contract_addr",tx_hash);
    var provider = new PrivateKeyProvider(priv_key, "https://ropsten.infura.io/v3/fcdbc05e44a84542a85beff327904450");
    var rpc = new Web3(provider);
    var receipt = await rpc.eth.getTransactionReceipt(tx_hash);
    //console.log("receipt",receipt);
    if (!receipt) throw "Failed to get transaction receipt";
    if (!receipt.contractAddress) throw "Contract address not found";
    return receipt.contractAddress;
};

var tx_hash=process.argv[2];
if (!tx_hash) throw "Missing tx_hash";

get_contract_addr(tx_hash).then(addr=>{
    console.log(addr);
}).catch(err=>{
    console.error("Error: "+err);
});

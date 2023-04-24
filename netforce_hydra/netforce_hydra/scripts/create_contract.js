#!/usr/bin/env node
var Web3=require("web3");
var PrivateKeyProvider = require("truffle-privatekey-provider");

var priv_key="3C2309BD5B8949BD0555B72CC57FEE46ADF532FE7A42D3B618F27856A348D343";

var account_address="0x893DCF0eE0a6979B8Ae246134Dc329Af66042f85"; // XXX

var contract_build=require("./HydraContractExchangeEthToken.json");

const gas_price = '20000000000';

var hydra_token="0x656a5f1d52a7fb2da3e00f973349c48b6d201b0f";

var create_contract_test=async (amount_eth,amount_token,recipient_eth,recipient_token)=>{
	//console.log("create_contract_test",amount_eth,amount_token,recipient_eth,recipient_token);
    var provider = new PrivateKeyProvider(priv_key, "https://ropsten.infura.io/v3/fcdbc05e44a84542a85beff327904450");
    var rpc = new Web3(provider);
    var amount_eth_int=rpc.utils.toWei(""+amount_eth,"ether");
    var amount_token_int=amount_token*100; // XXX
    return new Promise((resolve,reject)=>{
        const contract = new rpc.eth.Contract(contract_build.abi);
        contract.deploy({
            data: contract_build.bytecode,
            arguments: [hydra_token,amount_eth_int,amount_token_int,recipient_eth,recipient_token]
        }).send({
            from: account_address,
            gas: '1000000',
            gasPrice: gas_price,
        }).on('transactionHash', tx_hash=>{
            resolve(tx_hash);
        }).catch(err=>{
            reject(err);
        });
    });
};

var amount_eth=parseFloat(process.argv[2]);
if (!amount_eth) throw "Missing amount_eth";
var amount_token=parseFloat(process.argv[3]);
if (!amount_token) throw "Missing amount_token";
var recipient_eth=process.argv[4];
if (!recipient_eth) throw "Missing recipient_eth";
var recipient_token=process.argv[5];
if (!recipient_token) throw "Missing recipient_token";

create_contract_test(amount_eth,amount_token,recipient_eth,recipient_token).then(tx_hash=>{
    console.log(tx_hash);
}).catch(err=>{
    console.error("Error: "+err);
});

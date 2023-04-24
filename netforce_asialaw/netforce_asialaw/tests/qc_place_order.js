#!/usr/bin/env node
var rpc=require("./netforce_rpc");

rpc.set_base_url("https://backend.netforce.com");
rpc.set_database("nfo_asialaw");

var opts={
    client_id: 12,
    categ_id: 41,
    lawyer_id: 2,
    facts: "testing",
    questions: "testing?",
    parties: "ACME1,ACME2",
    call_times: ["2018-01-01 09:30:00","2018-01-01 12:30:00"],
    return_url: "https://asialawnetwork.com/qc_paypal_return",
    cancel_url: "https://asialawnetwork.com/qc_paypal_cancel",
};
rpc.execute("aln.api","qc_place_order",[],opts,(err,data)=>{
    if (err) {
        console.error(err);
        return;
    }
    console.log(data);
});

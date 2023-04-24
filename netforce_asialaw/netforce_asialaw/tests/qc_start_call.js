#!/usr/bin/env node
var rpc=require("./netforce_rpc");

rpc.set_base_url("https://backend.netforce.com");
rpc.set_database("nfo_asialaw");

var opts={
    case_id: 35,
    record_call: false,
};
rpc.execute("aln.api","qc_start_call",[],opts,(err,data)=>{
    if (err) {
        console.error(err);
        return;
    }
    console.log(data);
});

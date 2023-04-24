#!/usr/bin/env node
var rpc=require("./netforce_rpc");

rpc.set_base_url("https://backend.netforce.com");
rpc.set_database("nfo_asialaw");

var opts={
    case_id: 35,
};
rpc.execute("aln.api","get_case_info",[],opts,(err,data)=>{
    if (err) {
        console.error(err);
        return;
    }
    console.log(data);
});

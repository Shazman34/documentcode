#!/usr/bin/env node
var rpc=require("./netforce_rpc");

rpc.set_base_url("https://backend.netforce.com");
rpc.set_database("nfo_asialaw");

var opts={
    categ_id: 41,
};
rpc.execute("aln.api","get_qc_categ_info",[],opts,(err,data)=>{
    if (err) {
        console.error(err);
        return;
    }
    console.log(data);
});

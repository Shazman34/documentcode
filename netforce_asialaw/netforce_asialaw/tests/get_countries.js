#!/usr/bin/env node
var rpc=require("./netforce_rpc");

rpc.set_base_url("https://backend.netforce.com");
rpc.set_database("nfo_asialaw");

rpc.execute("aln.api","get_countries",[],{},(err,data)=>{
    if (err) {
        console.error(err);
        return;
    }
    console.log(data);
});

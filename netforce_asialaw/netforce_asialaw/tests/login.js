#!/usr/bin/env node
var rpc=require("./netforce_rpc");

rpc.set_base_url("https://backend.netforce.com");
rpc.set_database("nfo_asialaw");

var opts={
    email: "cherilynt@gmail.com",
    password: "1234",
};
rpc.execute("aln.api","login",[],opts,(err,data)=>{
    if (err) {
        console.error(err);
        return;
    }
    console.log(data);
});

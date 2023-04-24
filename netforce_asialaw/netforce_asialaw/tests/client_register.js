#!/usr/bin/env node
var rpc=require("./netforce_rpc");

rpc.set_base_url("https://backend.netforce.com");
rpc.set_database("nfo_asialaw");

var opts={
    first_name: "David",
    last_name: "Janssens",
    email: "dj4@netforce.com",
    country_code: "SG",
    phone: "6512345678",
    password: "1234",
    confirm_password: "1234",
};
rpc.execute("aln.api","client_register",[],opts,(err,data)=>{
    if (err) {
        console.error(err);
        return;
    }
    console.log(data);
});

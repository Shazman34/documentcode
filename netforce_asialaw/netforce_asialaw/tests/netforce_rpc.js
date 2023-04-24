var request=require("request");

var _base_url=null;
var _database=null;

module.exports.set_base_url=function(url) {
    _base_url=url;
}

module.exports.set_database=function(dbname) {
    _database=dbname;
}

module.exports.execute=function (model,method,args,opts,cb) {
    //console.log("RPC",model,method,args,opts);
    if (!_base_url) throw "RPC base url not set";
    var params=[model,method];
    params.push(args);
    params.push(opts||{});
    //var cookies=utils.get_cookies();
    //params.push(cookies);
    var headers={};
    if (_database) headers["X-Database"]=_database;
    request({
        uri: _base_url+"/json_rpc",
        method: "POST",
        headers: headers,
        json: {
            id: (new Date()).getTime(),
            method: "execute",
            params: params
        },
    },(error,response,data)=>{
        if (error) {
            //console.log("RPC ERROR",model,method,error);
            return;
        }
        if (data.error) {
            //console.log("RPC ERROR",model,method,data.error.message);
        } else {
            //console.log("RPC OK",model,method,data.result);
        }
        if (cb) {
            cb(data.error?data.error.message:null,data.result);
        }
    });
}

var rpc_url="https://admin.xbank.com/json_rpc";

module.exports.execute=function (model,method,args,opts,cb) {
    console.log("RPC",model,method,args,opts);
    var params=[model,method];
    params.push(args);
    if (opts) {
        params.push(opts);
    }
    $.ajax({
        url: rpc_url,
        method: "POST",
        data: JSON.stringify({
            id: (new Date()).getTime(),
            method: "execute",
            params: params
        }),
        dataType: "json",
        contentType: "application/x-www-form-urlencoded; charset=UTF-8",
        success: function(data) {
            if (data.error) {
                console.log("RPC ERROR",model,method,data.error.message);
            } else {
                console.log("RPC OK",model,method,data.result);
            }
            if (cb) {
                cb(data.error,data.result);
            }
        },
        error: function() {
            console.log("RPC ERROR",model,method);
        }
    });
}

module.exports.execute_cache=function (model,method,args,opts,cb) {
    console.log("RPC_cache",model,method,args,opts);
    var data={
        id: (new Date()).getTime(),
        model: model,
        method: method,
    };
    if (args) data.args=JSON.stringify(args);
    if (opts) data.opts=JSON.stringify(opts);
    $.ajax({
        url: rpc_url,
        method: "GET",
        data: data,
        dataType: "json",
        success: function(data) {
            if (data.error) {
                console.log("RPC ERROR",model,method,data.error.message);
            } else {
                console.log("RPC OK",model,method,data.result);
            }
            if (cb) {
                cb(data.error,data.result);
            }
        },
        error: function() {
            console.log("RPC ERROR",model,method);
        }
    });
}

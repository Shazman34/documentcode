RPC=require("./RPC");
actions=require("./actions")

module.exports.get_prices=function() {
    console.log(">>> actions.get_prices");
    return function(dispatch,getState) {
        $.ajax({
            url: "https://s3-ap-southeast-1.amazonaws.com/xbank/current_prices.jsonp?callback=?",
            type: "GET",
            cache: false,
            dataType: "jsonp",
            jsonpCallback: "callback1",
            success: function(data) {
                var action={
                    type: "GOT_PRICES",
                    prices: data,
                }
                dispatch(action);
            }.bind(this),
        });
    }
}

module.exports.get_price_chart=function() {
    console.log(">>> actions.get_price_chart");
    return function(dispatch,getState) {
        $.ajax({
            url: "https://s3-ap-southeast-1.amazonaws.com/xbank/price_chart.jsonp?callback=?",
            type: "GET",
            cache: false,
            dataType: "jsonp",
            jsonpCallback: "callback2",
            success: function(data) {
                $("#xb-price-chart").highcharts('StockChart', {
                    title : {
                        text : 'XBT/THB Price'
                    },
                    series : [{
                        type : 'candlestick',
                        name : 'BTC/THB Price',
                        data : data,
                    }],
                    rangeSelector: {
                        enabled: false,
                    },
                    credits: {
                        enabled: false,
                    },
                });
            }.bind(this),
        });
    }
}

module.exports.register=function(name,email,password) {
    console.log(">>> actions.register",name,email,password);
    return function(dispatch,getState) {
        RPC.execute("xb.interface","sign_up",[name,email,password],{},function(err,data) {
            if (err) {
                alert("Failed to sign up: "+err.message);
                return;
            }
            localStorage.user_id=data.user_id;
            window.location="/account";
            dispatch(actions.load_user_data());
        }.bind(this));
    }
}

module.exports.login=function(email,password) {
    console.log(">>> actions.login",email,password);
    return function(dispatch,getState) {
        RPC.execute("xb.interface","login",[email,password],{},function(err,data) {
            if (err) {
                alert("Failed to login: "+err.message);
                return;
            }
            localStorage.user_id=data.user_id;
            window.location="/account";
            dispatch(actions.load_user_data());
        }.bind(this));
    }
}

module.exports.logout=function() {
    console.log(">>> actions.logout");
    delete localStorage.user_id;
    window.location="/";
    return {
        type: "LOGOUT",
    }
}

module.exports.load_user_data=function() {
    console.log(">>> actions.load_user_data");
    return function(dispatch) {
        var user_id=parseInt(localStorage.user_id);
        if (!user_id) throw "User ID not found";
        dispatch({
            type: "USER_DATA_LOADING",
        });
        RPC.execute("base.user","read_path",[[user_id],["email","name","xb_account_id"]],{},function(err,data) {
            dispatch({
                type: "USER_DATA_LOADED",
                user_data: data[0],
            });
        }.bind(this));
    }
}

module.exports.withdraw=function(currency,amount,address,cb) {
    console.log(">>> actions.withdraw",currency,amount,address);
    return function(dispatch) {
        var args=[currency,amount,address];
        var user_id=parseInt(localStorage.user_id);
        var ctx={
            user_id: user_id, // XXX
        };
        RPC.execute("xb.interface","withdraw",args,{context:ctx},function(err,data) {
            if (err) {
                if (cb) cb(err);
                return;
            }
            cb(null,data);
        }.bind(this));
    }
}

module.exports.new_address=function(currency,cb) {
    console.log(">>> actions.new_address",currency);
    return function(dispatch,getState) {
        var user_id=parseInt(localStorage.user_id);
        var ctx={
            user_id: user_id, // XXX
        };
        RPC.execute("xb.interface","new_address",[currency],{context:ctx},function(err,data) {
            if (err) {
                if (cb) cb(err);
                return;
            }
            if (cb) cb(err,data);
            dispatch(actions.load_user_data());
        }.bind(this));
    }
}

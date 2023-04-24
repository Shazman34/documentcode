
module.exports=function(state, action) {
    console.log("##################################");
    console.log("reducer",state,action);
    if (state==null) {
        return {prev_prices:{},price_dirs:{}};
    }
    var new_state=$.extend(true,{},state);
    switch (action.type) {
        case "GOT_PRICES":
            new_state.prices=action.prices;
            if (state.prices) {
                for (var n in new_state.prices) {
                    var new_p=new_state.prices[n];
                    var prev_p=state.prices[n];
                    if (new_p!=prev_p) {
                        new_state.prev_prices[n]=prev_p;
                        if (new_p>prev_p) {
                            new_state.price_dirs[n]="up";
                        } else {
                            new_state.price_dirs[n]="down";
                        }
                    }
                }
            }
            break;
        case "USER_DATA_LOADED":
            new_state.user_data=action.user_data;
            break;
        case "LOGOUT":
            delete new_state.user_data;
            break;
    }
    console.log("new_state",new_state);
    return new_state;
}

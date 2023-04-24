/** @jsx React.DOM */
'use strict'

var React = require('react')
var connect = require("react-redux").connect
var RPC = require('../RPC')
var actions = require("../actions")

var Login = React.createClass({
    getInitialState: function() {
        return {};
    },

    render: function() {
        console.log("Deposit.render");
        var currency=this.props.params.currency;
        if (this.props.user_data && !this.state.data) {
            var acc_id=this.props.user_data.xb_account_id;
            RPC.execute("xb.account","read",[[acc_id],["address_xbt_id"]],{},function(err,data) {
                if (err) {
                    alert("Failed to read account data");
                    return;
                }
                this.setState({data: data[0]});
            }.bind(this));
        }
        if (!this.state.data) return <p>Loading...</p>
        if (currency=="xbt") {
            var address=this.state.data.address_xbt_id?this.state.data.address_xbt_id[1]:null;
        } else {
            throw "Invalid currency";
        }
        var amount=parseFloat(this.state.amount);
        return <div>
            <div className="page-header">
                <h3>Deposit</h3>
            </div>
            <form className="form-horizontal">
                <div className="form-group">
                    <label className="col-sm-2 control-label">Currency</label>
                    <div className="col-sm-10">
                        XBT
                    </div>
                </div>
                <div className="form-group">
                    <label className="col-sm-2 control-label">Address</label>
                    <div className="col-sm-10">
                        {address?address:"You don't have any address yet"}
                        <a href="#" style={{marginLeft: 20}} onClick={this.new_address}><span className="glyphicon glyphicon-plus-sign"></span> Generate new address</a>
                    </div>
                </div>
                <div className="form-group">
                    <label className="col-sm-2 control-label">Amount (Optional)</label>
                    <div className="col-sm-10">
                        <input type="text" className="form-control" placeholder="Amount" value={this.state.amount} onChange={this.onchange_amount}/>
                    </div>
                </div>
                <div className="form-group">
                    <label className="col-sm-2 control-label">QR Code</label>
                    <div className="col-sm-10">
                        {function() {
                            if (!address) return;
                            if (amount)
                                return <img src={"https://chart.googleapis.com/chart?chs=250x250&cht=qr&chl=bitcoin:"+address+"?amount="+amount}/>
                            else
                                return <img src={"https://chart.googleapis.com/chart?chs=250x250&cht=qr&chl="+address}/>
                        }.bind(this)()}
                    </div>
                </div>
            </form>
        </div>
    },

    onchange_amount: function(e) {
        this.setState({amount:e.target.value});
    },

    new_address: function(e) {
        e.preventDefault();
        this.props.dispatch(actions.new_address(this.props.params.currency,function() {
            this.setState({data:null});
        }.bind(this)));
    },
})

var select=function(state) {
    return {
        user_data: state.user_data,
    }
}

module.exports=connect(select)(Login);

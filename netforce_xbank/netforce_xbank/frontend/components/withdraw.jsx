/** @jsx React.DOM */
'use strict'

var React = require('react')
var connect = require("react-redux").connect
var RPC = require('../RPC')
var actions = require("../actions")
var fmt_money=require("../utils").fmt_money;

var Withdraw = React.createClass({
    getInitialState: function() {
        return {step:0};
    },

    render: function() {
        console.log("Withdraw.render");
        if (this.state.step==0) {
            return <div>
                <div className="page-header">
                    <h3>Withdraw</h3>
                </div>
                <form className="form-horizontal">
                    <div className="form-group">
                        <label className="col-sm-2 control-label">Currency</label>
                        <div className="col-sm-10">
                            XBT
                        </div>
                    </div>
                    <div className="form-group">
                        <label className="col-sm-2 control-label">Amount</label>
                        <div className="col-sm-10">
                            <input type="text" className="form-control" placeholder="Amount" value={this.state.amount} onChange={this.onchange_amount}/>
                        </div>
                    </div>
                    <div className="form-group">
                        <label className="col-sm-2 control-label">Address</label>
                        <div className="col-sm-10">
                            <input type="text" className="form-control" placeholder="Address" value={this.state.address} onChange={this.onchange_address}/>
                        </div>
                    </div>
                    <div className="form-group">
                        <div className="col-sm-10 col-sm-offset-2">
                            <button type="submit" className="btn btn-primary btn-lg" onClick={this.onclick_withdraw}>Withdraw</button>
                        </div>
                    </div>
                </form>
            </div>
        } else if (this.state.step==1) {
            return <div>
                <div className="page-header">
                    <h3>Confirm Withdrawal</h3>
                </div>
                <form className="form-horizontal">
                    <div className="form-group">
                        <label className="col-sm-2 control-label">Currency</label>
                        <div className="col-sm-10">
                            XBT
                        </div>
                    </div>
                    <div className="form-group">
                        <label className="col-sm-2 control-label">Amount</label>
                        <div className="col-sm-10">
                            {fmt_money(this.state.amount,8)}
                        </div>
                    </div>
                    <div className="form-group">
                        <label className="col-sm-2 control-label">Address</label>
                        <div className="col-sm-10">
                            {this.state.address}
                        </div>
                    </div>
                    <div className="form-group">
                        <div className="col-sm-10 col-sm-offset-2">
                            <button type="submit" className="btn btn-success btn-lg" onClick={this.onclick_confirm}><span className="glyphicon glyphicon-ok"></span> Confirm</button>
                            <button type="submit" className="btn btn-lg" onClick={this.onclick_back}><span className="glyphicon glyphicon-arrow-left"></span> Back</button>
                        </div>
                    </div>
                </form>
            </div>
        }
    },

    onchange_amount: function(e) {
        this.setState({
            amount: e.target.value,
        });
    },

    onchange_address: function(e) {
        this.setState({
            address: e.target.value,
        });
    },

    onclick_withdraw: function(e) {
        e.preventDefault();
        var amount=parseFloat(this.state.amount);
        if (!amount) {
            alert("Amount can not be empty");
            return;
        }
        var address=this.state.address;
        if (!address) {
            alert("Address can not be empty");
            return;
        }
        this.setState({
            amount: amount,
            address: address,
            step: 1,
        });
    },

    onclick_confirm: function(e) {
        e.preventDefault();
        this.props.dispatch(actions.withdraw("xbt",this.state.amount,this.state.address,function(err,data) {
            if (err) {
                alert("Withdrawal failed");
                this.setState({
                    step: 0,
                });
                return;
            }
            alert("Withdrawal successful: "+data.number);
            window.location="/account";
        }.bind(this)));
    },

    onclick_back: function(e) {
        e.preventDefault();
        this.setState({
            step: 0,
        });
    },
})

module.exports=connect()(Withdraw);

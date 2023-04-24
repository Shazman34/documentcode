/** @jsx React.DOM */
'use strict'

var React = require('react')
var connect = require("react-redux").connect
var RPC = require('../RPC')
var actions = require("../actions")
var Link = require("react-router").Link;
var fmt_money=require("../utils").fmt_money;

var Transactions = React.createClass({
    getInitialState: function() {
        return {};
    },

    render: function() {
        console.log("Transactions.render");
        if (this.props.user_data && !this.state.data) {
            var acc_id=this.props.user_data.xb_account_id;
            RPC.execute("xb.transaction","search_read",[[["account_id","=",acc_id]],["hash","currency","address","date","amount","balance","num_conf"]],{},function(err,data) {
                this.setState({data: data});
            }.bind(this));
        }
        if (this.state.data==null) return <p>Loading...</p>
        if (this.state.data.length==0) return <p>There are no transactions yet.</p >
        return <div>
            <table className="table">
                <thead>
                    <tr>
                        <th>Currency</th>
                        <th>Address</th>
                        <th>Date</th>
                        <th>Amount</th>
                        <th>Balance</th>
                        <th>Confirmations</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody>
                    {this.state.data.map(function(obj) {
                        return <tr>
                            <td>{obj.currency}</td>
                            <td>{obj.address}</td>
                            <td>{obj.date}</td>
                            <td>{fmt_money(obj.amount,8)}</td>
                            <td>{fmt_money(obj.balance,8)}</td>
                            <td>{obj.num_conf}</td>
                            <td>
                                {function() {
                                    if (obj.currency=="xbt")
                                        return <a href={"https://blockchain.info/tx/"+obj.hash}><span className="glyphicon glyphicon-arrow-right"></span> Verify</a>
                                }.bind(this)()}
                            </td>
                        </tr>
                    }.bind(this))}
                </tbody>
            </table>
        </div>
    }
})

var select=function(state) {
    return {
        user_data: state.user_data,
    }
}

module.exports=connect(select)(Transactions);

/** @jsx React.DOM */
'use strict'

var React = require('react')
var connect = require("react-redux").connect
var RPC = require('../RPC')
var actions = require("../actions")
var Link = require("react-router").Link;
var fmt_money=require("../utils").fmt_money;

var Addresses = React.createClass({
    getInitialState: function() {
        return {};
    },

    render: function() {
        console.log("Addresses.render");
        if (this.props.user_data && !this.state.data) {
            var acc_id=this.props.user_data.xb_account_id;
            RPC.execute("xb.address","search_read",[[["account_id","=",acc_id]],["currency","address","balance0"]],{},function(err,data) {
                this.setState({data: data});
            }.bind(this));
        }
        if (this.state.data==null) return <p>Loading...</p>
        if (this.state.data.length==0) return <p>There are no addresses yet.</p>
        return <div>
            <table className="table">
                <thead>
                    <tr>
                        <th>Currency</th>
                        <th>Address</th>
                        <th>Balance</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody>
                    {this.state.data.map(function(obj) {
                        if (!obj.balance0) return;
                        return <tr>
                            <td>{obj.currency}</td>
                            <td>{obj.address}</td>
                            <td>{fmt_money(obj.balance0,8)}</td>
                            <td>
                                {function() {
                                    if (obj.currency=="xbt")
                                        return <a href={"https://blockchain.info/address/"+obj.address}><span className="glyphicon glyphicon-arrow-right"></span> Verify</a>
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

module.exports=connect(select)(Addresses);

/** @jsx React.DOM */
'use strict'

var React = require('react')
var connect = require("react-redux").connect
var RPC = require('../RPC')
var actions = require("../actions")
var Link = require("react-router").Link;
var fmt_money=require("../utils").fmt_money;

var Balances = React.createClass({
    getInitialState: function() {
        return {};
    },

    render: function() {
        console.log("Account.render");
        if (this.props.user_data && !this.state.data) {
            var acc_id=this.props.user_data.xb_account_id;
            RPC.execute("xb.account","read",[[acc_id],["balance_xbt","balance_ltc","balance_eth"]],{},function(err,data) {
                this.setState({data: data[0]});
            }.bind(this));
        }
        if (this.state.data) {
            return <div>
                <h3>Fiat Balance</h3>
                <table className="table">
                    <thead>
                        <tr>
                            <th></th>
                            <th>Balance</th>
                            <th>In Orders</th>
                            <th>Total</th>
                            <th style={{width:"300px"}}></th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>THB</td>
                            <td>0.00</td>
                            <td>0.00</td>
                            <td>0.00</td>
                            <td>
                                <Link to="deposit/thb" className="btn btn-primary btn-lg">Deposit</Link>
                                &nbsp;
                                &nbsp;
                                <Link to="withdraw/thb" className="btn btn-primary btn-lg">Withdraw</Link>
                            </td>
                        </tr>
                    </tbody>
                </table>
                <h3>Crypto Balance</h3>
                <table className="table">
                    <thead>
                        <tr>
                            <th></th>
                            <th>Balance</th>
                            <th>In Orders</th>
                            <th>Total</th>
                            <th style={{width:"300px"}}></th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>XBT</td>
                            <td>{fmt_money(this.state.data.balance_xbt,8)}</td>
                            <td>0.00000000</td>
                            <td>{fmt_money(this.state.data.balance_xbt,8)}</td>
                            <td>
                                <Link to="deposit/xbt" className="btn btn-primary btn-lg">Deposit</Link>
                                &nbsp;
                                &nbsp;
                                <Link to="withdraw/xbt" className="btn btn-primary btn-lg">Withdraw</Link>
                            </td>
                        </tr>
                        <tr>
                            <td>LTC</td>
                            <td>{fmt_money(this.state.data.balance_ltc,8)}</td>
                            <td>0.00000000</td>
                            <td>{fmt_money(this.state.data.balance_ltc,8)}</td>
                            <td>
                                <Link to="deposit/ltc" className="btn btn-primary btn-lg">Deposit</Link>
                                &nbsp;
                                &nbsp;
                                <Link to="withdraw/ltc" className="btn btn-primary btn-lg">Withdraw</Link>
                            </td>
                        </tr>
                        <tr>
                            <td>ETH</td>
                            <td>{fmt_money(this.state.data.balance_eth,8)}</td>
                            <td>0.00000000</td>
                            <td>{fmt_money(this.state.data.balance_ltc,8)}</td>
                            <td>
                                <Link to="deposit/eth" className="btn btn-primary btn-lg">Deposit</Link>
                                &nbsp;
                                &nbsp;
                                <Link to="withdraw/eth" className="btn btn-primary btn-lg">Withdraw</Link>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        } else {
            return <p>Loading...</p>
        }
    }
})

var select=function(state) {
    return {
        user_data: state.user_data,
    }
}

module.exports=connect(select)(Balances);

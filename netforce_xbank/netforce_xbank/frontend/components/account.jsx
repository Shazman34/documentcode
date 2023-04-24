/** @jsx React.DOM */
'use strict'

var React = require('react')
var connect = require("react-redux").connect
var RPC = require('../RPC')
var actions = require("../actions")
var Link = require("react-router").Link;
var fmt_money=require("../utils").fmt_money;
var Balances=require("./balances")
var Transactions=require("./transactions")
var Addresses=require("./addresses")
var classnames=require("classnames")

var Account = React.createClass({
    getInitialState: function() {
        return {cur_tab:0};
    },

    render: function() {
        console.log("Account.render");
        return <div>
            <ul className="nav nav-tabs" style={{marginBottom:20}}>
              <li className={classnames({active:this.state.cur_tab==0})} onClick={this.click_tab.bind(this,0)}><a href="#">Balances</a></li>
              <li className={classnames({active:this.state.cur_tab==1})} onClick={this.click_tab.bind(this,1)}><a href="#">Transactions</a></li>
              <li className={classnames({active:this.state.cur_tab==2})} onClick={this.click_tab.bind(this,2)}><a href="#">Addresses</a></li>
            </ul>
            {function() {
                if (this.state.cur_tab==0) {
                    return <Balances/>
                } else if (this.state.cur_tab==1) {
                    return <Transactions/>
                } else if (this.state.cur_tab==2) {
                    return <Addresses/>
                }
            }.bind(this)()}
        </div>
    },

    click_tab: function(tab_no) {
        this.setState({cur_tab:tab_no});
    }
})

var select=function(state) {
    return {
        user_data: state.user_data,
    }
}

module.exports=connect(select)(Account);

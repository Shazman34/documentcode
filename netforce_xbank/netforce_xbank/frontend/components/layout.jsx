/** @jsx React.DOM */
'use strict'

var React = require('react')
var connect = require("react-redux").connect
var RPC = require('../RPC')
var moment = require('moment')
var actions = require("../actions")
var Link = require("react-router").Link;

var Layout = React.createClass({
    contextTypes: {
        history: React.PropTypes.object
    },

    render: function() {
        console.log("Layout.render");
        return <div>
            <nav className="navbar navbar-default">
                <div className="container-fluid">
                    <div className="navbar-header">
                        <a className="navbar-brand" href="/"><span style={{color:"red",fontWeight:"bold"}}>X</span><span style={{color:"#111",fontWeight:"bold"}}>Bank</span></a>
                    </div>
                    <ul className="nav navbar-nav">
                        <li className={this.context.history.isActive("market")?"active":""}><Link to="market">Buy / Sell</Link></li>
                        {function() {
                            if (this.props.user_data)
                                return <li className={this.context.history.isActive("account")?"active":""}><Link to="account">Account</Link></li>
                        }.bind(this)()}
                    </ul>
                    <ul className="nav navbar-nav navbar-right">
                        {function() {
                            if (!this.props.user_data)
                                return <li className={this.context.history.isActive("register")?"active":""}><Link to="register">Sign Up</Link></li>
                        }.bind(this)()}
                        {function() {
                            if (!this.props.user_data)
                                return <li className={this.context.history.isActive("login")?"active":""}><Link to="login">Login</Link></li>
                        }.bind(this)()}
                        {function() {
                            if (this.props.user_data)
                                return <li><a href="#" onClick={this.logout}>Logout</a></li>
                        }.bind(this)()}
                    </ul>
                </div>
            </nav>
            {this.props.children}
            <div style={{textAlign:"center",fontSize:11,color:"#999",borderTop:"1px solid #ccc",paddingTop:8,marginTop:18,paddingBottom:20}}>
                &copy; 2016 Netforce Co. Ltd.
            </div>
        </div>
    },

    logout: function(e) {
        e.preventDefault();
        this.props.dispatch(actions.logout());
    }
})

var select=function(state) {
    return {
        user_data: state.user_data,
    }
}

module.exports=connect(select)(Layout);

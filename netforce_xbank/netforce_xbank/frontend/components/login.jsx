/** @jsx React.DOM */
'use strict'

var React = require('react')
var connect = require("react-redux").connect
var RPC = require('../RPC')
var actions = require("../actions")

var Login = React.createClass({
    render: function() {
        console.log("Login.render");
        return <div>
            <div className="page-header">
                <h3>Login</h3>
            </div>
            <form className="form-horizontal">
                <div className="form-group">
                    <label className="col-sm-2 control-label">Email</label>
                    <div className="col-sm-4">
                        <input type="email" className="form-control" placeholder="Email" ref="email"/>
                    </div>
                </div>
                <div className="form-group">
                    <label className="col-sm-2 control-label">Password</label>
                    <div className="col-sm-4">
                        <input type="password" className="form-control" placeholder="Password" ref="password"/>
                    </div>
                </div>
                <div className="form-group">
                    <div className="col-sm-4 col-sm-offset-2">
                        <button type="submit" className="btn btn-primary btn-lg" onClick={this.login}>Login</button>
                    </div>
                </div>
            </form>
        </div>
    },

    login: function(e) {
        console.log("login");
        e.preventDefault();
        var email=this.refs.email.value;
        var password=this.refs.password.value;
        this.props.dispatch(actions.login(email,password));
    }
})

module.exports=connect()(Login);

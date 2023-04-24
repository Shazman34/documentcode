/** @jsx React.DOM */
'use strict'

var React = require('react')
var connect = require("react-redux").connect
var RPC = require('../RPC')
var actions = require("../actions")
var utils = require("../utils")

var Register = React.createClass({
    getInitialState: function() {
        return {};
    },

    render: function() {
        console.log("Register.render");
        return <div>
            <div className="page-header">
                <h3>Sign Up</h3>
            </div>
            <form className="form-horizontal">
                <div className="form-group">
                    <label className="col-sm-2 control-label">Email</label>
                    <div className="col-sm-4">
                        <input type="email" className="form-control" placeholder="Email" ref="email"/>
                    </div>
                </div>
                <div className="form-group" id="pw-container">
                    <label className="col-sm-2 control-label">Password</label>
                    <div className="col-sm-4">
                        <input type="password" className="form-control" placeholder="Password" ref="password"/>
                    </div>
                    <div className="col-sm-6 pw-progress"></div>
                </div>
                <div className="form-group">
                    <div className="col-sm-10 col-sm-offset-2">
                        <button type="submit" className="btn btn-primary btn-lg" onClick={this.register}>Sign Up</button>
                    </div>
                </div>
            </form>
        </div>
    },

    componentDidMount: function() {
        console.log("register.componentDidMount");
        var opts={
            ui: {
                container: "#pw-container",
                showVerdictsInsideProgressBar: true,
                viewports: {
                    progress: ".pw-progress",
                }
            },
            common: {
                onKeyUp: function(e,data) {
                    this.setState({score:data.score,level:data.verdictLevel});
                }.bind(this),
            }
        };
        $(":password").pwstrength(opts);
    },

    register: function(e) {
        console.log("register");
        e.preventDefault();
        try {
            var email=this.refs.email.value;
            if (!email) throw "Missing email";
            if (!utils.check_email(email)) throw "Invalid email";
            var password=this.refs.password.value;
            if (!password) throw "Missing password";
            if (this.state.level<1) throw "Password is too weak";
            var name=email;
        } catch (err) {
            alert(err);
            return;
        }
        this.props.dispatch(actions.register(name,email,password));
    },
})

var select=function(state) {
    return {
    }
}

module.exports=connect(select)(Register);

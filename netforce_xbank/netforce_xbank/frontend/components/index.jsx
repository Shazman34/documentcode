/** @jsx React.DOM */
'use strict'

var React = require('react')
var Router=require('react-router').Router
var Route=require('react-router').Route
var IndexRoute=require('react-router').IndexRoute
var Layout = require('./layout')
var Market = require('./market')
var Register = require('./register')
var Login = require('./login')
var Account = require('./account')
var Deposit = require('./deposit')
var Withdraw = require('./withdraw')

var createBrowserHistory = require('history/lib/createBrowserHistory')
const history = createBrowserHistory()

var Index = React.createClass({
    render: function() {
        return <Router history={history}>
            <Route path="/" component={Layout}>
                <IndexRoute path="market" component={Market}/>
                <Route path="market" component={Market}/>
                <Route path="account" component={Account}/>
                <Route path="register" component={Register}/>
                <Route path="login" component={Login}/>
                <Route path="deposit/:currency" component={Deposit}/>
                <Route path="withdraw/:currency" component={Withdraw}/>
            </Route>
        </Router>
    },
})

module.exports = Index;

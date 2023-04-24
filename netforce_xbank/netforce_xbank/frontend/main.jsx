/** @jsx React.DOM */
'use strict'

var ReactDOM = require('react-dom')
var React = require('react')
var Index = require('./components/index')
var createStore = require("redux").createStore
var applyMiddleware = require("redux").applyMiddleware
var Provider = require("react-redux").Provider
var thunkMiddleware = require("redux-thunk")
var reducer = require("./reducers")
var actions = require("./actions")
var i18n = require("./i18n")

var createStoreWithMiddleware=applyMiddleware(thunkMiddleware)(createStore);
var store=createStoreWithMiddleware(reducer);

var user_id=parseInt(localStorage.user_id);
if (user_id) {
    store.dispatch(actions.load_user_data());
}

ReactDOM.render( <Provider store={store}><Index/></Provider> , document.getElementById('content'))

setInterval(function() {
    store.dispatch(actions.get_prices());
},5000);

setInterval(function() {
    store.dispatch(actions.get_price_chart());
},60000);

/** @jsx React.DOM */
'use strict'

var React = require('react')
var connect = require("react-redux").connect
var RPC = require('../RPC')
var moment = require('moment')
var actions = require("../actions")
var classNames=require("classnames");
var PlaceOrder=require("./place_order");
var fmt_money=require("../utils").fmt_money;

var Market = React.createClass({
    getInitialState: function() {
        return {};
    },

    componentDidMount: function() {
        console.log("Market.componentDidMount",this);
        this.props.dispatch(actions.get_prices());
        this.props.dispatch(actions.get_price_chart());
    },

    render: function() {
        console.log("Market.render");
        return <div>
            <div className="row">
                <div className="col-md-6">
                    <div className="btn-group btn-group-sm" role="group">
                      <button type="button" className="btn btn-default active">Day</button>
                      <button type="button" className="btn btn-default">Week</button>
                      <button type="button" className="btn btn-default">Month</button>
                      <button type="button" className="btn btn-default">Year</button>
                    </div>
                    <div id="xb-price-chart"></div>
                </div>
                <div className="col-md-6">
                    <table className="table table-bordered xb-price-table">
                        <thead>
                            <tr>
                                <th>Product</th>
                                <th>Sell</th>
                                <th>Buy</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td className="xb-product">XBT / THB</td>
                                <td>
                                    <a href="#" className={classNames({"xb-price-big":true,"xb-price-up":this.props.price_dirs.btc_thb_bid=="up","xb-price-down":this.props.price_dirs.btc_thb_bid=="down"})} onClick={this.show_place_order.bind(this,"sell")}>
                                        {this.props.prices?fmt_money(this.props.prices.btc_thb_bid,0):"-"}
                                    </a>
                                </td>
                                <td>
                                    <a href="#" className={classNames({"xb-price-big":true,"xb-price-up":this.props.price_dirs.btc_thb_ask=="up","xb-price-down":this.props.price_dirs.btc_thb_ask=="down"})} onClick={this.show_place_order.bind(this,"buy")}>
                                        {this.props.prices?fmt_money(this.props.prices.btc_thb_ask,0):"-"}
                                    </a>
                                </td>
                            </tr>
                            <tr>
                                <td className="xb-product">LTC / THB</td>
                                <td>
                                    <a href="#" className={classNames({"xb-price-big":true,"xb-price-up":this.props.price_dirs.ltc_thb_bid=="up","xb-price-down":this.props.price_dirs.ltc_thb_bid=="down"})} onClick={this.show_place_order.bind(this,"sell")}>
                                        {this.props.prices?fmt_money(this.props.prices.ltc_thb_bid,2):"-"}
                                    </a>
                                </td>
                                <td>
                                    <a href="#" className={classNames({"xb-price-big":true,"xb-price-up":this.props.price_dirs.ltc_thb_ask=="up","xb-price-down":this.props.price_dirs.ltc_thb_ask=="down"})} onClick={this.show_place_order.bind(this,"buy")}>
                                        {this.props.prices?fmt_money(this.props.prices.ltc_thb_ask,2):"-"}
                                    </a>
                                </td>
                            </tr>
                            <tr>
                                <td className="xb-product">ETH / THB</td>
                                <td>
                                    <a href="#" className={classNames({"xb-price-big":true,"xb-price-up":this.props.price_dirs.eth_thb_bid=="up","xb-price-down":this.props.price_dirs.eth_thb_bid=="down"})} onClick={this.show_place_order.bind(this,"sell")}>
                                        {this.props.prices?fmt_money(this.props.prices.eth_thb_bid,2):"-"}
                                    </a>
                                </td>
                                <td>
                                    <a href="#" className={classNames({"xb-price-big":true,"xb-price-up":this.props.price_dirs.eth_thb_ask=="up","xb-price-down":this.props.price_dirs.eth_thb_ask=="down"})} onClick={this.show_place_order.bind(this,"buy")}>
                                        {this.props.prices?fmt_money(this.props.prices.eth_thb_ask,2):"-"}
                                    </a>
                                </td>
                            </tr>
                            <tr>
                                <td className="xb-product">LTC / XBT</td>
                                <td>
                                    <a href="#" className={classNames({"xb-price-big":true,"xb-price-up":this.props.price_dirs.ltc_xbt_bid=="up","xb-price-down":this.props.price_dirs.ltc_xbt_bid=="down"})} onClick={this.show_place_order.bind(this,"sell")}>
                                        {this.props.prices?fmt_money(this.props.prices.ltc_xbt_bid,5):"-"}
                                    </a>
                                </td>
                                <td>
                                    <a href="#" className={classNames({"xb-price-big":true,"xb-price-up":this.props.price_dirs.ltc_xbt_ask=="up","xb-price-down":this.props.price_dirs.ltc_xbt_ask=="down"})} onClick={this.show_place_order.bind(this,"buy")}>
                                        {this.props.prices?fmt_money(this.props.prices.ltc_xbt_ask,5):"-"}
                                    </a>
                                </td>
                            </tr>
                            <tr>
                                <td className="xb-product">ETH / XBT</td>
                                <td>
                                    <a href="#" className={classNames({"xb-price-big":true,"xb-price-up":this.props.price_dirs.eth_xbt_bid=="up","xb-price-down":this.props.price_dirs.eth_xbt_bid=="down"})} onClick={this.show_place_order.bind(this,"sell")}>
                                        {this.props.prices?fmt_money(this.props.prices.eth_xbt_bid,5):"-"}
                                    </a>
                                </td>
                                <td>
                                    <a href="#" className={classNames({"xb-price-big":true,"xb-price-up":this.props.price_dirs.eth_xbt_ask=="up","xb-price-down":this.props.price_dirs.eth_xbt_ask=="down"})} onClick={this.show_place_order.bind(this,"buy")}>
                                        {this.props.prices?fmt_money(this.props.prices.eth_xbt_ask,5):"-"}
                                    </a>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                    {this.props.prices?<p className="xb-price-time">Prices last updated: {this.props.prices.time}</p>:null}
                    <PlaceOrder order_type={this.state.order_type} show={this.state.show_place_order} on_hide={this.hide_place_order}/>
                </div>
            </div>
        </div>
    },

    show_place_order: function(order_type) {
        console.log("show_place_order");
        this.setState({order_type: order_type, show_place_order: true});
    },

    hide_place_order: function() {
        console.log("hide_place_order");
        this.setState({show_place_order: false});
    },
})

var select=function(state) {
    return {
        prices: state.prices,
        price_dirs: state.price_dirs,
    }
}

module.exports=connect(select)(Market);

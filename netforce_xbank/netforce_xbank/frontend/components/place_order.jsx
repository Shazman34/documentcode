/** @jsx React.DOM */
'use strict'

var React = require('react')
var connect = require("react-redux").connect
var RPC = require('../RPC')
var moment = require('moment')
var actions = require("../actions")

var PlaceOrder = React.createClass({
    getInitialState: function() {
        return {
            qty: 0,
        }
    },

    componentDidUpdate: function() {
        if (this.props.show) {
            $(this.refs.modal).modal("show");
            $(this.refs.modal).on('hidden.bs.modal', this.props.on_hide);
        }
    },

    render: function() {
        console.log("PlaceOrder.render");
        if (!this.props.show) return null;
        var price;
        if (this.props.order_type=="buy") {
            price=this.props.prices["btc_thb_ask"];
        } else if (this.props.order_type=="sell") {
            price=this.props.prices["btc_thb_bid"];
        } else {
            throw "Invalid order type";
        }
        var amount=Math.ceil(price*this.state.qty)||null;
        return <div className="modal" ref="modal">
            <div className="modal-dialog">
                <div className="modal-content">
                    <div className="modal-header">
                        <button type="button" className="close" data-dismiss="modal"><span>&times;</span></button>
                        <h4 className="modal-title">Place Order</h4>
                    </div>
                    <div className="modal-body">
                        <form className="form-horizontal">
                            <div className="form-group">
                                <label className="col-sm-4 control-label">Product</label>
                                <div className="col-sm-6">
                                    XBT / THB
                                </div>
                            </div>
                            <div className="form-group">
                                <label className="col-sm-4 control-label">Order Type</label>
                                <div className="col-sm-6">
                                    {this.props.order_type=="buy"?"Buy":"Sell"}
                                </div>
                            </div>
                            <div className="form-group">
                                <label className="col-sm-4 control-label">Price</label>
                                <div className="col-sm-6">
                                    {price}
                                </div>
                            </div>
                            <div className="form-group">
                                <label className="col-sm-4 control-label">Qty</label>
                                <div className="col-sm-6">
                                    <input type="text" className="form-control xb-input-qty" onChange={this.onchange_qty}/>
                                </div>
                            </div>
                            <div className="form-group">
                                <label className="col-sm-4 control-label">Amount</label>
                                <div className="col-sm-6">
                                    {amount}
                                </div>
                            </div>
                        </form>
                    </div>
                    <div className="modal-footer">
                        <button type="button" className="btn btn-default" data-dismiss="modal">Close</button>
                        <button type="button" className="btn btn-primary">Place Order</button>
                    </div>
                </div>
            </div>
        </div>
    },

    onchange_qty: function(e) {
        console.log("onchange_qty");
        this.setState({qty:parseFloat(e.target.value)});
    },
});

var select=function(state) {
    return {
        prices: state.prices,
    }
}

module.exports=connect(select)(PlaceOrder);

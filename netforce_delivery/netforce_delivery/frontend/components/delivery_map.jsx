var React = require('react')
var ReactDom = require('react-dom')
var moment = require('moment')
var classnames = require('classnames')
var $=require("jquery");
var _=require("underscore");
var rpc=require("netforce_ui_web/rpc");
var views=require("netforce_ui_web/views");

function DriverMarker(latlng, map, args) {
    this.latlng = latlng;   
    this.args = args;   
    this.setMap(map);   
}

DriverMarker.prototype = new google.maps.OverlayView();

DriverMarker.prototype.draw = function() {
    
    var self = this;
    
    var div = this.div;
    
    if (!div) {
    
        div = this.div = document.createElement('div');
        
        div.className = 'marker';
        
        div.style.position = 'absolute';
        div.style.cursor = 'pointer';

        $(div).append('<div style="font-size:12px;font-weight:bold;color:#333;text-align:center"><span style="background-color:white;padding:0px 2px">'+this.args.name+'</span></div>');
        if (this.args.loc) {
            $(div).append('<img src="'+require("../img/driver_32.png")+'"/>');
        } else {
            $(div).append('<img src="'+require("../img/driver_32_bw.png")+'"/>');
        }
        var bat=this.args.bat||0;
        var w=Math.floor(30*bat/100);
        var col;
        if (bat>50) col="#0f0";
        else if (bat>20) col="yellow";
        else if (bat>10) col="orange";
        else col="#f00";
        $(div).append('<div style="background:white;border:1px solid #666;width:30px;height:6px;margin-top:2px"><div style="height:4px;background-color:'+col+';width:'+w+'px"></div></div>');
        
        if (typeof(self.args.marker_id) !== 'undefined') {
            div.dataset.marker_id = self.args.marker_id;
        }
        
        google.maps.event.addDomListener(div, "click", function(event) {            
            google.maps.event.trigger(self, "click");
        });
        
        var panes = this.getPanes();
        panes.overlayImage.appendChild(div);
    }
    
    var point = this.getProjection().fromLatLngToDivPixel(this.latlng);
    
    if (point) {
        div.style.left = point.x + 'px';
        div.style.top = point.y + 'px';
    }
};

DriverMarker.prototype.remove = function() {
    if (this.div) {
        this.div.parentNode.removeChild(this.div);
        this.div = null;
    }   
};

DriverMarker.prototype.getPosition = function() {
    return this.latlng; 
};


var DeliveryMap = React.createClass({
    contextTypes: {
        history: React.PropTypes.object
    },

    getInitialState: function() {
        return {};
    },

    componentDidMount: function() {
        var opts={
        };
        var el=this.refs.map;
        var opts={
            //center: {lat: 13.7563, lng: 100.5018},
            center: {lat: 13.7563, lng: 100.6018},
            zoom: 11,
        };
        this.map = new google.maps.Map(el,opts);
        if (window.ds_interval) clearInterval(window.ds_interval);
        this.get_drivers(()=>{
            this.update_drivers();
        });
        window.ds_interval=setInterval(this.update_drivers.bind(this),5000);
        this.update_orders();
    },

    get_drivers: function(cb) {
        console.log("get_drivers");
        this.drivers={};
        rpc.execute("nd.driver","search_read",[[],["name","mobile"]],{},(err,data)=>{
            if (err) {
                alert("Error: "+err.message);
                return;
            }
            _.each(data,(o)=>{
                this.drivers[o.mobile]=true;
            });
            console.log("=> drivers",this.drivers);
            if (cb) cb();
        });
    },

    update_orders: function() {
        rpc.execute("nd.route","search_read_path",[[["state","in",["wait_depart","in_progress"]]],["state","orders.state","orders.sequence","orders.time_from","orders.time_to","orders.ship_address_id.coords","orders.customer_id.first_name","orders.ship_address_id.street_address"]],{},(err,data)=>{
            if (err) {
                alert("Failed to get data: "+err.message);
                return;
            }
            _.each(data,(route)=>{
                var path=[];
                _.each(route.orders,(order)=>{
                    if (!order.ship_address_id) return;
                    if (!order.ship_address_id.coords) return;
                    var r=order.ship_address_id.coords.split(",");
                    var pos={
                        lat: parseFloat(r[0]),
                        lng: parseFloat(r[1]),
                    };
                    var color;
                    if (order.state=="wait_pick") color="ff0000";
                    else if (order.state=="in_transit") color="0000ff";
                    else color="00ff00";
                    var title=(""+order.time_from+"-"+order.time_to)+", "+order.customer_id.first_name+", "+order.ship_address_id.street_address;
                    var marker=new google.maps.Marker({
                        position: pos,
                        map: this.map,
                        title: title,
                        icon: "http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld="+order.sequence+"|"+color+"|333333",
                    });
                    path.push(pos);
                });
                var color;
                if (route.state=="wait_depart") {
                    color="#cc0000";
                } else if (route.state=="in_progress") {
                    color="#0000cc";
                } else {
                    color="#00cc00";
                }
                var line=new google.maps.Polyline({
                    path: path,
                    geodesic: true,
                    strokeColor: color,
                    strokeOpacity: 1,
                    strokeWeight: 2,
                });
                line.setMap(this.map);
            });
        });
    },

    render: function() {
        console.log("Map.render");
        return <div>
            <div style={{height:500,marginTop:20}} ref="map"/>
            <div style={{marginTop:18}}>
                {function() {
                    if (this.state.active_drivers==null) return <p>Loading...</p>
                    return <p>
                        <span style={{marginRight:20}}>Status: {_.size(this.state.active_drivers)} active drivers</span>
                        {_.map(this.state.active_drivers,function(data,mobile) {
                            if (!this.drivers[mobile]) return;
                            return <span className={classnames("label",{"label-danger":data.loc!=null,"label-default":data.loc==null})} style={{marginLeft:5}}>
                                <a href="#" onClick={this.show_driver_info.bind(this,data)} style={{color:"#fff"}}>
                                    {data.name||"N/A"} ({data.bat}%)
                                    {function() {
                                        if (data.loc) return;
                                        return <span style={{marginLeft:5}}>[NO LOC, {data.cells?data.cells.length:"/"} cells]</span>
                                    }.bind(this)()}
                                </a>
                            </span>
                        }.bind(this))}
                    </p>
                }.bind(this)()}
            </div>
            {function() {
                if (this.state.show_track) return;
                return <button className="btn btn-default" onClick={this.show_track}><span className="glyphicon glyphicon-arrow-right"></span> Track Delivery</button>
            }.bind(this)()}
            {function() {
                if (!this.state.show_track) return;
                return <form className="form-inline">
                    <div className="form-group">
                        <input type="text" className="form-control" placeholder="Tracking Number"/>
                    </div>
                    <button className="btn btn-primary" style={{marginLeft:5}} onClick={this.do_track}>Track</button>
                    <button className="btn" onClick={this.hide_track} style={{marginLeft:5}}>Cancel</button>
                </form>
            }.bind(this)()}
        </div>
    },

    show_track: function(e) {
        e.preventDefault();
        this.setState({show_track: true});
    },

    hide_track: function(e) {
        e.preventDefault();
        this.setState({show_track: false});
    },

    do_track: function(e) {
        e.preventDefault();
        alert("This feature is not yet enabled!");
    },

    update_drivers: function() {
        console.log("update_drivers");
        var url="https://s3-ap-southeast-1.amazonaws.com/nfdelivery-carrier/active-drivers";
        $.ajax({
            url: url,
            dataType: "json",
            success: function(data) {
                console.log("got active drivers",data);
                this.setState({"active_drivers":data});
                _.each(this.markers,function(m) {
                    m.setMap(null);
                });
                this.markers=[];
                _.each(data,function(obj,mobile) {
                    var r;
                    if (!this.drivers[mobile]) return;
                    if (obj.loc) {
                        r=obj.loc.split(",");
                    } else if (obj.cell_loc) {
                        r=obj.cell_loc.split(",");
                    } else {
                        return;
                    }
                    var pos={
                        lat: parseFloat(r[0]),
                        lng: parseFloat(r[1]),
                    };
                    var title=obj.name||"N/A";
                    if (obj.bat) title+=" (bat "+obj.bat+"%)";
                    var latlng=new google.maps.LatLng(pos.lat,pos.lng);
                    var marker=new DriverMarker(latlng,this.map,obj);
                    this.markers.push(marker);
                }.bind(this));
            }.bind(this),
        });
    },

    show_driver_info(data,e) {
        e.preventDefault();
        alert(JSON.stringify(data));
        this.get_cell_pos(data);
    },

    get_cell_pos(info) {
        console.log("get_cell_pos",info);
        var api_key="AIzaSyAnOTbaAFeCz6YM_eIkv_oaHpc-eSsV8Ho";
        var url="https://www.googleapis.com/geolocation/v1/geolocate?key="+api_key;
        var data={
            cellTowers: [],
        };
        _.each(info.cells,function(cell) {
            var tower={};
            tower.cellId=cell.cid;
            tower.locationAreaCode=cell.lac;
            tower.mobileCountryCode=cell.mcc;
            tower.mobileNetworkCode=cell.mnc;
            tower.signalStrength=cell.dbm;
            data.cellTowers.push(tower);
        }.bind(this));
        console.log("data",data);
        $.post(url,data,function(res) {
            console.log("res",res);
            var loc=res.location;
            var lat=loc.lat;
            var lng=loc.lng;
            var acc=res.accurary;
            alert("lat="+lat+" lng="+lng+" acc="+acc);
        }.bin(this));
    },
})

module.exports=DeliveryMap;
views.register("delivery_map",DeliveryMap);

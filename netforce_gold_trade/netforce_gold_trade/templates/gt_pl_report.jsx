<div>
<center>
    <h2>
        Profit &amp; Loss Report
    </h2>
    <h3>
        From {data.date_from} to {data.date_to} 
    </h3>
</center>

<h3>Customer Trade</h3>
<table className="table table-bordered table-hover">
    <thead>
        <tr>
            <th>Type</th>
            <th>Avg Price</th>
            <th>Total Qty (bg)</th>
            <th>Total Qty (Kg)</th>
            <th>Total Amt</th>
            <th>P/L</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>We BUY 96</td>
            <td>{currency(data.cust_avg_96_sell)}</td>
            <td>{numeral(data.cust_qty_96_sell).format("0,0.000")}</td>
            <td>{numeral(data.cust_qty_96_sell/65.6).format("0,0.000")}</td>
            <td>{currency(data.cust_amt_96_sell)}</td>
            <td></td>
        </tr>
        <tr>
            <td>We SELL 96</td>
            <td>{currency(data.cust_avg_96_buy)}</td>
            <td>{numeral(data.cust_qty_96_buy).format("0,0.000")}</td>
            <td>{numeral(data.cust_qty_96_buy/65.6).format("0,0.000")}</td>
            <td>{currency(data.cust_amt_96_buy)}</td>
            <td></td>
        </tr>
        <tr>
            <td>We BUY 99</td>
            <td>{currency(data.cust_avg_99_sell)}</td>
            <td>{numeral(data.cust_qty_99_sell/65.6).format("0,0.000")}</td>
            <td>{numeral(data.cust_qty_99_sell).format("0,0.000")}</td>
            <td>{currency(data.cust_amt_99_sell)}</td>
            <td></td>
        </tr>
        <tr>
            <td>We SELL 99</td>
            <td>{currency(data.cust_avg_99_buy)}</td>
            <td>{numeral(data.cust_qty_99_buy/65.6).format("0,0.000")}</td>
            <td>{numeral(data.cust_qty_99_buy).format("0,0.000")}</td>
            <td>{currency(data.cust_amt_99_buy)}</td>
            <td></td>
        </tr>
        <tr>
            <td>Total</td>
            <td></td>
            <td>{numeral(data.cust_total_qty_bg).format("0,0.000")}</td>
            <td>{numeral(data.cust_total_qty_kg).format("0,0.000")}</td>
            <td>{currency(data.cust_total_amt)}</td>
            <td>{currency(data.cust_pl)}</td>
            <td></td>
        </tr>
    </tbody>
</table>

<h3>Supplier Trade</h3>
<table className="table table-bordered table-hover">
    <thead>
        <tr>
            <th>Type</th>
            <th>Avg Price</th>
            <th>Total Qty (bg)</th>
            <th>Total Qty (Kg)</th>
            <th>Total Amt</th>
            <th>P/L</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>We BUY 96</td>
            <td>{currency(data.sup_avg_96_buy)}</td>
            <td>{numeral(data.sup_qty_96_buy).format("0,0.000")}</td>
            <td>{numeral(data.sup_qty_96_buy/65.6).format("0,0.000")}</td>
            <td>{currency(data.sup_amt_96_buy)}</td>
            <td></td>
        </tr>
        <tr>
            <td>We SELL 96</td>
            <td>{currency(data.sup_avg_96_sell)}</td>
            <td>{numeral(data.sup_qty_96_sell).format("0,0.000")}</td>
            <td>{numeral(data.sup_qty_96_sell/65.6).format("0,0.000")}</td>
            <td>{currency(data.sup_amt_96_sell)}</td>
            <td></td>
        </tr>
        <tr>
            <td>We BUY 99</td>
            <td>{currency(data.sup_avg_99_buy)}</td>
            <td>{numeral(data.sup_qty_99_buy/65.6).format("0,0.000")}</td>
            <td>{numeral(data.sup_qty_99_buy).format("0,0.000")}</td>
            <td>{currency(data.sup_amt_99_buy)}</td>
            <td></td>
        </tr>
        <tr>
            <td>We SELL 99</td>
            <td>{currency(data.sup_avg_99_sell)}</td>
            <td>{numeral(data.sup_qty_99_sell/65.6).format("0,0.000")}</td>
            <td>{numeral(data.sup_qty_99_sell).format("0,0.000")}</td>
            <td>{currency(data.sup_amt_99_sell)}</td>
            <td></td>
        </tr>
        <tr>
            <td>Total</td>
            <td></td>
            <td>{numeral(data.sup_total_qty_bg).format("0,0.000")}</td>
            <td>{numeral(data.sup_total_qty_kg).format("0,0.000")}</td>
            <td>{currency(data.sup_total_amt)}</td>
            <td>{currency(data.sup_pl)}</td>
            <td></td>
        </tr>
    </tbody>
</table>

<h3>Combined Trade</h3>
<table className="table table-bordered table-hover">
    <thead>
        <tr>
            <th>Type</th>
            <th>Avg Price</th>
            <th>Total Qty (bg)</th>
            <th>Total Qty (Kg)</th>
            <th>Total Amt</th>
            <th>P/L</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>We BUY 96</td>
            <td>{currency(data.all_avg_96_buy)}</td>
            <td>{numeral(data.all_qty_96_buy).format("0,0.000")}</td>
            <td>{numeral(data.all_qty_96_buy/65.6).format("0,0.000")}</td>
            <td>{currency(data.all_amt_96_buy)}</td>
            <td></td>
        </tr>
        <tr>
            <td>We SELL 96</td>
            <td>{currency(data.all_avg_96_sell)}</td>
            <td>{numeral(data.all_qty_96_sell).format("0,0.000")}</td>
            <td>{numeral(data.all_qty_96_sell/65.6).format("0,0.000")}</td>
            <td>{currency(data.all_amt_96_sell)}</td>
            <td></td>
        </tr>
        <tr>
            <td>We BUY 99</td>
            <td>{currency(data.all_avg_99_buy)}</td>
            <td>{numeral(data.all_qty_99_buy/65.6).format("0,0.000")}</td>
            <td>{numeral(data.all_qty_99_buy).format("0,0.000")}</td>
            <td>{currency(data.all_amt_99_buy)}</td>
            <td></td>
        </tr>
        <tr>
            <td>We SELL 99</td>
            <td>{currency(data.all_avg_99_sell)}</td>
            <td>{numeral(data.all_qty_99_sell/65.6).format("0,0.000")}</td>
            <td>{numeral(data.all_qty_99_sell).format("0,0.000")}</td>
            <td>{currency(data.all_amt_99_sell)}</td>
            <td></td>
        </tr>
        <tr>
            <td>Total</td>
            <td></td>
            <td>{numeral(data.all_total_qty_bg).format("0,0.000")}</td>
            <td>{numeral(data.all_total_qty_kg).format("0,0.000")}</td>
            <td>{currency(data.all_total_amt)}</td>
            <td>{currency(data.all_pl)}</td>
            <td></td>
        </tr>
    </tbody>
</table>
</div>

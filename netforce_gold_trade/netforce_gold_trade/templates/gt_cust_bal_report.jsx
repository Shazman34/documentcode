<div>
<center>
    <h2>
        Customer Balance Report
    </h2>
    <h3>
        Customer: {data.cust_name} 
        <br/>
        Date: {data.date}
    </h3>
</center>

<table className="table table-hover table-bordered">
    <thead>
        <tr>
            <th>Time</th>
            <th>Ref</th>
            <th>Qty 96 In</th>
            <th>Qty 99 In</th>
            <th>THB In</th>
            <th>Qty 96 Out</th>
            <th>Qty 99 Out</th>
            <th>THB Out</th>
            <th>Balance 96</th>
            <th>Balance 99</th>
            <th>Balance THB</th>
        </tr>
    </thead>
    <tbody>
        {data.lines.map(l=>{
            return <tr>
                <td>{l.time}</td>
                <td><a href={l.link_url}>{l.ref}</a></td>
                <td>{l.qty_96>0?l.qty_96:null}</td>
                <td>{l.qty_99>0?l.qty_99:null}</td>
                <td>{l.amt>0?currency(l.amt):null}</td>
                <td>{l.qty_96<0?-l.qty_96:null}</td>
                <td>{l.qty_99<0?-l.qty_99:null}</td>
                <td>{l.amt<0?currency(-l.amt):null}</td>
                <td>{l.bal_qty_96}</td>
                <td>{l.bal_qty_99}</td>
                <td>{currency(l.bal_amt)}</td>
            </tr>
        })}
    </tbody>
</table>

</div>

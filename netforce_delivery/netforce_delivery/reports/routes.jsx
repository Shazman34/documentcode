<html>
<title>Delivery Routes</title>
<body>
{routes.map((r)=>{
    return <div>
        <h1>{r.carrier_id.name}-{r.delivery_date}-{r.round_id.period_id.name}</h1>
        <table>
            <thead>
                <th>#</th>
                <th>From Time</th>
                <th>To Time</th>
                <th>Cust. Code</th>
                <th>Cust. Name</th>
                <th>Street Address</th>
                <th>Instructions</th>
                <th>Products</th>
                <th>Arrival Time</th>
                <th>Returns</th>
            </thead>
            <tbody>
                {r.orders.map((o)=>{
                    return <tr>
                        <td>{o.sequence}</td>
                        <td>{o.time_from}</td>
                        <td>{o.time_to}</td>
                        <td>{o.location_id.cust_code}</td>
                        <td>{o.location_id.cust_name}</td>
                        <td>{o.location_id.street_address}</td>
                        <td>{o.location_id.instructions}</td>
                        <td>{o.item_desc}</td>
                        <td></td>
                        <td></td>
                    </tr>
                })}
            </tbody>
        </table>
    </div>
})}
</body>
</html>

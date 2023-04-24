<div>
<center>
<h2>Product Returns</h2>
</center>
{function() {
    if (customers.length==0) return <p>There are no items to display</p>;
    return <table className="table">
        <thead>
            <tr>
                <th>Customer Code</th>
                <th>Customer First Name</th>
                <th>Customer Last Name</th>
                <th>Product Name</th>
                <th>Delivered Qty</th>
                <th>Returned Qty</th>
                <th>Remaining Qty To Return</th>
            </tr>
        </thead>
        <tbody>
            {customers.map((c)=>{
                return c.products.map((p)=>{
                    return <tr>
                        <td><a href={"/action?name=nd_customer&mode=form&active_id="+c.id}>{c.code}</a></td>
                        <td>{c.first_name}</td>
                        <td>{c.last_name}</td>
                        <td>{p.name}</td>
                        <td>{p.out_qty}</td>
                        <td>{p.in_qty}</td>
                        <td><b>{p.bal_qty}</b></td>
                    </tr>
                });
            })}
        </tbody>
    </table>
}.bind(this)()}
</div>

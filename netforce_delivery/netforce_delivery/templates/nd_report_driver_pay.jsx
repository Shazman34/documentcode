<div>
<center>
<h2>Driver Payable</h2>
<h3>{date_from} to {date_to}</h3>
</center>
{function() {
    if (drivers.length==0) return <p>There are no items to display</p>;
    return <table className="table">
        <thead>
            <tr>
                <th>Driver Name</th>
                <th>Date</th>
                <th>Job Number</th>
                <th>Due Amount</th>
            </tr>
        </thead>
        <tbody>
            {drivers.map((d)=>{
                return [
                    <tr>
                        <td><b>{d.name}</b></td>
                        <td></td>
                        <td></td>
                        <td></td>
                    </tr>,
                    d.jobs.map((j)=>{
                        return <tr>
                            <td></td>
                            <td>{j.date}</td>
                            <td><a href={"/action?name=nd_job&mode=form&active_id="+j.id}>{j.number}</a></td>
                            <td>{j.amount_due}</td>
                        </tr>
                    }),
                    <tr>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td><b>Total: {d.amount_due_total}</b></td>
                    </tr>];
            })}
        </tbody>
    </table>
}.bind(this)()}
</div>

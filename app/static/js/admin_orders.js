async function loadOrders(){

const res = await fetch("/admin/orders")

const data = await res.json()

let html=""

data.forEach(o=>{

html+=`
<tr>

<td>${o.id}</td>
<td>${o.user}</td>
<td>${o.total}</td>

<td>${o.status}</td>

<td>

<select onchange="updateStatus(${o.id},this.value)">

<option>pending</option>
<option>shipping</option>
<option>completed</option>

</select>

</td>

</tr>
`

})

document.getElementById("orders_table").innerHTML=html

}

async function updateStatus(id,status){

await fetch(`/order/admin/${id}/update`,{
method:"POST",
headers:{
"Content-Type":"application/x-www-form-urlencoded"
},
body:`status=${status}`
})

}

loadOrders()
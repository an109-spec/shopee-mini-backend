async function loadDashboard(){

const res = await fetch("/admin/dashboard/data")

const data = await res.json()

document.getElementById("total_orders").innerText = data.total_orders
document.getElementById("monthly_revenue").innerText = data.monthly_revenue
document.getElementById("new_users").innerText = data.new_users

let html=""

data.top_products.forEach(p=>{
html+=`
<tr>
<td>${p.name}</td>
<td>${p.sold}</td>
</tr>
`
})

document.getElementById("top_products").innerHTML=html

}

loadDashboard()

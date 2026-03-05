async function loadProducts(){

const res = await fetch("/products")

const data = await res.json()

let html=""

data.items.forEach(p=>{

html+=`
<tr>
<td>${p.id}</td>
<td>${p.name}</td>
<td>${p.price}</td>
<td>${p.stock}</td>

<td>
<button onclick="deleteProduct(${p.id})">
Delete
</button>
</td>

</tr>
`

})

document.getElementById("product_table").innerHTML=html

}

async function deleteProduct(id){

await fetch("/products/"+id,{
method:"DELETE"
})

loadProducts()

}

loadProducts()
async function createVoucher(){
const code=document.getElementById("code").value
const type=document.getElementById("type").value
const value=document.getElementById("value").value
const quantity=document.getElementById("quantity").value
const min=document.getElementById("min").value
const expire=document.getElementById("expire").value
await fetch("/seller/api/voucher/create",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({
code:code,
discount_type:type,
discount_value:value,
quantity:quantity,
min_order:min,
expired_at:expire
})
})
location.reload()
}
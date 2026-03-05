const btn = document.getElementById("confirm-payment-btn")

if(btn){

btn.addEventListener("click",()=>{

const orderId = btn.dataset.order

fetch("/payment/confirm",{

method:"POST",
headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({
order_id:orderId
})

})
.then(res=>res.json())
.then(data=>{

if(data.success){
window.location.href="/payment/success/"+orderId
}

})

})

}
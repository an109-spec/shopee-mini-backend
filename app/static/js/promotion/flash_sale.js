
const flashInput = document.getElementById("flashPrice")
if(flashInput){
flashInput.addEventListener("input", function(){
const flash = this.value
if(!selectedVariantPrice) return
const percent = Math.round(
(1 - flash/selectedVariantPrice)*100
)
document.getElementById("discountPercentInput").value = percent
})
}

window.createFlashSale = async function(){
const variants = document.querySelectorAll(
"input[name='variant_ids[]']:checked"
)

if(variants.length === 0){
alert("Phải chọn ít nhất 1 phân loại")
return
}

const percent=document.getElementById("discountPercentInput").value
const stock=parseInt(document.getElementById("stock").value)

const start=document.querySelector("[name='start_time']").value
const end=document.querySelector("[name='end_time']").value

for(const v of variants){
const stockVariant = parseInt(v.dataset.stock)
if(stock > stockVariant){
alert("Flash sale vượt tồn kho của variant: " + v.value)
window.location.href="/seller/flash-sales"
return
}
}

for(const v of variants){
const res = await fetch(FLASH_SALE_CREATE_URL,{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({
variant_id:v.value,
discount_percent:percent,
stock_limit:stock,
start_time:start,
end_time:end
})
})
if(!res.ok){
const text = await res.text()
console.error(text)
alert("Tạo flash sale thất bại")
return
}
}
location.reload()
}
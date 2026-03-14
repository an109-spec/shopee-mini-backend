document.addEventListener("DOMContentLoaded", () => {
updateCountdown()
setInterval(updateCountdown,1000)
updateStatus()
sortFilter()

function updateCountdown(){
document.querySelectorAll(".countdown").forEach(el=>{
const end = parseInt(el.dataset.end) * 1000
const now = Date.now()
let diff = end - now
if(diff <= 0){
el.innerText = "Ended"
return
}

const h = Math.floor(diff/3600000)
const m = Math.floor((diff%3600000)/60000)
const s = Math.floor((diff%60000)/1000)
el.innerText =
`${h}:${m.toString().padStart(2,"0")}:${s.toString().padStart(2,"0")}`
})
}

function updateStatus(){
document.querySelectorAll(".saleRow").forEach(row=>{
const start = row.dataset.start*1000
const end = row.dataset.end*1000
const now = Date.now()
const label = row.querySelector(".statusLabel")
if(now < start){
label.innerHTML =
`<span class="status status--pending">Upcoming</span>`
}
else if(now > end){
label.innerHTML =
`<span class="status status--off">Ended</span>`
}
else{
label.innerHTML =
`<span class="status status--active">Running</span>`
}
})
}

function sortFilter(){
const filter = document.getElementById("saleFilter")
if(!filter) return
filter.addEventListener("change",()=>{
const type = filter.value
document.querySelectorAll(".saleRow").forEach(row=>{
const start = row.dataset.start*1000
const end = row.dataset.end*1000
const now = Date.now()

let status="running"
if(now < start) status="upcoming"
else if(now > end) status="ended"
if(type==="all" || type===status)
row.style.display=""
else
row.style.display="none"
})
})
}
})
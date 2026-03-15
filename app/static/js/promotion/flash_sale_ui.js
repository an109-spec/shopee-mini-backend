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

const days = Math.floor(diff / (1000*60*60*24))
diff %= (1000*60*60*24)

const hours = Math.floor(diff / (1000*60*60))
diff %= (1000*60*60)

const minutes = Math.floor(diff / (1000*60))
diff %= (1000*60)

const seconds = Math.floor(diff / 1000)

el.innerText =
`${days}d ${hours}h ${minutes}m ${seconds}s`

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
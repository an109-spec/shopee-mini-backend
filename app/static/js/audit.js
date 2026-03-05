async function loadAudit(){

const res = await fetch("/audit/logs")

const data = await res.json()

let html=""

data.forEach(log=>{

html+=`
<tr>

<td>${log.time}</td>
<td>${log.user}</td>
<td>${log.action}</td>
<td>${log.target}</td>

</tr>
`

})

document.getElementById("audit_table").innerHTML=html

}

loadAudit()
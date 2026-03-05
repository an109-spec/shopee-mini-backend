const socket = io()

const box = document.getElementById("chat-box")
const input = document.getElementById("message-input")
const sendBtn = document.getElementById("send-btn")
const typingDiv = document.getElementById("typing")


socket.on("connect", () => {

    socket.emit("join_room", {
        room_id: ROOM_ID
    })

    loadHistory()

})


function loadHistory(){

    fetch(`/chat/history/${ROOM_ID}`)
    .then(r=>r.json())
    .then(data=>{

        data.forEach(renderMessage)

    })

}


sendBtn.onclick = sendMessage

input.addEventListener("keypress", e=>{

    socket.emit("typing",{room_id:ROOM_ID})

    if(e.key==="Enter"){
        sendMessage()
    }

})


function sendMessage(){

    const msg = input.value.trim()

    if(!msg) return

    socket.emit("send_message",{

        room_id: ROOM_ID,
        content: msg

    })

    input.value=""

}


socket.on("receive_message", data => {

    renderMessage(data)

})


socket.on("user_typing", () => {

    typingDiv.innerText = "typing..."

    setTimeout(()=>{
        typingDiv.innerText=""
    },1500)

})


function renderMessage(msg){

    const div = document.createElement("div")

    div.classList.add("message")

    if(msg.sender_id == CURRENT_USER_ID){
        div.classList.add("self")
    }

    div.innerHTML = `
        <div class="bubble">${msg.content}</div>
    `

    box.appendChild(div)

    box.scrollTop = box.scrollHeight

}
const ROOM_ID = window.CHAT_CONFIG.room_id
const CURRENT_USER_ID = window.CHAT_CONFIG.current_user_id
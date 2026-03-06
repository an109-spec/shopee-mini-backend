document.addEventListener("DOMContentLoaded", () => {

console.log("Shopee Mini UI Loaded");


/* AUTO HIDE ALERT */

const alerts = document.querySelectorAll(".alert");

alerts.forEach(alert => {

setTimeout(() => {

alert.style.opacity="0";
alert.style.transition="0.5s";

setTimeout(()=>{

alert.remove();

},500);

},3000);

});


/* SEARCH SUGGEST */

const input=document.getElementById("searchInput");
const suggest=document.getElementById("searchSuggest");

if(input){

input.addEventListener("focus",()=>{

suggest.style.display="block";

});

input.addEventListener("blur",()=>{

setTimeout(()=>{

suggest.style.display="none";

},200);

});

}

});
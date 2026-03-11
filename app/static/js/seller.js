document.addEventListener("DOMContentLoaded", () => {

  /* ===============================
     Revenue Chart
  =============================== */
  const chartElement = document.getElementById("revenueChart");

  if (chartElement) {
    const ctx = chartElement.getContext("2d");

    fetch("/seller/api/revenue")
      .then(res => res.json())
      .then(data => {
        new Chart(ctx, {
          type: "line",
          data: {
            labels: data.labels,
            datasets: [{
              label: "Doanh thu",
              data: data.values,
              borderWidth: 2,
              tension: 0.4
            }]
          }
        });
      });
  }


  /* ===============================
     Shop name counter
  =============================== */
  const shopNameInput = document.querySelector('input[name="name"]');
  const counter = document.querySelector(".counter");

  if (shopNameInput && counter) {

    counter.textContent = shopNameInput.value.length + "/30";

    shopNameInput.addEventListener("input", () => {
      counter.textContent = shopNameInput.value.length + "/30";
    });

  }

  /* ===============================
     Address Modal
  =============================== */
  const modal = document.getElementById("addressModal");
  const editBtn = document.querySelector(".edit-address-btn");
  const cancelBtn = document.getElementById("cancelAddress");
  const saveBtn = document.getElementById("saveAddress");

  if (editBtn) {
    editBtn.onclick = () => {
      modal.style.display = "flex";
    };
  }

  if (cancelBtn) {
    cancelBtn.onclick = () => {
      modal.style.display = "none";
    };
  }


  /* ===============================
     Address dropdown (VN API)
  =============================== */
  const city = document.getElementById("citySelect");
  const district = document.getElementById("districtSelect");
  const ward = document.getElementById("wardSelect");

  if (city) {

    fetch("https://provinces.open-api.vn/api/p/")
      .then(res => res.json())
      .then(data => {
        data.forEach(p => {
          city.innerHTML += `<option value="${p.code}">${p.name}</option>`;
        });
      });

    city.addEventListener("change", () => {

      district.innerHTML = '<option value="">Chọn Quận/Huyện</option>';
      ward.innerHTML = '<option value="">Chọn Phường/Xã</option>';

      fetch(`https://provinces.open-api.vn/api/p/${city.value}?depth=2`)
        .then(res => res.json())
        .then(data => {

          data.districts.forEach(d => {
            district.innerHTML += `<option value="${d.code}">${d.name}</option>`;
          });

        });

    });

    district.addEventListener("change", () => {

      ward.innerHTML = '<option value="">Chọn Phường/Xã</option>';

      fetch(`https://provinces.open-api.vn/api/d/${district.value}?depth=2`)
        .then(res => res.json())
        .then(data => {

          data.wards.forEach(w => {
            ward.innerHTML += `<option value="${w.code}">${w.name}</option>`;
          });

        });

    });

  }


  /* ===============================
     Save address
  =============================== */
  if (saveBtn) {

    saveBtn.onclick = () => {

      const detail = document.getElementById("modalDetail").value;

      const cityText = city.options[city.selectedIndex]?.text || "";
      const districtText = district.options[district.selectedIndex]?.text || "";
      const wardText = ward.options[ward.selectedIndex]?.text || "";

      const fullAddress =
        detail + ", " + wardText + ", " + districtText + ", " + cityText;

      document.getElementById("pickupAddressInput").value = fullAddress;

      const addressView = document.querySelector(".pickup-address");
      if (addressView) {
        addressView.textContent = fullAddress;
      }

      modal.style.display = "none";

    };

  }

});


/* ===============================
   Product Image Upload
================================*/

document.addEventListener("DOMContentLoaded", () => {

const uploadBox = document.getElementById("uploadArea")
const imageInput = document.getElementById("imageInput")
const preview = document.getElementById("previewImages")
const thumbnailInput = document.getElementById("thumbnailIndex")

if(!uploadBox || !imageInput || !preview) return

let filesStore = []
function syncInputFiles(){

const dt = new DataTransfer()

filesStore.forEach(file=>{
dt.items.add(file)
})

imageInput.files = dt.files

}
uploadBox.onclick = () => {
    if(imageInput) imageInput.click()
}
uploadBox.addEventListener("dragenter", e=>{
e.preventDefault()
})

uploadBox.addEventListener("dragover", e=>{
    e.preventDefault()
})

uploadBox.addEventListener("drop", e=>{
    e.preventDefault()
    e.stopPropagation()
    handleFiles(e.dataTransfer.files)
})

imageInput.addEventListener("change", ()=>{
    handleFiles(imageInput.files)
})

function handleFiles(files){

for(const file of files){

if(filesStore.length >= 9){
alert("Chỉ được tối đa 9 ảnh")
break
}

filesStore.push(file)

}

syncInputFiles()
renderPreview()

}

function renderPreview(){
    preview.innerHTML=""
    filesStore.forEach((file,index)=>{

        const reader = new FileReader()

        reader.onload = e =>{

            const div = document.createElement("div")
            div.className="image-item"

            if(thumbnailInput && index === Number(thumbnailInput.value)){
                div.classList.add("active")
            }

            div.innerHTML = `
                <img src="${e.target.result}">
                <button type="button" class="delete-img">×</button>
                ${thumbnailInput && index === Number(thumbnailInput.value) ? "<span>Ảnh đại diện</span>" : ""}
            `
            const deleteBtn = div.querySelector(".delete-img")

              deleteBtn.onclick = (ev)=>{

              ev.stopPropagation()

              filesStore.splice(index,1)

              syncInputFiles()

              renderPreview()

              }

            div.onclick = ()=>{
              if(thumbnailInput){
                  thumbnailInput.value = index
              }
              renderPreview()
          }

            preview.appendChild(div)
        }

        reader.readAsDataURL(file)
    })
}

})


/* ===============================
   Variant dynamic
================================*/

function addVariant(){

const body = document.getElementById("variantBody")

const row = document.createElement("tr")

row.innerHTML = `

<td>
<input type="file" name="variant_image[]" accept="image/*">
</td>

<td>
<input name="variant_size[]" placeholder="S">
</td>

<td>
<input name="variant_color[]" placeholder="Red">
</td>

<td>
<div class="price-input">
<input type="number" name="variant_price[]" value="0">
<div class="price-text"></div>
</div>
</td>

<td>
<input type="number" name="variant_stock[]" value="0">
</td>

<td>
<button type="button" onclick="removeVariant(this)">X</button>
</td>

`

body.appendChild(row)

}

function removeVariant(btn){

btn.closest("tr").remove()

}

/* ===============================
   Variant generator (Size x Color)
================================*/

function generateVariants(){

const sizes = document
.getElementById("sizeInput")
.value
.split(",")

const colors = document
.getElementById("colorInput")
.value
.split(",")

const body = document.getElementById("variantBody")

body.innerHTML=""

sizes.forEach(size=>{

colors.forEach(color=>{

const row=`
<tr>

<td>
<input type="file" name="variant_image[]" accept="image/*">
</td>

<td>
<input name="variant_size[]" value="${size.trim()}">
</td>

<td>
<input name="variant_color[]" value="${color.trim()}">
</td>

<td>
<div class="price-input">
<input type="number" name="variant_price[]" value="0">
<div class="price-text"></div>
</div>
</td>

<td>
<input type="number" name="variant_stock[]" value="0">
</td>

<td>
<button type="button" onclick="removeVariant(this)">X</button>
</td>

</tr>
`

body.insertAdjacentHTML("beforeend",row)

})

})

}

function setBulkPrice(){

const price=document
.getElementById("bulkPrice").value

const stock=document
.getElementById("bulkStock").value

document
.querySelectorAll("[name='variant_price[]']")
.forEach(e=>{
e.value=price
})

document
.querySelectorAll("[name='variant_stock[]']")
.forEach(e=>{
e.value=stock
})

}

/* ===============================
   Price -> Vietnamese text
================================*/

function numberToVietnamese(num) {

const units = ["", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
const tens = ["", "", "hai mươi", "ba mươi", "bốn mươi", "năm mươi", "sáu mươi", "bảy mươi", "tám mươi", "chín mươi"]
const scales = ["", " nghìn", " triệu", " tỷ"]

if (num == 0) return "không đồng"

let result = ""
let scale = 0

while (num > 0) {

let chunk = num % 1000

if (chunk != 0) {

let chunkText = ""

let hundred = Math.floor(chunk / 100)
let ten = Math.floor((chunk % 100) / 10)
let unit = chunk % 10

if (hundred > 0) chunkText += units[hundred] + " trăm "

if (ten > 1) {
chunkText += tens[ten] + " "
if (unit > 0) chunkText += units[unit] + " "
}

else if (ten == 1) {
chunkText += "mười "
if (unit > 0) chunkText += units[unit] + " "
}

else if (unit > 0) {
chunkText += units[unit] + " "
}

result = chunkText + scales[scale] + " " + result
}

num = Math.floor(num / 1000)
scale++
}

return result.trim() + " đồng"
}



/* listen variant price input */

document.addEventListener("input", function(e){

    if(e.target.name === "variant_price[]"){

const value = parseInt(e.target.value)

const priceBox = e.target.closest(".price-input")
if(!priceBox) return

const textBox = priceBox.querySelector(".price-text")
if(!textBox) return

if(!value){
textBox.innerText=""
return
}

textBox.innerText = numberToVietnamese(value)

}

})

document.addEventListener("DOMContentLoaded", () => {

  const prices = document.querySelectorAll('input[name="variant_price[]"]')

  prices.forEach(input => {

const value = parseInt(input.value)

if(!value) return

const priceBox = input.closest(".price-input")
if(!priceBox) return

const textBox = priceBox.querySelector(".price-text")

if(textBox){
textBox.innerText = numberToVietnamese(value)
}

})

})
document.addEventListener("DOMContentLoaded", () => {

const checkboxes = document.querySelectorAll(
'input[name="category_ids[]"]'
)

checkboxes.forEach(box => {

box.addEventListener("change", () => {

let checked =
document.querySelectorAll(
'input[name="category_ids[]"]:checked'
)

if(checked.length > 3){

box.checked = false
alert("Chỉ được chọn tối đa 3 danh mục")

}

})

})
})
const bulkPrice = document.getElementById("bulkPrice")

if(bulkPrice){

bulkPrice.addEventListener("input", e=>{

const value = parseInt(e.target.value)

if(!value) return

const text = numberToVietnamese(value)

let helper = document.getElementById("bulkPriceText")

if(!helper){
helper = document.createElement("div")
helper.id = "bulkPriceText"
bulkPrice.parentNode.appendChild(helper)
}

helper.innerText = text

})

}
function deleteImage(url,btn){

fetch("/seller/products/image/delete",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({
image_url:url
})
})
.then(res=>res.json())
.then(data=>{

if(data.success){
btn.parentElement.remove()
}else{
alert("Xóa ảnh thất bại")
}

})
.catch(()=>{
alert("Server error")
})

}

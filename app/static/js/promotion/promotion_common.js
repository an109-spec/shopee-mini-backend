let selectedVariantPrice = 0
let selectedVariantStock = 0
document.addEventListener("DOMContentLoaded", function(){
  document.querySelectorAll(".productCheck").forEach(cb => {
    cb.addEventListener("change", function(){
      const productId = this.value
      const box = document.getElementById("variantBox-" + productId)
      if(this.checked){
        fetch(`/seller/api/product/${productId}/variants`)
          .then(res => res.json())
          .then(data => {
            if(!data || data.length === 0 || !data[0].id){
              box.innerHTML = `
<div class="variant-empty">
Sản phẩm này không có phân loại
</div>
<label class="variant-item">
<input type="checkbox" name="variant_ids[]" value="${productId}" data-price="0" data-stock="0">
Áp dụng cho toàn bộ sản phẩm
</label>
`
              return
            }
            let html = "<div class='variant-title'>Phân loại:</div>"
            html += "<div class='variant-list'>"
            data.forEach(v => {
              html += `
<label class="variant-item">
<input type="checkbox"
name="variant_ids[]"
value="${v.id}"
data-price="${v.price}"
data-stock="${v.stock}">
${v.size || v.color || "không có phân loại"}
</label>
`
})
            html += "</div>"
            box.innerHTML = html
          })
      } else {
        box.innerHTML = ""
      }
    })
  })

  document.addEventListener("change", function(e){
    if(e.target.name === "variant_ids[]"){
      const variants = document.querySelectorAll("input[name='variant_ids[]']:checked")
      let prices = []
      let totalStock = 0

      variants.forEach(v => {
        const price = parseFloat(v.dataset.price ?? 0)
        const stock = parseInt(v.dataset.stock || 0)
        prices.push(price)
        totalStock += stock
      })

      // stock nhập ở form là tổng số lượng flash sale cho các variant đã chọn
      selectedVariantStock = totalStock

      const originPrice = document.getElementById("originPrice")
      const stockInfo = document.getElementById("stockInfo")

      if(prices.length === 0){
        if(originPrice) originPrice.value = ""
        if(stockInfo) stockInfo.innerText = "Tồn kho: -"
        return
      }

      const min = Math.min(...prices)
      const max = Math.max(...prices)
      selectedVariantPrice = min

      if(originPrice){
        if(min === max) originPrice.value = min
        else originPrice.value = `${min} - ${max}`
      }

      if(stockInfo){
        stockInfo.innerText = "Tổng tồn kho: " + totalStock
      }
    }
  })

  const form = document.querySelector("form")
  if(form){
    form.addEventListener("submit", function(e){
      const variants = document.querySelectorAll("input[name='variant_ids[]']:checked")
      if(variants.length === 0){
        alert("Phải chọn ít nhất 1 phân loại")
        e.preventDefault()
      }
    })
  }

  const selectAll = document.getElementById("selectAllVariants")
  if(selectAll) {
    selectAll.addEventListener("change", async function(){
      const checked = this.checked
      const products = document.querySelectorAll(".productCheck")

      for(const p of products){
        p.checked = checked

        const productId = p.value
        const box = document.getElementById("variantBox-" + productId)

        if(checked){
          if(box.innerHTML.trim() === ""){
            const res = await fetch(`/seller/api/product/${productId}/variants`)
            const data = await res.json()

            let html = "<div class='variant-title'>Phân loại:</div>"
            html += "<div class='variant-list'>"

            if(!data || data.length === 0 || !data[0].id){
              html += `

<label class="variant-item">
<input type="checkbox" name="variant_ids[]" value="${productId}" data-price="0" data-stock="0">
Áp dụng cho toàn bộ sản phẩm
</label>
`

            } else {
              data.forEach(v => {
                html += `
<label class="variant-item">
<input type="checkbox"
name="variant_ids[]"
value="${v.id}"
data-price="${v.price}"
data-stock="${v.stock}">
${v.size || v.color || "không có phân loại"}
</label>
`

              })
            }

            html += "</div>"
            box.innerHTML = html
          }

          setTimeout(() => {
            box.querySelectorAll("input[name='variant_ids[]']").forEach(v => {
              v.checked = true
              v.dispatchEvent(new Event("change", { bubbles: true }))
            })
          }, 50)
        } else {
          box.innerHTML = ""
        }
      }
    })
  }

})

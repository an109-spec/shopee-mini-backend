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
  const input = document.querySelector('input[name="name"]');
  const counter = document.querySelector(".counter");

  if (input && counter) {

    counter.textContent = input.value.length + "/30";

    input.addEventListener("input", () => {
      counter.textContent = input.value.length + "/30";
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

    // Load provinces
    fetch("https://provinces.open-api.vn/api/p/")
      .then(res => res.json())
      .then(data => {
        data.forEach(p => {
          city.innerHTML += `<option value="${p.code}">${p.name}</option>`;
        });
      });


    // Province change
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


    // District change
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
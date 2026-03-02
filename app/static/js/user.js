/* =========================
   STATUS
========================= */

function setStatus(message, isError = false) {
  const el = document.getElementById("status-message");
  if (!el) return;

  el.textContent = message;
  el.className = `status-message ${
    isError ? "status-message--error" : "status-message--success"
  }`;
}

/* =========================
   API REQUEST WRAPPER
========================= */

async function apiRequest(path, method = "GET", body = null) {
  const options = {
    method,
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include", // quan trọng nếu dùng session/cookie
  };

  if (body) {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(path, options);
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Có lỗi xảy ra");
  }

  return data;
}

/* =========================
   RENDER PROFILE
========================= */

function renderProfile(data) {
  document.getElementById("profile-username").textContent =
    data.username || "-";
  document.getElementById("profile-email").textContent =
    data.email || "-";
  document.getElementById("profile-phone").textContent =
    data.phone || "-";
  document.getElementById("profile-full-name").textContent =
    data.profile?.full_name || "-";
  document.getElementById("profile-birthday").textContent =
    data.profile?.birthday || "-";

  document.getElementById("edit-username").value =
    data.username || "";
  document.getElementById("edit-email").value =
    data.email || "";
  document.getElementById("edit-phone").value =
    data.phone || "";
  document.getElementById("edit-full-name").value =
    data.profile?.full_name || "";
  document.getElementById("edit-birthday").value =
    data.profile?.birthday || "";

  if (data.avatar) {
    document.getElementById("avatar-preview").src = data.avatar;
  }
}

/* =========================
   RENDER ORDERS
========================= */

function renderOrders(orders) {
  const container = document.getElementById("orders-container");
  container.innerHTML = "";

  if (!orders.length) {
    container.innerHTML = "<p>Chưa có đơn hàng nào.</p>";
    return;
  }

  orders.forEach((order) => {
    const itemList = (order.items || [])
      .map(
        (item) =>
          `<li>${item.product_name || "Sản phẩm"} x ${item.quantity} - ${item.price}</li>`
      )
      .join("");

    const block = document.createElement("div");
    block.className = "order-item";
    block.innerHTML = `
      <p><strong>Đơn #${order.order_id}</strong> - ${order.status}</p>
      <p>Tổng tiền: ${order.total_price}</p>
      <ul>${itemList}</ul>
    `;
    container.appendChild(block);
  });
}

/* =========================
   LOAD PROFILE
========================= */

async function loadProfile() {
  const data = await apiRequest("/user/profile");
  renderProfile(data);
}

/* =========================
   EVENT LISTENERS
========================= */

document.getElementById("btn-save-profile")?.addEventListener("click", async () => {
  try {
    const payload = {
      username: document.getElementById("edit-username").value,
      email: document.getElementById("edit-email").value,
      phone: document.getElementById("edit-phone").value,
      full_name: document.getElementById("edit-full-name").value,
      birthday: document.getElementById("edit-birthday").value,
    };

    const data = await apiRequest("/user/profile", "PATCH", payload);
    renderProfile(data);
    setStatus("Đã cập nhật hồ sơ");
  } catch (error) {
    setStatus(error.message, true);
  }
});

document.getElementById("btn-auto-avatar")?.addEventListener("click", async () => {
  try {
    const data = await apiRequest("/user/avatar/auto", "POST");
    document.getElementById("avatar-preview").src = data.avatar;
    setStatus("Đã tạo avatar ngẫu nhiên");
  } catch (error) {
    setStatus(error.message, true);
  }
});

document.getElementById("btn-change-avatar")?.addEventListener("click", async () => {
  try {
    const avatar = document.getElementById("avatar-url").value;
    const data = await apiRequest("/user/avatar", "PATCH", { avatar });
    document.getElementById("avatar-preview").src = data.avatar;
    setStatus("Đã cập nhật avatar");
  } catch (error) {
    setStatus(error.message, true);
  }
});

document.getElementById("btn-upload-avatar")?.addEventListener("click", async () => {
  try {
    const fileInput = document.getElementById("avatar-file");
    const file = fileInput.files[0];

    if (!file) {
      throw new Error("Vui lòng chọn ảnh avatar");
    }

    const formData = new FormData();
    formData.append("avatar", file);

    const response = await fetch("/user/avatar/upload", {
      method: "POST",
      body: formData,
      credentials: "include",
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Có lỗi xảy ra");
    }

    document.getElementById("avatar-preview").src = data.avatar;
    setStatus("Đã cập nhật avatar từ file");
  } catch (error) {
    setStatus(error.message, true);
  }
});

document.getElementById("btn-change-password")?.addEventListener("click", async () => {
  try {
    const current_password =
      document.getElementById("current-password").value;
    const new_password =
      document.getElementById("new-password").value;

    const data = await apiRequest("/user/password", "PATCH", {
      current_password,
      new_password,
    });

    setStatus(data.message || "Đổi mật khẩu thành công");

    document.getElementById("current-password").value = "";
    document.getElementById("new-password").value = "";
  } catch (error) {
    setStatus(error.message, true);
  }
});

document.getElementById("btn-load-orders")?.addEventListener("click", async () => {
  try {
    const data = await apiRequest("/user/purchase-history");
    renderOrders(data.orders || []);
    setStatus("Đã tải lịch sử mua hàng");
  } catch (error) {
    setStatus(error.message, true);
  }
});

/* =========================
   INITIAL LOAD
========================= */

(async function init() {
  try {
    await loadProfile();
  } catch (error) {
    setStatus(error.message, true);
  }
})();
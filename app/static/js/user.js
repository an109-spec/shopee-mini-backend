function getUserId() {
  const value = document.getElementById("user-id").value;
  const userId = Number(value);
  if (!userId || userId < 1) {
    throw new Error("Vui lòng nhập user_id hợp lệ");
  }
  return userId;
}

function setStatus(message, isError = false) {
  const el = document.getElementById("status-message");
  el.textContent = message;
  el.className = `status-message ${isError ? "status-message--error" : "status-message--success"}`;
}

async function apiRequest(path, method = "GET", body = null) {
  const options = { method, headers: {} };

  if (body) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body);
  }

  const response = await fetch(path, options);
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Có lỗi xảy ra");
  }

  return data;
}

function renderProfile(data) {
  document.getElementById("profile-username").textContent = data.username || "-";
  document.getElementById("profile-email").textContent = data.email || "-";
  document.getElementById("profile-phone").textContent = data.phone || "-";
  document.getElementById("profile-full-name").textContent = data.profile?.full_name || "-";
  if (data.avatar) {
    document.getElementById("avatar-preview").src = data.avatar;
  }
}

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

document.getElementById("btn-load-profile").addEventListener("click", async () => {
  try {
    const userId = getUserId();
    const data = await apiRequest(`/user/profile?user_id=${userId}`);
    renderProfile(data);
    setStatus("Đã tải hồ sơ thành công");
  } catch (error) {
    setStatus(error.message, true);
  }
});

document.getElementById("btn-auto-avatar").addEventListener("click", async () => {
  try {
    const userId = getUserId();
    const data = await apiRequest(`/user/avatar/auto?user_id=${userId}`, "POST");
    document.getElementById("avatar-preview").src = data.avatar;
    setStatus("Đã tạo avatar ngẫu nhiên");
  } catch (error) {
    setStatus(error.message, true);
  }
});

document.getElementById("btn-change-avatar").addEventListener("click", async () => {
  try {
    const userId = getUserId();
    const avatar = document.getElementById("avatar-url").value;
    const data = await apiRequest(`/user/avatar?user_id=${userId}`, "PATCH", { avatar });
    document.getElementById("avatar-preview").src = data.avatar;
    setStatus("Đã cập nhật avatar");
  } catch (error) {
    setStatus(error.message, true);
  }
});

document.getElementById("btn-change-password").addEventListener("click", async () => {
  try {
    const userId = getUserId();
    const current_password = document.getElementById("current-password").value;
    const new_password = document.getElementById("new-password").value;
    const data = await apiRequest(`/user/password?user_id=${userId}`, "PATCH", {
      current_password,
      new_password,
    });
    setStatus(data.message || "Đổi mật khẩu thành công");
  } catch (error) {
    setStatus(error.message, true);
  }
});

document.getElementById("btn-load-orders").addEventListener("click", async () => {
  try {
    const userId = getUserId();
    const data = await apiRequest(`/user/purchase-history?user_id=${userId}`);
    renderOrders(data.orders || []);
    setStatus("Đã tải lịch sử mua hàng");
  } catch (error) {
    setStatus(error.message, true);
  }
});
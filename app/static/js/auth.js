document.addEventListener("DOMContentLoaded", () => {
  const forms = document.querySelectorAll(".auth__form");

  forms.forEach((form) => {
    form.addEventListener("submit", () => {
      const btn = form.querySelector("button[type='submit']");
      if (btn && !btn.disabled) {
        btn.classList.add("btn--loading");
        btn.innerText = "Đang xử lý...";
      }
    });
  });
const timerEl = document.querySelector("[data-otp-expire-at]");
  if (!timerEl) {
    return;
  }

  const valueEl = timerEl.querySelector(".otp-timer__value");
  const resendBtn = document.querySelector("[data-resend-btn]");
  const rawExpireAt = timerEl.getAttribute("data-otp-expire-at");
  const expireAt = rawExpireAt ? new Date(rawExpireAt) : null;

  if (!expireAt || Number.isNaN(expireAt.getTime()) || !valueEl) {
    return;
  }

  const setResendState = (enabled) => {
    if (!resendBtn) return;
    resendBtn.disabled = !enabled;
    resendBtn.textContent = enabled ? "Gửi lại OTP khác" : "Gửi lại OTP khác (chờ hết hạn)";
  };

  const updateCountdown = () => {
    const now = new Date();
    const diffMs = expireAt.getTime() - now.getTime();

    if (diffMs <= 0) {
      valueEl.textContent = "00:00";
      timerEl.classList.remove("otp-timer--warning");
      timerEl.classList.add("otp-timer--expired");
      setResendState(true);
      return false;
    }

    const totalSec = Math.floor(diffMs / 1000);
    const min = Math.floor(totalSec / 60);
    const sec = totalSec % 60;

    timerEl.classList.remove("otp-timer--warning", "otp-timer--expired");
    if (totalSec <= 30) {
      timerEl.classList.add("otp-timer--expired");
    } else if (totalSec <= 90) {
      timerEl.classList.add("otp-timer--warning");
    }

    valueEl.textContent = `${String(min).padStart(2, "0")}:${String(sec).padStart(2, "0")}`;
    setResendState(false);
    return true;
  };

  updateCountdown();
  const intervalId = window.setInterval(() => {
    if (!updateCountdown()) {
      window.clearInterval(intervalId);
    }
  }, 1000);
});
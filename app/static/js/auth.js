/**
 * Auth page scripts
 * Không xử lý business logic
 */

document.addEventListener("DOMContentLoaded", () => {
  const forms = document.querySelectorAll(".auth__form");

  forms.forEach((form) => {
    form.addEventListener("submit", () => {
      const btn = form.querySelector("button[type='submit']");
      if (btn) {
        btn.disabled = true;
        btn.innerText = "Đang xử lý...";
      }
    });
  });
});

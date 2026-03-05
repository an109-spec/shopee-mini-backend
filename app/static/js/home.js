(function () {
  const el = document.getElementById("flash-countdown");
  if (!el) return;

  const endsAt = el.dataset.endsAt;
  if (!endsAt) return;

  function render() {
    const diff = new Date(endsAt).getTime() - Date.now();
    if (diff <= 0) {
      el.textContent = "Đã kết thúc";
      return;
    }

    const sec = Math.floor(diff / 1000) % 60;
    const min = Math.floor(diff / (1000 * 60)) % 60;
    const hour = Math.floor(diff / (1000 * 60 * 60));
    el.textContent = [hour, min, sec].map((v) => String(v).padStart(2, "0")).join(":");
    requestAnimationFrame(render);
  }

  render();
})();
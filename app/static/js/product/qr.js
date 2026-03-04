window.ProductQR = {
  bind(productId) {
    const open = document.getElementById('open-qr');
    const close = document.getElementById('close-qr');
    const modal = document.getElementById('qr-modal');
    const image = document.getElementById('qr-image');
    if (!open || !close || !modal || !image) return;

    open.addEventListener('click', () => {
      image.src = `/products/${productId}/qr`;
      modal.classList.remove('hidden');
    });
    close.addEventListener('click', () => modal.classList.add('hidden'));
  }
};
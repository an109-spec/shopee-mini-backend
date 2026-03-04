(function () {
  const root = document.getElementById('product-detail-page');
  if (!root) return;

  const productId = root.dataset.productId;
  const endpointBase = root.dataset.endpointBase || '/products';
  const detailEl = document.getElementById('product-detail');
  const relatedEl = document.getElementById('related-products');
  const reviewEl = document.getElementById('review-list');
  const reviewForm = document.getElementById('review-form');

  function renderProduct(item) {
    detailEl.innerHTML = `<article class="product-detail"><h2>${item.name}</h2><p>${item.description || ''}</p><p>Giá: ${item.price}</p></article>`;
  }

  function renderRelated(items) {
    relatedEl.innerHTML = (items || []).map((item) => `<article class="product-card"><h4>${item.name}</h4><p>${item.price}</p></article>`).join('');
  }

  function renderReviews(items) {
    reviewEl.innerHTML = (items || []).map((r) => window.ProductReview.renderItem(r)).join('') || '<p>Chưa có đánh giá.</p>';
  }

  async function loadAll() {
    const [productRes, relatedRes, reviewsRes] = await Promise.all([
      fetch(`${endpointBase}/${productId}`),
      fetch(`${endpointBase}/${productId}/related`),
      fetch(`${endpointBase}/${productId}/reviews`)
    ]);

    renderProduct(await productRes.json());
    renderRelated((await relatedRes.json()).items || []);
    renderReviews((await reviewsRes.json()).items || []);
    if (window.ProductQR) window.ProductQR.bind(productId);
  }

  reviewForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(reviewForm);
    const payload = {
      user_id: Number(fd.get('user_id')),
      rating: Number(fd.get('rating')),
      comment: fd.get('comment')
    };

    await fetch(`${endpointBase}/${productId}/reviews`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const refreshed = await fetch(`${endpointBase}/${productId}/reviews`);
    renderReviews((await refreshed.json()).items || []);
    reviewForm.reset();
  });

  loadAll();
})();
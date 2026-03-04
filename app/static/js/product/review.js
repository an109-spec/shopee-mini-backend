window.ProductReview = {
  renderItem(review) {
    return `<article class="review-item"><div class="review-item__head"><strong>User #${review.user_id}</strong><span>${review.rating}/5</span></div><p>${review.comment || ''}</p></article>`;
  }
};
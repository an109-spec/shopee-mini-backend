window.ProductFilter = {
  read() {
    const form = document.getElementById('product-filter-form');
    if (!form) return {};
    const data = new FormData(form);
    return Object.fromEntries([...data.entries()].filter(([, v]) => String(v).trim() !== ''));
  }
};
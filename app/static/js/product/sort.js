window.ProductSort = {
  read() {
    const select = document.getElementById('sort-select');
    return select ? select.value : 'newest';
  }
};
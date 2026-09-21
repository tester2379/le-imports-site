// Products page filters (DSM-1143). Filtering is done on the cards already in
// the page rather than by re-fetching, so it stays instant and works with the
// site served as plain static files. Both selects narrow the same set.
(function () {
  "use strict";
  var grid = document.getElementById("productGrid");
  if (!grid) return;
  var brand = document.getElementById("filterBrand");
  var cat = document.getElementById("filterCategory");
  var count = document.getElementById("filterCount");
  var none = document.getElementById("noResults");
  var reset = document.getElementById("filterReset");
  var cards = Array.prototype.slice.call(grid.querySelectorAll(".product-card"));

  function apply() {
    var b = brand.value, c = cat.value, shown = 0;
    cards.forEach(function (card) {
      var ok = (!b || card.dataset.brand === b) && (!c || card.dataset.category === c);
      card.hidden = !ok;
      if (ok) shown++;
    });
    count.textContent = shown + (shown === 1 ? " product" : " products");
    none.hidden = shown !== 0;
  }
  brand.addEventListener("change", apply);
  cat.addEventListener("change", apply);
  reset.addEventListener("click", function () {
    brand.value = ""; cat.value = ""; apply();
  });
})();

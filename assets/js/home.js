/* Landing page widgets */
(function () {
  const map = {
    produced: () => Brew.state.produced,
    oee:      () => Brew.efficiency(),
    temp:     () => Brew.state.temperature.toFixed(1),
    press:    () => Brew.state.pressure.toFixed(2)
  };
  function render() {
    document.querySelectorAll("[data-counter]").forEach((el) => {
      const k = el.getAttribute("data-counter");
      if (map[k]) el.textContent = map[k]();
    });
  }
  Brew.subscribe(render);
  Brew.spark(document.getElementById("hero-spark"),
    () => Brew.state.metricsSeries.map(p => p.eff || 0));

  // auto-start so visitor sees motion
  if (!Brew.state.running && !Brew.state.eStop && Brew.state.produced === 0) {
    setTimeout(() => Brew.start(), 600);
  }
})();

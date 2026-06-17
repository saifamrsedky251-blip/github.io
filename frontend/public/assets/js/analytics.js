(function () {
  Brew.spark(document.getElementById("ch-prod"),
    () => Brew.state.metricsSeries.map(p => p.produced || 0),
    "#c8763a");
  Brew.spark(document.getElementById("ch-def"),
    () => Brew.state.metricsSeries.map(p => p.defective || 0),
    "#d96452");
  Brew.spark(document.getElementById("ch-temp"),
    () => Brew.state.metricsSeries.map(p => p.temp || 0),
    "#e6b454");
  Brew.spark(document.getElementById("ch-eff"),
    () => Brew.state.metricsSeries.map(p => p.eff || 0),
    "#6ec28c");
})();

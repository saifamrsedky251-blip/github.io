(function () {
  const $ = (id) => document.getElementById(id);

  $("btn-start").addEventListener("click", () => Brew.start());
  $("btn-stop").addEventListener("click",  () => Brew.stop());
  $("btn-reset").addEventListener("click", () => { if (confirm("Reset all counters?")) Brew.reset(); });
  $("btn-estop").addEventListener("click", () => Brew.state.eStop ? Brew.releaseEStop() : Brew.eStop());

  function setArc(path, percent) {
    const len = 283;
    path.setAttribute("stroke-dashoffset", String(len - (percent / 100) * len));
  }

  function fmtRuntime(sec) {
    const h = Math.floor(sec / 3600);
    const m = Math.floor((sec % 3600) / 60);
    const s = Math.floor(sec % 60);
    return `${String(h).padStart(2,"0")}:${String(m).padStart(2,"0")}:${String(s).padStart(2,"0")}`;
  }

  function status(value, lo, hi) {
    if (value < lo) return { tag: "tag--info", txt: "LOW" };
    if (value > hi) return { tag: "tag--bad",  txt: "HIGH" };
    return { tag: "tag--good", txt: "OK" };
  }

  function render(s) {
    $("scada-state").textContent = s.eStop ? "E-STOP" : (s.running ? "RUNNING" : "IDLE");
    $("scada-state").style.color = s.eStop ? "var(--ink-bad)" : (s.running ? "var(--ink-good)" : "var(--ink-cream)");

    $("g-temp").textContent = s.temperature.toFixed(1);
    $("g-press").textContent = s.pressure.toFixed(2);
    setArc($("g-temp-arc"),  Math.max(0, Math.min(100, ((s.temperature - 60) / 50) * 100)));
    setArc($("g-press-arc"), Math.max(0, Math.min(100, (s.pressure / 8) * 100)));

    $("scada-runtime").textContent = fmtRuntime(s.runtimeSec);

    // PVs
    const pvs = [
      { tag: "TT-101", label: "Sealer temperature", val: s.temperature.toFixed(1) + " °C", lo: 88, hi: 100, raw: s.temperature },
      { tag: "PT-201", label: "Piston pressure",    val: s.pressure.toFixed(2) + " bar", lo: 3.5, hi: 5.5, raw: s.pressure },
      { tag: "SS-301", label: "Line speed",          val: s.speed + " cpm",                lo: 5,  hi: 30, raw: s.speed },
      { tag: "QC-401", label: "Defect rate",         val: (s.targetDefectRate*100).toFixed(1) + " %", lo: 0, hi: 5, raw: s.targetDefectRate * 100 },
      { tag: "ML-501", label: "Loader health",       val: s.machineHealth.loader.toFixed(0) + " %",   lo: 70, hi: 100, raw: s.machineHealth.loader },
      { tag: "ML-502", label: "Filler health",       val: s.machineHealth.filler.toFixed(0) + " %",   lo: 70, hi: 100, raw: s.machineHealth.filler },
      { tag: "ML-503", label: "Sealer health",       val: s.machineHealth.sealer.toFixed(0) + " %",   lo: 70, hi: 100, raw: s.machineHealth.sealer },
      { tag: "ML-504", label: "Packer health",       val: s.machineHealth.packer.toFixed(0) + " %",   lo: 70, hi: 100, raw: s.machineHealth.packer },
    ];
    $("pv-body").innerHTML = pvs.map(p => {
      const st = status(p.raw, p.lo, p.hi);
      return `<tr>
        <td class="mono">${p.tag}</td>
        <td>${p.label} <small style="color:var(--ink-mute)">— <span class="mono">${p.val}</span></small></td>
        <td class="mono" style="color:var(--ink-mute)">${p.lo} – ${p.hi}</td>
        <td><span class="tag ${st.tag}">${st.txt}</span></td>
      </tr>`;
    }).join("");

    // alarms
    $("alarm-list").innerHTML = s.alarms.length
      ? s.alarms.slice(0, 20).map(a => `
        <li>
          <span class="ts">${a.ts}</span>
          <span>${a.msg}</span>
          <span class="sev tag--${a.sev === "bad" ? "bad" : (a.sev === "warn" ? "warn" : "info")}">${a.sev.toUpperCase()}</span>
        </li>`).join("")
      : `<li style="grid-template-columns:1fr; color:var(--ink-mute)">No active alarms.</li>`;

    const banner = $("alarm-banner");
    const recentBad = s.alarms.slice(0, 3).find(a => a.sev === "bad");
    if (recentBad) {
      banner.className = "alarm-bar";
      banner.innerHTML = `<span class="dot bad pulse"></span><strong>${recentBad.msg}</strong><span style="margin-left:auto; color:var(--ink-mute); font-family:var(--font-mono); font-size:11px">${recentBad.ts}</span>`;
    } else {
      banner.className = "alarm-bar ok";
      banner.innerHTML = `<span class="dot good"></span><strong>All systems nominal</strong><span style="margin-left:auto; color:var(--ink-mute); font-family:var(--font-mono); font-size:11px">no critical alarms</span>`;
    }
  }
  Brew.subscribe(render);
})();

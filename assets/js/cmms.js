(function () {
  const $ = (id) => document.getElementById(id);

  const MACHINES = [
    { key: "loader",    label: "Loader",    code: "ML-501", task: "Inspect feeder belt",   freq: "weekly" },
    { key: "filler",    label: "Filler",    code: "ML-502", task: "Clean doser & calibrate", freq: "every 12h" },
    { key: "sealer",    label: "Sealer",    code: "ML-503", task: "Replace foil reel",     freq: "shift" },
    { key: "packer",    label: "Packer",    code: "ML-504", task: "Lubricate cam",          freq: "weekly" },
    { key: "inspector", label: "Inspector", code: "ML-505", task: "Verify camera focus",   freq: "monthly" }
  ];

  $("repair-submit").addEventListener("click", () => {
    const m = $("repair-machine").value;
    const n = $("repair-note").value.trim() || "General maintenance";
    Brew.logRepair(m, n);
    $("repair-note").value = "";
  });

  function classFor(h) {
    if (h >= 85) return { tag: "tag--good", txt: "HEALTHY", bar: "bar--good", dot: "good" };
    if (h >= 70) return { tag: "tag--warn", txt: "ATTENTION", bar: "bar--warn", dot: "warn" };
    return { tag: "tag--bad", txt: "CRITICAL", bar: "bar--bad", dot: "bad" };
  }

  function fmtHM(sec) {
    const h = Math.floor(sec / 3600);
    const m = Math.floor((sec % 3600) / 60);
    return `${String(h).padStart(2,"0")}:${String(m).padStart(2,"0")}`;
  }

  function render(s) {
    // health cards
    $("health-cards").innerHTML = MACHINES.map(m => {
      const h = s.machineHealth[m.key] || 0;
      const cls = classFor(h);
      return `<div class="card" data-testid="health-${m.key}">
        <h4><span class="dot ${cls.dot}"></span> ${m.label} <small style="margin-left:auto; color:var(--ink-mute)" class="mono">${m.code}</small></h4>
        <div style="display:flex; align-items:end; justify-content:space-between; margin-bottom:8px;">
          <strong style="font-family:var(--font-display); font-size:2rem;">${h.toFixed(0)}<small style="font-size:1rem; color:var(--ink-mute)">%</small></strong>
          <span class="tag ${cls.tag}">${cls.txt}</span>
        </div>
        <div class="bar ${cls.bar}"><span style="width:${h}%"></span></div>
        <p style="font-family:var(--font-mono); font-size:11px; color:var(--ink-mute); margin:10px 0 0; letter-spacing:.1em; text-transform:uppercase;">${m.task} — ${m.freq}</p>
      </div>`;
    }).join("");

    // schedule
    $("schedule-body").innerHTML = MACHINES.map(m => {
      const h = s.machineHealth[m.key] || 0;
      const due = h < 75 ? "Overdue" : (h < 85 ? "Soon" : "Scheduled");
      const tagCls = h < 75 ? "tag--bad" : (h < 85 ? "tag--warn" : "tag--info");
      return `<tr>
        <td class="mono">${m.label} · ${m.code}</td>
        <td>${m.task}</td>
        <td class="mono" style="color:var(--ink-mute)">${m.freq}</td>
        <td><span class="tag ${tagCls}">${due}</span></td>
      </tr>`;
    }).join("");

    // repair log
    $("repair-log-list").innerHTML = s.repairLog.length
      ? s.repairLog.map(r => `<li>
          <span class="ts">${r.ts}</span>
          <span><strong>${r.machine}</strong> — ${r.note}</span>
          <span class="sev tag--info">LOGGED</span>
        </li>`).join("")
      : `<li style="grid-template-columns:1fr; color:var(--ink-mute)">No repairs logged yet.</li>`;

    // downtime ledger (estimated from non-running portion of session)
    const idleSec = Math.max(0, Math.floor(s.runtimeSec * 0.04) + s.repairLog.length * 240); // approx
    $("dt-total").textContent = fmtHM(idleSec);
    $("dt-mtbf").textContent  = s.repairLog.length ? fmtHM(Math.floor(s.runtimeSec / Math.max(1, s.repairLog.length))) : "—";
    $("dt-mttr").textContent  = s.repairLog.length ? "00:04" : "—";
  }
  Brew.subscribe(render);
})();

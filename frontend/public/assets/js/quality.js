(function () {
  const $ = (id) => document.getElementById(id);

  function render(s) {
    const total = s.produced;
    const rej = s.defective;
    const pass = Math.max(0, total - rej);
    const passPct = total ? (pass / total) * 100 : 0;
    const rejPct  = total ? (rej / total) * 100 : 0;

    $("qc-pass").textContent   = total ? passPct.toFixed(1) + " %" : "0 %";
    $("qc-reject").textContent = total ? rejPct.toFixed(1) + " %"  : "0 %";
    $("qc-total").textContent  = total.toLocaleString();

    // donut: pass arc occupies passPct of 100
    $("donut-pass").setAttribute("stroke-dasharray", `${passPct.toFixed(2)} ${(100 - passPct).toFixed(2)}`);
    $("donut-rej").setAttribute("stroke-dasharray",  `${rejPct.toFixed(2)} ${(100 - rejPct).toFixed(2)}`);
    $("donut-rej").setAttribute("stroke-dashoffset", `${(-passPct).toFixed(2)}`);
    $("donut-center").textContent = (total ? passPct.toFixed(0) : 0) + "%";

    $("legend-pass").textContent = pass.toLocaleString();
    $("legend-rej").textContent  = rej.toLocaleString();
    $("bar-pass").style.width = passPct + "%";
    $("bar-rej").style.width  = rejPct + "%";

    // defect breakdown
    const total_rej = rej || 1;
    const list = Brew.DEFECT_TYPES.map(d => {
      const c = s.rejects[d.key] || 0;
      const pct = (c / total_rej) * 100;
      return `<div>
        <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
          <span style="font-size:13px;">${d.label}</span>
          <span class="mono" style="font-size:12px; color:var(--ink-cream-2)">${c} <small style="color:var(--ink-mute)">(${pct.toFixed(1)}%)</small></span>
        </div>
        <div class="bar bar--bad"><span style="width:${pct}%"></span></div>
      </div>`;
    }).join("");
    $("defect-list").innerHTML = list;

    // history
    $("qc-history-body").innerHTML = s.history.length
      ? s.history.map(h => `<tr>
          <td class="mono">${h.id}</td>
          <td><span class="tag ${h.status === "PASS" ? "tag--good" : "tag--bad"}">${h.status}</span></td>
          <td>${h.reason}</td>
          <td class="mono" style="color:var(--ink-mute)">${h.ts}</td>
        </tr>`).join("")
      : `<tr><td colspan="4" style="color:var(--ink-mute); text-align:center; padding:24px">No products yet. Visit Production to start the line.</td></tr>`;
  }
  Brew.subscribe(render);
})();

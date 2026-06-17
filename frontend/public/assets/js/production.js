(function () {
  const $ = (id) => document.getElementById(id);

  $("btn-start").addEventListener("click", () => Brew.start());
  $("btn-stop").addEventListener("click", () => Brew.stop());
  $("btn-reset").addEventListener("click", () => { if (confirm("Reset all counters?")) Brew.reset(); });
  $("btn-estop").addEventListener("click", () => {
    if (Brew.state.eStop) Brew.releaseEStop();
    else Brew.eStop();
  });

  $("speed-slider").addEventListener("input", (e) => {
    Brew.setSpeed(e.target.value);
    $("speed-val").textContent = e.target.value;
  });
  $("defect-slider").addEventListener("input", (e) => {
    Brew.setDefectRate(e.target.value / 100);
    $("defect-val").textContent = (+e.target.value).toFixed(1);
  });
  document.querySelectorAll("[data-defect]").forEach((b) =>
    b.addEventListener("click", () => Brew.triggerDefect(b.getAttribute("data-defect")))
  );

  // ===== capsule animation engine =====
  const conveyor = document.getElementById("conveyor");
  const stageBar = document.getElementById("line-stage-bar");
  const stages = [6, 23, 40, 57, 74]; // % left positions for stages 1..5

  /** active capsules: { el, x, stage, defect, born } */
  const capsules = [];
  let lastSpawn = 0;

  function spawn(defectKind) {
    const el = document.createElement("div");
    el.className = "capsule";
    el.style.left = "2%";
    el.setAttribute("data-stage", "1");
    if (defectKind) {
      el.setAttribute("data-defect", "true");
      el.title = defectKind;
    }
    conveyor.appendChild(el);
    capsules.push({ el, x: 2, stage: 1, defect: defectKind || null, born: Date.now() });
  }

  function step() {
    const s = Brew.state;
    const running = s.running && !s.eStop;
    conveyor.setAttribute("data-running", running ? "true" : "false");

    if (running) {
      const dx = (s.speed / 60) * (16 / 60); // px-ish per frame; speed in cpm
      const now = Date.now();
      const interval = Math.max(800, 6000 / Math.max(1, s.speed)); // ms between spawns
      if (now - lastSpawn > interval) {
        lastSpawn = now;
        const isDefect = Math.random() < s.targetDefectRate;
        spawn(isDefect ? "defect" : null);
      }

      capsules.forEach((c) => {
        c.x += dx * 6; // visual move
        // update stage indicator based on x position
        let st = 1;
        for (let i = 0; i < stages.length; i++) if (c.x >= stages[i]) st = i + 1;
        if (st !== c.stage) {
          c.stage = st;
          c.el.setAttribute("data-stage", String(st));
        }
        c.el.style.left = c.x + "%";

        // route defect to reject lane after stage 5
        if (c.x > 84 && c.defect) {
          c.el.style.bottom = `${110 + Math.random() * 50}px`;
          c.el.style.left = `${90 + Math.random() * 4}%`;
        }
      });

      // cleanup off-screen
      for (let i = capsules.length - 1; i >= 0; i--) {
        if (capsules[i].x > 100) {
          capsules[i].el.remove();
          capsules.splice(i, 1);
        }
      }
    }

    // update machines
    document.querySelectorAll(".machine").forEach((m, i) => {
      const stage = i + 1;
      let st = running ? "run" : "stop";
      if (running && s.targetDefectRate > 0.08 && stage === 3) st = "warn";
      m.setAttribute("data-state", st);
    });

    // update active stage indicator
    if (stageBar) {
      const activeStage = running ? Math.floor((Date.now() / 700) % 5) + 1 : 0;
      stageBar.querySelectorAll(".line-stage").forEach((el) => {
        el.setAttribute("data-active", el.getAttribute("data-stage") == activeStage ? "true" : "false");
      });
    }

    // labels
    const lbl = document.getElementById("line-state-label");
    if (lbl) lbl.textContent = s.eStop ? "EMERGENCY STOP" : (s.running ? "RUNNING" : "IDLE");

    requestAnimationFrame(step);
  }
  requestAnimationFrame(step);

  // ===== KPI rendering =====
  function render(s) {
    document.getElementById("kpi-produced").textContent = s.produced.toLocaleString();
    document.getElementById("kpi-defective").textContent = s.defective.toLocaleString();
    document.getElementById("kpi-efficiency").textContent = Brew.efficiency() + "%";
    document.getElementById("kpi-speed").textContent = s.speed;

    const speedSlider = document.getElementById("speed-slider");
    if (document.activeElement !== speedSlider) {
      speedSlider.value = s.speed;
      document.getElementById("speed-val").textContent = s.speed;
    }
    const defectSlider = document.getElementById("defect-slider");
    if (document.activeElement !== defectSlider) {
      defectSlider.value = Math.round(s.targetDefectRate * 100);
      document.getElementById("defect-val").textContent = (s.targetDefectRate * 100).toFixed(1);
    }

    // recent table
    const body = document.getElementById("recent-body");
    body.innerHTML = s.history.slice(0, 20).map(h => `
      <tr>
        <td class="mono">${h.id}</td>
        <td><span class="tag ${h.status === "PASS" ? "tag--good" : "tag--bad"}">${h.status}</span></td>
        <td>${h.reason}</td>
        <td class="mono" style="color:var(--ink-mute)">${h.ts}</td>
      </tr>
    `).join("") || `<tr><td colspan="4" style="color:var(--ink-mute); text-align:center; padding:24px">No products produced yet — press ▶ Start.</td></tr>`;
  }
  Brew.subscribe(render);
})();

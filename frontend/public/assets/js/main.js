/* ============================================================
 * BrewLine — shared utilities
 * ============================================================ */
(function () {
  "use strict";

  // mobile nav toggle
  const burger = document.getElementById("nav-burger");
  const links = document.querySelector(".nav__links");
  if (burger && links) {
    burger.addEventListener("click", () => links.classList.toggle("open"));
  }

  // animate "rise" elements
  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          e.target.classList.add("rise");
          io.unobserve(e.target);
        }
      });
    },
    { threshold: 0.12 }
  );
  document.querySelectorAll("[data-rise]").forEach((el, i) => {
    el.style.animationDelay = `${i * 0.05}s`;
    io.observe(el);
  });

  // ===== shared shop-floor simulator (persisted in localStorage) =====
  // single source of truth so multiple pages can co-operate
  const KEY = "brewline_state_v1";
  const DEFAULT_STATE = {
    running: false,
    eStop: false,
    speed: 12,          // capsules / min
    targetDefectRate: 0.03,
    produced: 0,
    defective: 0,
    rejects: { underfill: 0, overfill: 0, seal: 0, shell: 0, pack: 0 },
    temperature: 92,     // °C sealer
    pressure: 4.2,       // bar piston
    runtimeSec: 0,
    machineHealth: { loader: 96, filler: 91, sealer: 88, packer: 94, inspector: 97 },
    alarms: [],
    history: [],         // recent products (last 50)
    metricsSeries: [],   // time series for charts
    repairLog: [],
    lastTick: Date.now()
  };

  function load() {
    try {
      const raw = localStorage.getItem(KEY);
      if (!raw) return structuredClone(DEFAULT_STATE);
      const parsed = JSON.parse(raw);
      return { ...structuredClone(DEFAULT_STATE), ...parsed };
    } catch (e) {
      return structuredClone(DEFAULT_STATE);
    }
  }
  function save(s) { try { localStorage.setItem(KEY, JSON.stringify(s)); } catch (e) {} }

  const state = load();
  state.lastTick = Date.now();

  const subscribers = new Set();
  function notify() { subscribers.forEach((fn) => { try { fn(state); } catch (e) {} }); }

  const DEFECT_TYPES = [
    { key: "underfill", label: "Underfilled capsule", weight: 0.30, sev: "warn" },
    { key: "overfill",  label: "Overfilled capsule",  weight: 0.18, sev: "warn" },
    { key: "seal",      label: "Seal failure",        weight: 0.22, sev: "bad"  },
    { key: "shell",     label: "Damaged shell",       weight: 0.14, sev: "bad"  },
    { key: "pack",      label: "Packaging failure",   weight: 0.16, sev: "warn" }
  ];

  function pickDefect() {
    const r = Math.random();
    let acc = 0;
    for (const d of DEFECT_TYPES) {
      acc += d.weight;
      if (r <= acc) return d;
    }
    return DEFECT_TYPES[0];
  }

  function nowStr() {
    const d = new Date();
    return d.toLocaleTimeString("en-GB", { hour12: false });
  }

  function pushAlarm(sev, msg) {
    state.alarms.unshift({ ts: nowStr(), sev, msg });
    if (state.alarms.length > 40) state.alarms.length = 40;
  }

  function newProductId() {
    const n = (state.produced + 1).toString().padStart(6, "0");
    return `CAP-${new Date().toISOString().slice(0,10).replace(/-/g,"")}-${n}`;
  }

  // global API
  const Brew = {
    state,
    DEFECT_TYPES,
    subscribe(fn) { subscribers.add(fn); fn(state); return () => subscribers.delete(fn); },
    save() { save(state); },
    start() {
      if (state.eStop) { pushAlarm("bad", "Cannot start — E-Stop engaged"); notify(); return; }
      state.running = true;
      pushAlarm("info", "Line started");
      notify(); save(state);
    },
    stop() {
      state.running = false;
      pushAlarm("warn", "Line stopped");
      notify(); save(state);
    },
    eStop() {
      state.running = false; state.eStop = true;
      pushAlarm("bad", "EMERGENCY STOP engaged");
      notify(); save(state);
    },
    releaseEStop() {
      state.eStop = false;
      pushAlarm("info", "E-Stop released");
      notify(); save(state);
    },
    reset() {
      const fresh = structuredClone(DEFAULT_STATE);
      Object.keys(fresh).forEach(k => state[k] = fresh[k]);
      pushAlarm("info", "Counters reset");
      notify(); save(state);
    },
    setSpeed(v) { state.speed = Math.max(1, Math.min(60, +v || 12)); notify(); save(state); },
    setDefectRate(v) {
      state.targetDefectRate = Math.max(0, Math.min(0.5, +v || 0));
      notify(); save(state);
    },
    triggerDefect(kind) {
      const t = DEFECT_TYPES.find(d => d.key === kind) || pickDefect();
      state.defective += 1;
      state.rejects[t.key] = (state.rejects[t.key] || 0) + 1;
      pushAlarm(t.sev, `${t.label} detected on the line`);
      state.history.unshift({ id: newProductId(), status: "REJECT", reason: t.label, ts: nowStr() });
      if (state.history.length > 50) state.history.length = 50;
      notify(); save(state);
    },
    logRepair(machine, note) {
      state.repairLog.unshift({ ts: nowStr(), machine, note });
      if (state.repairLog.length > 30) state.repairLog.length = 30;
      // boost health a bit
      if (state.machineHealth[machine] !== undefined) {
        state.machineHealth[machine] = Math.min(100, state.machineHealth[machine] + 5);
      }
      pushAlarm("info", `Maintenance logged — ${machine}: ${note}`);
      notify(); save(state);
    }
  };
  window.Brew = Brew;

  // master tick loop (1 Hz) — drives counters / sensors regardless of page
  setInterval(() => {
    const dt = (Date.now() - state.lastTick) / 1000;
    state.lastTick = Date.now();

    // sensor drift
    const tempTarget = state.running ? 94 : 78;
    state.temperature += (tempTarget - state.temperature) * 0.08 + (Math.random() - 0.5) * 0.6;
    const presTarget = state.running ? 4.5 : 1.2;
    state.pressure += (presTarget - state.pressure) * 0.1 + (Math.random() - 0.5) * 0.15;

    if (state.running && !state.eStop) {
      state.runtimeSec += dt;
      // produce capsules based on speed (per minute)
      const perSec = state.speed / 60;
      const expected = perSec * dt + (Math.random() < (perSec * dt) % 1 ? 0 : 0);
      const make = Math.floor(perSec * dt + Math.random() * 0.6);
      for (let i = 0; i < make; i++) {
        const isDefect = Math.random() < state.targetDefectRate;
        state.produced += 1;
        const pid = newProductId();
        if (isDefect) {
          const t = pickDefect();
          state.defective += 1;
          state.rejects[t.key] = (state.rejects[t.key] || 0) + 1;
          state.history.unshift({ id: pid, status: "REJECT", reason: t.label, ts: nowStr() });
          if (Math.random() < 0.25) pushAlarm(t.sev, `${t.label} — ${pid}`);
        } else {
          state.history.unshift({ id: pid, status: "PASS", reason: "—", ts: nowStr() });
        }
        if (state.history.length > 50) state.history.length = 50;
      }

      // health decay
      for (const k of Object.keys(state.machineHealth)) {
        if (Math.random() < 0.06) {
          state.machineHealth[k] = Math.max(40, state.machineHealth[k] - Math.random() * 0.25);
        }
      }
    }

    // metric history (~60 points)
    state.metricsSeries.push({
      t: Date.now(),
      produced: state.produced,
      defective: state.defective,
      temp: state.temperature,
      pres: state.pressure,
      eff: efficiency(state)
    });
    if (state.metricsSeries.length > 60) state.metricsSeries.shift();

    save(state);
    notify();
  }, 1000);

  function efficiency(s) {
    if (s.produced === 0) return 0;
    const yieldRate = (s.produced - s.defective) / Math.max(1, s.produced);
    const speedRatio = Math.min(1, s.speed / 15);
    return Math.round(yieldRate * 0.7 * 100 + speedRatio * 0.3 * 100);
  }
  Brew.efficiency = () => efficiency(state);

  // tiny canvas sparkline helper
  Brew.spark = function (canvas, getSeries, color = "#c8763a") {
    if (!canvas) return;
    function draw() {
      const ctx = canvas.getContext("2d");
      const w = canvas.width, h = canvas.height;
      ctx.clearRect(0, 0, w, h);
      const series = getSeries();
      if (!series || series.length < 2) return;
      const min = Math.min(...series);
      const max = Math.max(...series);
      const range = max - min || 1;
      ctx.beginPath();
      series.forEach((v, i) => {
        const x = (i / (series.length - 1)) * (w - 4) + 2;
        const y = h - ((v - min) / range) * (h - 8) - 4;
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
      });
      const grad = ctx.createLinearGradient(0, 0, 0, h);
      grad.addColorStop(0, color + "cc");
      grad.addColorStop(1, color + "00");
      ctx.lineTo(w - 2, h - 2);
      ctx.lineTo(2, h - 2);
      ctx.closePath();
      ctx.fillStyle = grad;
      ctx.fill();
      ctx.beginPath();
      series.forEach((v, i) => {
        const x = (i / (series.length - 1)) * (w - 4) + 2;
        const y = h - ((v - min) / range) * (h - 8) - 4;
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
      });
      ctx.strokeStyle = color;
      ctx.lineWidth = 1.6;
      ctx.stroke();
    }
    draw();
    Brew.subscribe(draw);
  };

  // clock
  function tickClock() {
    const el = document.getElementById("hero-clock");
    if (el) el.textContent = nowStr();
  }
  setInterval(tickClock, 1000); tickClock();
})();

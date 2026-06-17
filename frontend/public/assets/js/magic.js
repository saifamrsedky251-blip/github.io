/* Magic Survival page interactions */
(function () {
  // mobile nav
  const burger = document.getElementById("nav-burger");
  const links = document.querySelector(".m-nav__links");
  if (burger && links) burger.addEventListener("click", () => links.classList.toggle("open"));

  // play buttons → control corresponding <audio>
  document.querySelectorAll(".m-play").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      const key = btn.getAttribute("data-audio");
      const audio = document.getElementById("audio-" + key);
      if (!audio) return;
      // stop all other audios so they don't overlap
      document.querySelectorAll("audio").forEach((a) => { if (a !== audio) { a.pause(); a.currentTime = 0; } });
      if (audio.paused) {
        audio.currentTime = 0;
        audio.play().catch(() => {});
        btn.textContent = "■ Stop";
      } else {
        audio.pause();
        audio.currentTime = 0;
        btn.textContent = btn.classList.contains("m-play--inline") ? "▶ this" : "▶ Sample";
      }
      audio.onended = () => {
        btn.textContent = btn.classList.contains("m-play--inline") ? "▶ this" : "▶ Sample";
      };
    });
  });

  // STARFIELD canvas
  const canvas = document.getElementById("stars");
  if (canvas) {
    const ctx = canvas.getContext("2d");
    let stars = [];
    let raf;
    function resize() {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      const n = Math.floor((canvas.width * canvas.height) / 9000);
      stars = Array.from({ length: n }, () => ({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        r: Math.random() * 1.4 + 0.2,
        s: Math.random() * 0.05 + 0.02,
        a: Math.random() * Math.PI * 2,
        c: Math.random() < 0.08
          ? "rgba(196,181,253,0.9)"
          : (Math.random() < 0.5 ? "rgba(255,255,255,0.8)" : "rgba(34,211,238,0.7)")
      }));
    }
    function tick() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      for (const s of stars) {
        s.a += s.s;
        const op = 0.4 + Math.sin(s.a) * 0.4;
        ctx.beginPath();
        ctx.fillStyle = s.c.replace(/[0-9.]+\)/, op.toFixed(2) + ")");
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        ctx.fill();
      }
      raf = requestAnimationFrame(tick);
    }
    resize(); tick();
    window.addEventListener("resize", () => { cancelAnimationFrame(raf); resize(); tick(); });
  }

  // intersection-observer reveal
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) {
        e.target.style.opacity = "1";
        e.target.style.transform = "translateY(0)";
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.15 });
  document.querySelectorAll(".m-class, .m-control, .m-ability, .m-card").forEach((el, i) => {
    el.style.opacity = "0";
    el.style.transform = "translateY(18px)";
    el.style.transition = `opacity .7s ease ${i * 0.06}s, transform .7s cubic-bezier(.2,.7,.2,1) ${i * 0.06}s`;
    io.observe(el);
  });
})();

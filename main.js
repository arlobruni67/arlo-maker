(() => {
  const apps = window.ARLO_APPS || [];
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const arrow = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>';
  const check = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>';

  /* ---------- theme ---------- */
  const root = document.documentElement;
  const isDark = () => root.dataset.theme ? root.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
  $("#themeBtn").addEventListener("click", () => {
    const next = isDark() ? "light" : "dark";
    const apply = () => { root.dataset.theme = next; try { localStorage.setItem("arlo-theme", next); } catch (e) {} };
    if (document.startViewTransition && !reduced) document.startViewTransition(apply); else apply();
  });

  /* ---------- counts from data ---------- */
  const n = apps.length;
  $("#appCountPill").textContent = `${n} app${n === 1 ? "" : "s"}`;
  $("#statApps").dataset.count = n;
  const langs = new Set(apps.flatMap((a) => a.tech).filter((t) => ["Python", "C#", "Rust", "C++", "JavaScript", "TypeScript", "Go"].includes(t)));
  $$(".stat b")[1].dataset.count = langs.size;
  $("#year").textContent = new Date().getFullYear();

  /* ---------- hero icons ---------- */
  const stack = $("#heroStack");
  apps.slice(0, 3).forEach((a) => {
    const d = document.createElement("div");
    d.className = "float-icon";
    d.innerHTML = `<img src="${a.icon}" alt="">${a.badge ? `<span class="badge-rs">${esc(a.badge)}</span>` : ""}`;
    d.addEventListener("click", () => openApp(a.id));
    stack.appendChild(d);
  });

  /* ---------- typed words ---------- */
  const words = ["video editors", "screen recorders", "game capture tools", "fast Windows apps", "things that never drop frames"];
  const typed = $("#typed");
  if (!reduced) {
    let wi = 0, ci = words[0].length, del = true;
    const tick = () => {
      const w = words[wi];
      ci += del ? -1 : 1;
      typed.textContent = w.slice(0, ci);
      let wait = del ? 35 : 70;
      if (!del && ci === w.length) { del = true; wait = 1800; }
      else if (del && ci === 0) { del = false; wi = (wi + 1) % words.length; wait = 300; }
      setTimeout(tick, wait);
    };
    setTimeout(tick, 2200);
  }

  /* ---------- bubbles canvas ---------- */
  const cv = $("#bubbles"), cx = cv.getContext("2d");
  let W = 0, H = 0, dots = [], mouse = { x: -999, y: -999 };
  const resize = () => {
    const dpr = Math.min(devicePixelRatio || 1, 2);
    W = cv.clientWidth; H = cv.clientHeight;
    cv.width = W * dpr; cv.height = H * dpr; cx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const count = Math.round(Math.min(46, W / 28));
    dots = Array.from({ length: count }, () => ({
      x: Math.random() * W, y: Math.random() * H, r: 3 + Math.random() * 16,
      vy: .15 + Math.random() * .45, ph: Math.random() * 6.28, vx: 0, ox: 0
    }));
  };
  resize(); addEventListener("resize", resize);
  cv.parentElement.addEventListener("pointermove", (e) => { const b = cv.getBoundingClientRect(); mouse = { x: e.clientX - b.left, y: e.clientY - b.top }; });
  cv.parentElement.addEventListener("pointerleave", () => (mouse = { x: -999, y: -999 }));
  let heroVisible = true;
  new IntersectionObserver(([e]) => (heroVisible = e.isIntersecting)).observe(cv);
  const draw = (t) => {
    if (heroVisible) {
      cx.clearRect(0, 0, W, H);
      const dark = isDark();
      for (const d of dots) {
        d.y -= d.vy; d.ph += .01;
        const dx = d.x + d.ox - mouse.x, dy = d.y - mouse.y, dist = Math.hypot(dx, dy);
        if (dist < 120) d.vx += (dx / (dist || 1)) * .6;
        d.vx *= .92; d.ox += d.vx; d.ox *= .98;
        if (d.y < -30) { d.y = H + 30; d.x = Math.random() * W; }
        const x = d.x + d.ox + Math.sin(d.ph) * 12;
        const g = cx.createRadialGradient(x - d.r * .3, d.y - d.r * .3, 0, x, d.y, d.r);
        g.addColorStop(0, dark ? "rgba(169,220,245,.35)" : "rgba(255,255,255,.95)");
        g.addColorStop(1, dark ? "rgba(137,207,240,.06)" : "rgba(137,207,240,.35)");
        cx.fillStyle = g; cx.beginPath(); cx.arc(x, d.y, d.r, 0, 6.283); cx.fill();
      }
    }
    if (!reduced) requestAnimationFrame(draw);
  };
  requestAnimationFrame(draw);

  // blobs drift toward the pointer
  const blobs = $$(".blob");
  addEventListener("pointermove", (e) => {
    if (reduced) return;
    const px = e.clientX / innerWidth - .5, py = e.clientY / innerHeight - .5;
    blobs.forEach((b, i) => (b.style.transform = `translate(${px * (40 + i * 30)}px, ${py * (40 + i * 30)}px)`));
  });

  /* ---------- scroll: progress bar, nav, timeline ---------- */
  const bar = $("#scrollBar"), nav = $("#nav"), tl = $("#timeline");
  const links = $$(".nav-links a"), secs = links.map((a) => $(a.getAttribute("href")));
  const onScroll = () => {
    const max = document.documentElement.scrollHeight - innerHeight;
    bar.style.transform = `scaleX(${max > 0 ? scrollY / max : 0})`;
    nav.classList.toggle("small", scrollY > 40);
    const r = tl.getBoundingClientRect();
    const p = Math.min(1, Math.max(0, (innerHeight * .75 - r.top) / r.height));
    tl.style.setProperty("--tl", p);
    let cur = -1;
    secs.forEach((s, i) => { if (s && s.getBoundingClientRect().top < innerHeight * .4) cur = i; });
    links.forEach((a, i) => a.classList.toggle("on", i === cur));
  };
  addEventListener("scroll", onScroll, { passive: true }); onScroll();

  /* ---------- reveal + count up ---------- */
  const countUp = (el) => {
    const end = +el.dataset.count;
    if (reduced || end === 0) { el.textContent = end; return; }
    const t0 = performance.now(), dur = 1400;
    const step = (t) => {
      const k = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - k, 4);
      el.textContent = Math.round(end * e);
      if (k < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };
  const io = new IntersectionObserver((entries) => {
    entries.forEach((en) => {
      if (!en.isIntersecting) return;
      const el = en.target;
      setTimeout(() => el.classList.add("in"), (+el.dataset.delay || 0));
      const c = el.querySelector("[data-count]"); if (c) countUp(c);
      io.unobserve(el);
    });
  }, { threshold: .15 });
  const watch = () => {
    $$(".reveal:not(.in)").forEach((el) => {
      const sibs = [...el.parentElement.children].filter((c) => c.classList.contains("reveal"));
      el.dataset.delay = Math.max(0, sibs.indexOf(el)) * 90;
      io.observe(el);
    });
  };
  watch();

  /* ---------- app grid ---------- */
  const grid = $("#grid");
  const highlight = (text, q) => {
    const safe = esc(text);
    if (!q) return safe;
    const re = new RegExp(`(${q.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "ig");
    return safe.replace(re, "<mark>$1</mark>");
  };
  const render = (q = "") => {
    grid.innerHTML = "";
    apps.forEach((a, i) => {
      const card = document.createElement("button");
      card.className = "card";
      card.dataset.id = a.id;
      card.dataset.cat = a.category;
      card.style.setProperty("--i", i);
      const shot = a.shots[0];
      card.innerHTML = `
        <div class="card-shot ${shot ? "" : "empty"}">
          <img src="${shot ? shot.src : a.icon}" alt="" loading="lazy">
        </div>
        <div class="card-body">
          <div class="card-top">
            <div class="app-icon"><img src="${a.icon}" alt="">${a.badge ? `<span class="badge-rs">${esc(a.badge)}</span>` : ""}</div>
            <span class="status ${a.status}">${esc(a.statusLabel)}</span>
          </div>
          <h3>${highlight(a.name, q)}</h3>
          <p>${highlight(a.tagline, q)}</p>
          <div class="tags">${a.tech.map((t) => `<span class="tag">${highlight(t, q)}</span>`).join("")}</div>
          <span class="card-more">See details ${arrow}</span>
        </div>`;
      card.setAttribute("aria-label", `${a.name}: ${a.tagline}`);
      card.addEventListener("click", () => openApp(a.id));
      card.addEventListener("animationend", () => (card.style.animation = "none"), { once: true });
      tilt(card);
      grid.appendChild(card);
    });
  };
  const tilt = (el) => {
    if (reduced || matchMedia("(hover: none)").matches) return;
    el.addEventListener("pointermove", (e) => {
      const b = el.getBoundingClientRect();
      const x = (e.clientX - b.left) / b.width, y = (e.clientY - b.top) / b.height;
      el.style.transform = `rotateX(${(.5 - y) * 10}deg) rotateY(${(x - .5) * 12}deg) translateY(-6px)`;
      el.style.setProperty("--mx", `${x * 100}%`);
      el.style.setProperty("--my", `${y * 100}%`);
    });
    el.addEventListener("pointerleave", () => (el.style.transform = ""));
  };

  // filter + search
  let filter = "all", query = "";
  const apply = () => {
    const q = query.trim().toLowerCase();
    render(query.trim());
    let shown = 0;
    $$(".card", grid).forEach((c) => {
      const a = apps.find((x) => x.id === c.dataset.id);
      const hay = [a.name, a.tagline, a.description, ...a.tech, ...a.features].join(" ").toLowerCase();
      const ok = (filter === "all" || a.category === filter) && (!q || hay.includes(q));
      c.classList.toggle("hide", !ok);
      if (ok) c.style.setProperty("--i", shown++);
    });
    $("#empty").hidden = shown > 0;
  };
  const chips = $$(".chip"), glider = $("#glider");
  const moveGlider = () => {
    const a = $(".chip.active");
    glider.style.width = a.offsetWidth + "px";
    glider.style.transform = `translateX(${a.offsetLeft}px)`;
  };
  chips.forEach((c) => c.addEventListener("click", () => {
    chips.forEach((x) => { x.classList.toggle("active", x === c); x.setAttribute("aria-selected", x === c); });
    filter = c.dataset.filter; moveGlider(); apply();
  }));
  let st;
  $("#search").addEventListener("input", (e) => { query = e.target.value; clearTimeout(st); st = setTimeout(apply, 120); });
  addEventListener("resize", moveGlider);
  document.fonts && document.fonts.ready.then(moveGlider);
  apply(); moveGlider();

  /* ---------- downloads ---------- */
  const lic = window.ARLO_LICENSE || {};
  const dlIcon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5M5 20h14"/></svg>';
  // local preview serves the zips from downloads/; online they come from the GitHub release
  const online = /github\.io$/.test(location.hostname) && window.ARLO_RELEASE;
  const fileUrl = (f) => (online ? window.ARLO_RELEASE + f.split("/").pop() : f);
  const manifest = fetch("downloads/manifest.json").then((r) => (r.ok ? r.json() : {})).catch(() => ({}));
  const fmt = (b) => (b ? (b >= 1e6 ? (b / 1e6).toFixed(1) + " MB" : Math.max(1, Math.round(b / 1e3)) + " KB") : "");
  const fileSize = (f) => manifest.then((m) => fmt(m[f.split("/").pop()]));
  const fillSizes = (scope) => $$("[data-size]", scope).forEach((el) =>
    fileSize(el.dataset.size).then((s) => { el.textContent = s; el.hidden = !s; }));
  const dlButtons = (a) => (a.downloads || []).map((d) => `
    <a class="btn ${d.kind === "app" ? "primary" : "ghost"} dl" href="${fileUrl(d.file)}" download>
      ${dlIcon}<span>${esc(d.label)}</span><small class="size" data-size="${d.file}" hidden></small>
    </a>`).join("");
  $("#dlGrid").innerHTML = apps.filter((a) => a.downloads && a.downloads.length).map((a) => `
    <article class="dl-card reveal">
      <div class="app-icon"><img src="${a.icon}" alt=""></div>
      <div class="dl-info">
        <h3>${esc(a.name)}</h3>
        <p>${a.tech.map(esc).join(" · ")}</p>
      </div>
      <div class="dl-btns">${dlButtons(a)}</div>
    </article>`).join("");
  fillSizes($("#dlGrid"));
  $("#licenseText").textContent = `${lic.summary || ""} Licence: ${lic.name || ""}.`;
  $("#licenseLink").href = lic.file || "#";
  watch();

  /* ---------- modal ---------- */
  const modal = $("#modal");
  let current = null, shotIdx = 0, lastFocus = null;
  const showShot = (i) => {
    if (!current || !current.shots.length) return;
    shotIdx = (i + current.shots.length) % current.shots.length;
    const s = current.shots[shotIdx], img = $("#mImg");
    img.classList.add("swap");
    setTimeout(() => { img.src = s.src; img.alt = s.caption; $("#mCaption").textContent = s.caption; img.classList.remove("swap"); }, reduced ? 0 : 180);
    $$("#mThumbs button").forEach((b, k) => b.classList.toggle("on", k === shotIdx));
  };
  function openApp(id) {
    const a = apps.find((x) => x.id === id); if (!a) return;
    current = a; lastFocus = document.activeElement;
    $("#mIcon").innerHTML = `<img src="${a.icon}" alt="">${a.badge ? `<span class="badge-rs">${esc(a.badge)}</span>` : ""}`;
    $("#mTitle").textContent = a.name;
    $("#mTagline").textContent = a.tagline;
    $("#mMeta").innerHTML = `<span class="status ${a.status}">${esc(a.statusLabel)}</span>` + a.tech.map((t) => `<span class="tag">${esc(t)}</span>`).join("");
    $("#mDesc").textContent = a.description;
    $("#mDl").innerHTML = (a.downloads && a.downloads.length)
      ? `${dlButtons(a)}<span class="m-lic">Open source · <a href="${lic.file}" target="_blank" rel="noopener">${esc(lic.name || "")}</a> · ${esc(lic.short || "")}</span>`
      : "";
    fillSizes($("#mDl"));
    $("#mStats").innerHTML = a.stats.map((s) => `<div class="m-stat"><b>${esc(s.prefix || "")}<span data-count="${s.value}">0</span></b><span>${esc(s.label)}</span></div>`).join("");
    $("#mFeatures").innerHTML = a.features.map((f, i) => `<li style="--i:${i}">${check}<span>${esc(f)}</span></li>`).join("");
    const gal = $("#mGallery");
    gal.hidden = !a.shots.length;
    $("#mThumbs").innerHTML = a.shots.map((s, i) => `<button aria-label="Show ${esc(s.caption)}"><img src="${s.src}" alt=""></button>`).join("");
    $$("#mThumbs button").forEach((b, i) => b.addEventListener("click", () => showShot(i)));
    $("#mThumbs").hidden = a.shots.length < 2;
    $("#gPrev").hidden = $("#gNext").hidden = a.shots.length < 2;
    if (a.shots.length) { const s = a.shots[0]; $("#mImg").src = s.src; $("#mImg").alt = s.caption; $("#mCaption").textContent = s.caption; shotIdx = 0; $$("#mThumbs button")[0] && $$("#mThumbs button")[0].classList.add("on"); }
    modal.hidden = false; modal.classList.remove("closing");
    document.body.classList.add("lock");
    $(".modal-card").scrollTop = 0;
    $$("#mStats [data-count]").forEach((el) => { el.textContent = "0"; requestAnimationFrame(() => countUp(el)); });
    $(".modal-close").focus();
    history.replaceState(null, "", "#app/" + a.id);
  }
  const closeApp = () => {
    if (modal.hidden) return;
    modal.classList.add("closing");
    setTimeout(() => { modal.hidden = true; modal.classList.remove("closing"); }, reduced ? 0 : 240);
    document.body.classList.remove("lock");
    history.replaceState(null, "", location.pathname);
    lastFocus && lastFocus.focus({ preventScroll: true });
    current = null;
  };
  $$("[data-close]").forEach((el) => el.addEventListener("click", closeApp));
  $("#gPrev").addEventListener("click", () => showShot(shotIdx - 1));
  $("#gNext").addEventListener("click", () => showShot(shotIdx + 1));
  addEventListener("keydown", (e) => {
    if (modal.hidden) return;
    if (e.key === "Escape") closeApp();
    else if (e.key === "ArrowRight") showShot(shotIdx + 1);
    else if (e.key === "ArrowLeft") showShot(shotIdx - 1);
    else if (e.key === "Tab") {
      const f = $$("button:not([hidden]), a[href], input", $(".modal-card")).filter((x) => x.offsetParent);
      if (!f.length) return;
      if (e.shiftKey && document.activeElement === f[0]) { e.preventDefault(); f[f.length - 1].focus(); }
      else if (!e.shiftKey && document.activeElement === f[f.length - 1]) { e.preventDefault(); f[0].focus(); }
    }
  });
  // swipe between screenshots
  let sx = null;
  $(".m-stage").addEventListener("pointerdown", (e) => (sx = e.clientX));
  $(".m-stage").addEventListener("pointerup", (e) => { if (sx !== null && Math.abs(e.clientX - sx) > 50) showShot(shotIdx + (e.clientX < sx ? 1 : -1)); sx = null; });

  // deep link: index.html#app/ebs
  const m = location.hash.match(/^#app\/(.+)$/);
  if (m) openApp(m[1]);
})();

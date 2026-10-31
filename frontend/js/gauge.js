/* ---------- Risk gauge (speedometer style) ---------- */
function polarPoint(cx, cy, r, angleDeg) {
  const rad = (angleDeg * Math.PI) / 180;
  return { x: cx + r * Math.cos(rad), y: cy - r * Math.sin(rad) };
}

function describeArc(cx, cy, r, startAngle, endAngle) {
  const start = polarPoint(cx, cy, r, startAngle);
  const end = polarPoint(cx, cy, r, endAngle);
  const largeArc = startAngle - endAngle > 180 ? 1 : 0;
  return `M ${start.x.toFixed(2)} ${start.y.toFixed(2)} A ${r} ${r} 0 ${largeArc} 0 ${end.x.toFixed(2)} ${end.y.toFixed(2)}`;
}

/**
 * Renders a 0-100 speedometer gauge into `container`.
 * value: default probability percent (0 = safest, 100 = riskiest)
 */
function renderGauge(container, value) {
  const cx = 110,
    cy = 108,
    r = 88,
    needleLen = r - 24;
  const clamped = Math.max(0, Math.min(100, value));
  const targetAngle = 180 - (clamped / 100) * 180; // 180=safest(left), 0=riskiest(right)

  const svg = `
    <svg viewBox="0 0 220 140" width="100%" style="max-width:260px">
      <path d="${describeArc(cx, cy, r, 180, 135)}" stroke="var(--risk-low)" stroke-width="16" fill="none" stroke-linecap="round" opacity="0.9"/>
      <path d="${describeArc(cx, cy, r, 135, 90)}" stroke="var(--risk-medium)" stroke-width="16" fill="none" stroke-linecap="round" opacity="0.9"/>
      <path d="${describeArc(cx, cy, r, 90, 0)}" stroke="var(--risk-high)" stroke-width="16" fill="none" stroke-linecap="round" opacity="0.9"/>
      <line class="gauge-needle" x1="${cx}" y1="${cy}" x2="${cx}" y2="${cy}" stroke="#fff" stroke-width="3" stroke-linecap="round"/>
      <circle cx="${cx}" cy="${cy}" r="7" fill="#fff"/>
    </svg>
  `;
  container.innerHTML = svg;

  const needle = container.querySelector(".gauge-needle");
  const startAngle = 180; // begin resting in the safest position, sweep in on load
  const duration = 800;
  const startTime = performance.now();

  function easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3);
  }

  function tick(now) {
    const t = Math.min(1, (now - startTime) / duration);
    const angle = startAngle + (targetAngle - startAngle) * easeOutCubic(t);
    const tip = polarPoint(cx, cy, needleLen, angle);
    needle.setAttribute("x2", tip.x.toFixed(2));
    needle.setAttribute("y2", tip.y.toFixed(2));
    if (t < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

/* ---------- Donut chart (risk distribution) ---------- */
function renderDonut(container, segments) {
  // segments: [{label, value, color}]
  const total = segments.reduce((s, d) => s + d.value, 0) || 1;
  const cx = 70,
    cy = 70,
    r = 54,
    sw = 22;
  const circumference = 2 * Math.PI * r;
  let offset = 0;

  const arcs = segments
    .map((seg) => {
      const frac = seg.value / total;
      const dash = frac * circumference;
      const el = `<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${seg.color}" stroke-width="${sw}"
        stroke-dasharray="${dash} ${circumference - dash}" stroke-dashoffset="${-offset}"
        transform="rotate(-90 ${cx} ${cy})" stroke-linecap="butt"/>`;
      offset += dash;
      return el;
    })
    .join("");

  const legend = segments
    .map(
      (seg) => `
      <div style="display:flex;align-items:center;gap:8px;font-size:13px;color:var(--text-muted);margin-top:8px;">
        <span style="width:9px;height:9px;border-radius:50%;background:${seg.color};flex-shrink:0;"></span>
        ${seg.label} <span class="mono" style="margin-left:auto;color:var(--text);font-weight:600;">${seg.value}</span>
      </div>`
    )
    .join("");

  container.innerHTML = `
    <div style="display:flex;align-items:center;gap:22px;flex-wrap:wrap;">
      <svg viewBox="0 0 140 140" width="140" height="140">${arcs}</svg>
      <div style="flex:1;min-width:120px;">${legend}</div>
    </div>
  `;
}

/* ---------- Line chart (applications over time) ---------- */
function renderLineChart(container, points) {
  // points: [{label, value}]
  if (!points.length) {
    container.innerHTML = `<div class="empty-state"><p>No trend data yet.</p></div>`;
    return;
  }
  const w = 480,
    h = 180,
    padL = 10,
    padR = 10,
    padT = 16,
    padB = 28;
  const max = Math.max(...points.map((p) => p.value), 1);
  const stepX = (w - padL - padR) / Math.max(points.length - 1, 1);

  const coords = points.map((p, i) => {
    const x = padL + i * stepX;
    const y = padT + (1 - p.value / max) * (h - padT - padB);
    return { x, y, ...p };
  });

  const linePath = coords.map((c, i) => `${i === 0 ? "M" : "L"} ${c.x.toFixed(1)} ${c.y.toFixed(1)}`).join(" ");
  const areaPath = `${linePath} L ${coords[coords.length - 1].x.toFixed(1)} ${h - padB} L ${coords[0].x.toFixed(1)} ${h - padB} Z`;

  const dots = coords
    .map(
      (c) =>
        `<circle cx="${c.x.toFixed(1)}" cy="${c.y.toFixed(1)}" r="3.5" fill="var(--indigo)" stroke="#fff" stroke-width="1.5"/>`
    )
    .join("");

  const labels = coords
    .map(
      (c) =>
        `<text x="${c.x.toFixed(1)}" y="${h - 6}" font-size="10.5" fill="var(--text-faint)" text-anchor="middle" font-family="var(--font-mono)">${c.label}</text>`
    )
    .join("");

  container.innerHTML = `
    <svg viewBox="0 0 ${w} ${h}" width="100%" style="overflow:visible">
      <defs>
        <linearGradient id="lineFill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="var(--indigo)" stop-opacity="0.18"/>
          <stop offset="100%" stop-color="var(--indigo)" stop-opacity="0"/>
        </linearGradient>
      </defs>
      <path d="${areaPath}" fill="url(#lineFill)"/>
      <path d="${linePath}" fill="none" stroke="var(--indigo)" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"/>
      ${dots}
      ${labels}
    </svg>
  `;
}

/* ---------- Small horizontal factor bar (explainability) ---------- */
function factorBarColor(pct) {
  if (pct < 40) return "var(--risk-low)";
  if (pct < 70) return "var(--risk-medium)";
  return "var(--risk-high)";
}

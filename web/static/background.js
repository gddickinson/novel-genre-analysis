// Subtle animated background: a few slowly drifting branch-like strokes. Skipped under prefers-reduced-motion.
export function background(canvas) {
  if (!canvas || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const ctx = canvas.getContext('2d');
  const seeds = Array.from({ length: 7 }, (_, i) => ({ x: Math.random(), y: Math.random(), p: i * 1.7 }));
  const size = () => { canvas.width = innerWidth; canvas.height = innerHeight; };
  size();
  addEventListener('resize', size);
  const branch = (x, y, a, len, depth) => {
    if (depth === 0) return;
    const x2 = x + Math.cos(a) * len, y2 = y + Math.sin(a) * len;
    ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x2, y2); ctx.stroke();
    branch(x2, y2, a - 0.45, len * 0.72, depth - 1);
    branch(x2, y2, a + 0.45, len * 0.72, depth - 1);
  };
  const tick = t => {
    const { width: w, height: h } = canvas;
    ctx.clearRect(0, 0, w, h);
    ctx.lineWidth = 1;
    seeds.forEach((s, i) => {
      ctx.strokeStyle = i % 2 ? 'rgba(199,125,255,.16)' : 'rgba(245,196,81,.14)';
      branch(s.x * w, s.y * h, -Math.PI / 2 + Math.sin(t / 9000 + s.p) * 0.3, 60, 6);
    });
    if (!document.hidden) setTimeout(() => requestAnimationFrame(tick), 60); else setTimeout(() => requestAnimationFrame(tick), 600);
  };
  requestAnimationFrame(tick);
}

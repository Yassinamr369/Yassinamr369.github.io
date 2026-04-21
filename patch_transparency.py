with open('index copy.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update drawMethodPath to accept styling parameters
old_draw = """  function drawMethodPath(pts, color, progress, p) {
    if (!pts.length) return;
    const maxIdx = Math.floor(progress);
    const remainder = progress - maxIdx;

    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';"""

new_draw = """  function drawMethodPath(pts, color, progress, p, dash = [], lineWidth = 2) {
    if (!pts.length) return;
    const maxIdx = Math.floor(progress);
    const remainder = progress - maxIdx;

    ctx.save();
    ctx.globalAlpha = activeMethods.size > 1 ? 0.75 : 1.0; // 🔹 Makes overlap visible
    if(dash.length) ctx.setLineDash(dash);

    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = lineWidth;
    ctx.lineCap = 'round';"""

html = html.replace(old_draw, new_draw)

# also need to pop ctx.restore() at that end of drawMethodPath
old_draw_end = """      ctx.fillStyle = '#000';
      ctx.fill();
      ctx.lineWidth = 1.5;
      ctx.strokeStyle = color;
      ctx.stroke();
    }
  }"""
new_draw_end = """      ctx.fillStyle = '#000';
      ctx.fill();
      ctx.lineWidth = 1.5;
      ctx.strokeStyle = color;
      ctx.stroke();
    }
    ctx.restore();
  }"""
html = html.replace(old_draw_end, new_draw_end)


# 2. Update calls to add dash and width
old_calls = """    // Comparison methods (draw first, behind Euler)
    if (activeMethods.has('rk4') && pointsRK4.length)   drawMethodPath(pointsRK4,   '#a78bfa', progress, p);
    if (activeMethods.has('heun') && pointsHeun.length)  drawMethodPath(pointsHeun,  '#3b82f6', progress, p);"""

new_calls = """    // Comparison methods (draw first, behind Euler)
    // 🔹 Used distinctive dashing for easier identification
    if (activeMethods.has('rk4') && pointsRK4.length)   drawMethodPath(pointsRK4,   '#a78bfa', progress, p, [8, 4], 2.5);
    if (activeMethods.has('heun') && pointsHeun.length)  drawMethodPath(pointsHeun,  '#3b82f6', progress, p, [4, 4], 2);"""
html = html.replace(old_calls, new_calls)

# 3. Update Euler Path to respect transparency when multiple are on screen
old_euler = """    // Euler Path (primary, always on top)
    if (activeMethods.has('euler')) {
      ctx.beginPath();
      ctx.strokeStyle = Theme.euler;
      ctx.lineWidth = 2.5;"""

new_euler = """    // Euler Path (primary, always on top)
    if (activeMethods.has('euler')) {
      ctx.save();
      ctx.globalAlpha = activeMethods.size > 1 ? 0.9 : 1.0; // 🔹 Keep Euler slightly more prominent
      ctx.beginPath();
      ctx.strokeStyle = Theme.euler;
      ctx.lineWidth = 2.5;"""
html = html.replace(old_euler, new_euler)

# Add ctx.restore to Euler points end
old_euler_end = """      for (let i = 0; i <= maxIdx; i++) {
        const [cx, cy] = mapToCanvas(points[i].x, points[i].y, p);
        ctx.beginPath();
        ctx.arc(cx, cy, 4, 0, Math.PI * 2);
        ctx.fillStyle = '#000';
        ctx.fill();
        ctx.lineWidth = 2;
        ctx.strokeStyle = Theme.euler;
        ctx.stroke();
      }"""
new_euler_end = """      for (let i = 0; i <= maxIdx; i++) {
        const [cx, cy] = mapToCanvas(points[i].x, points[i].y, p);
        ctx.beginPath();
        ctx.arc(cx, cy, 4, 0, Math.PI * 2);
        ctx.fillStyle = '#000';
        ctx.fill();
        ctx.lineWidth = 2;
        ctx.strokeStyle = Theme.euler;
        ctx.stroke();
      }
      ctx.restore();"""
html = html.replace(old_euler_end, new_euler_end)

with open('index copy.html', 'w', encoding='utf-8') as f:
    f.write(html)

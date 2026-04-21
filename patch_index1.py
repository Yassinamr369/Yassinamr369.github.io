with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add button
html = html.replace('<button class="btn-secondary" id="btnReset">Clear</button>', 
                    '<button class="btn-secondary" id="btnReset">Clear</button>\n        <button class="btn-secondary" id="btnResetZoom" title="Reset Zoom and Panning position">Reset View</button>')

# 2. Add event listener
html = html.replace("document.getElementById('btnDefault').addEventListener('click', () => {", 
                    "document.getElementById('btnResetZoom').addEventListener('click', resetZoom);\n\n  document.getElementById('btnDefault').addEventListener('click', () => {")

# 3. Update renderFrame to use dashed and wide lines correctly for the selected method
html = html.replace('// Euler Path', '// Method Path')
html = html.replace('ctx.strokeStyle = Theme.euler;', 'ctx.strokeStyle = p.method === "rk4" ? Theme.rk4 : (p.method === "heun" ? Theme.heun : Theme.euler);')

old_euler_stroke = """    ctx.stroke();

    // Points
    for (let i = 0; i <= maxIdx; i++) {"""
new_euler_stroke = """    ctx.stroke();

    // Points
    for (let i = 0; i <= maxIdx; i++) {"""

# Actually I need to add ctx.setLineDash to the main render
old_render_part = """    ctx.beginPath();
    ctx.strokeStyle = p.method === "rk4" ? Theme.rk4 : (p.method === "heun" ? Theme.heun : Theme.euler);
    ctx.lineWidth = 2.5;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';"""
new_render_part = """    ctx.save();
    ctx.beginPath();
    let themeColor = p.method === "rk4" ? Theme.rk4 : (p.method === "heun" ? Theme.heun : Theme.euler);
    ctx.strokeStyle = themeColor;
    if (p.method === "rk4") ctx.setLineDash([8, 4]);
    else if (p.method === "heun") ctx.setLineDash([4, 4]);
    else ctx.setLineDash([]);
    ctx.lineWidth = p.method === 'rk4' ? 2.5 : 2;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';"""
html = html.replace(old_render_part, new_render_part)

old_point_render = """    // Points
    for (let i = 0; i <= maxIdx; i++) {
      const [cx, cy] = mapToCanvas(points[i].x, points[i].y, p);
      ctx.beginPath();
      ctx.arc(cx, cy, 4, 0, Math.PI * 2);
      ctx.fillStyle = '#000';
      ctx.fill();
      ctx.lineWidth = 2;
      ctx.strokeStyle = p.method === "rk4" ? Theme.rk4 : (p.method === "heun" ? Theme.heun : Theme.euler);
      ctx.stroke();
    }"""
new_point_render = """    // Points
    for (let i = 0; i <= maxIdx; i++) {
      const [cx, cy] = mapToCanvas(points[i].x, points[i].y, p);
      ctx.beginPath();
      ctx.arc(cx, cy, 4, 0, Math.PI * 2);
      ctx.fillStyle = '#000';
      ctx.fill();
      ctx.lineWidth = 1.5;
      ctx.strokeStyle = themeColor;
      ctx.stroke();
    }
    ctx.restore();"""
html = html.replace(old_point_render, new_point_render)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update CSS
css_add = """
  /* ─── NEW FEATURES ─────────────────────── */
  .presets-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }
  .btn-preset {
    background: rgba(255,255,255,0.05);
    border: 1px solid var(--border);
    color: var(--text-main);
    font-size: 10px;
    padding: 8px;
  }
  .btn-preset:hover {
    background: rgba(255,255,255,0.1);
    border-color: var(--text-muted);
  }
  .panel, .table-container {
    background: var(--bg-panel);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 20px;
    margin-top: 20px;
  }
  .table-container {
    max-height: 250px;
    overflow-y: auto;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    font-family: var(--font-mono);
    font-size: 12px;
  }
  th, td {
    padding: 8px;
    text-align: left;
    border-bottom: 1px solid var(--border);
  }
  th { color: var(--text-muted); position: sticky; top: 0; background: var(--bg-panel); }
  .err-small { color: var(--accent-green); }
  .err-large { color: var(--accent-red); }
  .row-highlight { background: rgba(255,255,255,0.1); }
  
  .tooltip {
    position: absolute;
    background: rgba(0,0,0,0.85);
    border: 1px solid var(--border);
    color: #fff;
    padding: 10px;
    border-radius: 8px;
    font-family: var(--font-mono);
    font-size: 11px;
    pointer-events: none;
    backdrop-filter: blur(4px);
    z-index: 100;
    transition: opacity 0.2s;
  }
  .explanation-panel p {
    font-size: 14px;
    color: var(--text-muted);
    margin-bottom: 8px;
    line-height: 1.5;
  }
  .math-rule {
    font-family: var(--font-mono);
    color: var(--accent-blue);
    background: rgba(59, 130, 246, 0.1);
    padding: 8px;
    border-radius: 4px;
    display: inline-block;
    margin: 8px 0;
  }
  .warning-text { color: var(--accent-red); font-weight: bold; margin-top: 10px; }
  .color-euler { color: var(--euler-color, #ffffff); }
  .color-heun { color: var(--accent-blue); }
  .color-rk4 { color: var(--accent-purple); }
"""
html = html.replace('/* ─── APP SECTION ──────────────────────── */', css_add + '\n  /* ─── APP SECTION ──────────────────────── */')

# 2. Add Presets and Method Selector in Sidebar
sidebar_addition = """
      <h3 class="section-title">Equation Presets</h3>
      <div class="presets-grid" style="margin-bottom: 24px;">
        <button class="btn-preset" onclick="setPreset('linear')">1. Linear ODE</button>
        <button class="btn-preset" onclick="setPreset('exponential')">2. Exp. Growth</button>
        <button class="btn-preset" onclick="setPreset('logistic')">3. Logistic Growth</button>
        <button class="btn-preset" onclick="setPreset('physics')">4. Free Fall</button>
        <button class="btn-preset" onclick="setPreset('decay')">5. Fluid/Decay</button>
        <button class="btn-preset" onclick="setPreset('advanced')" title="Advanced (and feel free to add more meaningful or interesting models beyond this list)">6. Complex (e^ix)</button>
      </div>

      <h3 class="section-title">Parameters</h3>
"""
html = html.replace('<h3 class="section-title">Parameters</h3>', sidebar_addition)

method_field = """
        <div class="field full">
          <label>Solver Method</label>
          <select id="method-select" style="width: 100%; background: rgba(255, 255, 255, 0.03); border: 1px solid var(--border); border-radius: 8px; color: var(--text-main); font-family: var(--font-mono); font-size: 13px; padding: 10px 12px; outline: none;">
            <option value="euler">Euler Method</option>
            <option value="heun">Improved Euler (Heun)</option>
            <option value="rk4">Runge-Kutta 4 (RK4)</option>
          </select>
        </div>
"""
html = html.replace('<div class="field-grid">', '<div class="field-grid">\n' + method_field)

# 3. Explanation and Table
panel_html = """
    <div class="full-width" style="grid-column: 1 / -1; display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
      <div class="panel explanation-panel">
        <h3 class="section-title">Mathematical Insight</h3>
        <div id="math-explanation">
          <p>The <strong>Euler Method</strong> approximates the solution to a differential equation by taking linear steps along the tangent line.</p>
          <div class="math-rule" id="math-rule-display">y(n+1) = y(n) + h * f(x, y)</div>
          <p>Smaller step sizes (<strong>h</strong>) yield a closer approximation to the curve, reducing the error but requiring more iterations.</p>
          <div id="stability-warning" class="warning-text" style="display:none;">⚠️ Method may be unstable or inaccurate due to large step size.</div>
        </div>
      </div>
      
      <div class="panel table-container">
        <table id="data-table">
          <thead>
            <tr>
              <th>n</th>
              <th>x</th>
              <th>y (Approx)</th>
              <th>dy/dx</th>
              <th>Exact y</th>
              <th>Error</th>
            </tr>
          </thead>
          <tbody id="table-body"></tbody>
        </table>
      </div>
    </div>
"""
html = html.replace('    </main>\n\n  </div>', f'    </main>\n{panel_html}\n  </div>')

# 4. Canvas Tooltip container overlay
canvas_stage = '<main class="stage" style="position: relative;">'
html = html.replace('<main class="stage">', canvas_stage)
html = html.replace('<div class="zoom-hint" id="zoomHint">', '<div id="tooltip" class="tooltip" style="opacity:0;"></div>\n      <div class="zoom-hint" id="zoomHint">')

# 5. Fix Javascript Evaluation (Function of x only for Exact Solution)
html = html.replace('const exact = evaluateMath(compiledTrue, cur.x, 0);', 'const exact = evaluateMath(compiledTrue, cur.x, cur.y);') # true function could still use generic variables
html = html.replace('const y = evaluateMath(compiledTrue, x, 0);', 'const y = evaluateMath(compiledTrue, x, 0);') 
# wait, wait. The prompt says "Exact solution is treated as a function of x only". So I'll modify evaluating Math to only pass x inside evaluateMath(compiledTrue, x).
html = html.replace('evaluateMath(compiledTrue, x, 0)', 'evaluateTrue(compiledTrue, x)')
html = html.replace('evaluateMath(compiledTrue, cur.x, 0)', 'evaluateTrue(compiledTrue, cur.x)')
js_addition = """
  function evaluateTrue(compiled, x) {
    try { return compiled.evaluate({ x, e: Math.E, pi: Math.PI }); } 
    catch(e) { return NaN; }
  }
"""
html = html.replace('function evaluateMath(compiled, x, y) {', js_addition + '\n  function evaluateMath(compiled, x, y) {')

# 6. Presets and Logic Additions
js_logic = """
  const methodSelect = document.getElementById('method-select');
  
  function setPreset(type) {
    const presets = {
      linear: { fxy: "x + y", ftrue: "-x - 1 + 2*exp(x)", x0: 0, y0: 1, h: 0.1, n: 20, xend: 2, yrange: 10, exp: "Simple linear ODE. Exact solution diverges due to exp(x)." },
      exponential: { fxy: "0.5*y", ftrue: "exp(0.5*x)", x0: 0, y0: 1, h: 0.2, n: 20, xend: 4, yrange: 8, exp: "Unrestricted growth proportional to population size." },
      logistic: { fxy: "y*(1 - y)", ftrue: "1 / (1 + exp(-x))", x0: 0, y0: 0.1, h: 0.5, n: 20, xend: 10, yrange: 1.5, exp: "Growth restricted by a carrying capacity (y=1). Notice how it flattens." },
      physics: { fxy: "-9.81", ftrue: "100 - 9.81*x", x0: 0, y0: 100, h: 0.5, n: 20, xend: 10, yrange: 120, exp: "Velocity under constant gravity (dv/dt = -g)." },
      decay: { fxy: "-0.5*y", ftrue: "10 * exp(-0.5*x)", x0: 0, y0: 10, h: 0.4, n: 25, xend: 10, yrange: 12, exp: "Radioactive decay or fluid leaving a tank." },
      advanced: { fxy: "cos(x) - y", ftrue: "0.5*(sin(x) + cos(x)) - 0.5*exp(-x)", x0: 0, y0: 0, h: 0.2, n: 50, xend: 10, yrange: 2, exp: "A complex mixing of trigonometric driving forces and exponential decay." }
    };
    const p = presets[type];
    document.getElementById('fxy').value = p.fxy;
    document.getElementById('ftrue').value = p.ftrue;
    document.getElementById('x0').value = p.x0;
    document.getElementById('y0').value = p.y0;
    document.getElementById('h').value = p.h;
    document.getElementById('n').value = p.n;
    document.getElementById('xend').value = p.xend;
    document.getElementById('yrange').value = p.yrange;
    document.getElementById('btnRun').click();
  }

  // Update explanation based on method
  function updateExplanation() {
    const h = parseFloat(document.getElementById('h').value);
    const m = methodSelect.value;
    const rule = document.getElementById('math-rule-display');
    if (m === 'euler') rule.innerText = "y(n+1) = y(n) + h * f(x_n, y_n)";
    else if (m === 'heun') rule.innerText = "y(n+1) = y(n) + (h/2)*(f(x_n, y_n) + f(x_{n+1}, y_{n+1}^*))";
    else if (m === 'rk4') rule.innerText = "y(n+1) = y(n) + (h/6)*(k1 + 2k2 + 2k3 + k4)";
    
    const warn = document.getElementById('stability-warning');
    if (h > 0.5) warn.style.display = "block";
    else warn.style.display = "none";
  }

  // Update getParams to include method
  function getParamsNew() {
    const p = getParamsOld();
    p.method = methodSelect.value;
    return p;
  }
"""
html = html.replace('function getParams() {', js_logic + '\n  function getParamsOld() {')
html = html.replace('getParams()', 'getParamsNew()')

# 7. Modify calculatePoints to support methodologies
points_calc = """
  function calculatePoints(p) {
    const pts = [{ x: p.x0, y: p.y0, slope: evaluateMath(compiledF, p.x0, p.y0) }];
    for (let i = 0; i < p.n; i++) {
        const cur = pts[pts.length - 1];
        let nextX = cur.x + p.h;
        let nextY = 0;
        let slope = evaluateMath(compiledF, cur.x, cur.y);
        
        if (p.method === 'euler') {
            nextY = cur.y + p.h * slope;
        } else if (p.method === 'heun') {
            let eulerY = cur.y + p.h * slope;
            let nextSlope = evaluateMath(compiledF, nextX, eulerY);
            nextY = cur.y + (p.h / 2) * (slope + nextSlope);
        } else if (p.method === 'rk4') {
            let k1 = p.h * slope;
            let k2 = p.h * evaluateMath(compiledF, cur.x + p.h/2, cur.y + k1/2);
            let k3 = p.h * evaluateMath(compiledF, cur.x + p.h/2, cur.y + k2/2);
            let k4 = p.h * evaluateMath(compiledF, nextX, cur.y + k3);
            nextY = cur.y + (k1 + 2*k2 + 2*k3 + k4) / 6;
        }
        
        let actSlope = evaluateMath(compiledF, nextX, nextY);
        pts.push({ x: +nextX.toFixed(8), y: nextY, slope: actSlope });
    }
    updateExplanation();
    return pts;
  }
"""
html = html.replace('  function calculatePoints(p) {\n    const pts = [{ x: p.x0, y: p.y0, slope: evaluateMath(compiledF, p.x0, p.y0) }];\n    for (let i = 0; i < p.n; i++) {\n      const cur = pts[pts.length - 1];\n      const nextX = cur.x + p.h;\n      const nextY = cur.y + p.h * cur.slope;\n      const nextSlope = evaluateMath(compiledF, nextX, nextY);\n      pts.push({ x: +nextX.toFixed(8), y: nextY, slope: nextSlope });\n    }\n    return pts;\n  }', points_calc)

# 8. Render colors based on method and Table population
html = html.replace('Theme.euler', "p.method === 'rk4' ? Theme.rk4 : p.method === 'heun' ? Theme.heun : Theme.euler")
html = html.replace("Theme = {", "Theme = { heun: '#3b82f6', rk4: '#8b5cf6',")

table_logic = """
  // Manage Table
  function updateTable(p, progress) {
    const tbody = document.getElementById('table-body');
    if (!tbody) return;
    
    let html = '';
    const maxIdx = Math.floor(progress);
    
    for (let i = 0; i <= Math.min(points.length - 1, maxIdx + Math.max(5, p.n)); i++) {
      if (i > p.n) break;
      const cur = points[i];
      if (!cur) continue;
      
      let exactHtml = '-';
      let errHtml = '-';
      if (compiledTrue) {
        const exact = evaluateTrue(compiledTrue, cur.x);
        if (!isNaN(exact) && isFinite(exact)) {
           exactHtml = exact.toFixed(5);
           const err = Math.abs(cur.y - exact);
           const errColor = err < 0.05 ? 'err-small' : (err > 0.5 ? 'err-large' : '');
           errHtml = `<span class="${errColor}">${err.toFixed(5)}</span>`;
        }
      }
      
      const highlight = (i === maxIdx) ? 'class="row-highlight"' : '';
      const visible = i <= maxIdx ? '' : 'style="opacity:0.3"';
      
      html += `<tr ${highlight} ${visible}>
        <td>${i}</td>
        <td>${cur.x.toFixed(4)}</td>
        <td>${cur.y.toFixed(5)}</td>
        <td>${cur.slope ? cur.slope.toFixed(4) : '-'}</td>
        <td>${exactHtml}</td>
        <td>${errHtml}</td>
      </tr>`;
    }
    tbody.innerHTML = html;
  }
"""

html = html.replace('  function updateStatusBar(p, progress) {', table_logic + '\n  function updateStatusBar(p, progress) {')
html = html.replace('updateStatusBar(p, progress);', 'updateStatusBar(p, progress);\n    updateTable(p, progress);')

tooltip_js = """
  // Interaction Tooltips
  const tooltip = document.getElementById('tooltip');
  let toolTipLocked = false;
  appCanvas.addEventListener('mousemove', (e) => {
    if(isPanning || toolTipLocked || !points.length) return;
    const rect = appCanvas.getBoundingClientRect();
    const mx = (e.clientX - rect.left) * (appCanvas.width / rect.width);
    const my = (e.clientY - rect.top) * (appCanvas.height / rect.height);
    
    const p = getParamsNew();
    let closest = null;
    let minDist = 20; // 20px hover radius
    
    for(let i=0; i<=Math.floor(currentAnimProgress); i++) {
        const [cx, cy] = mapToCanvas(points[i].x, points[i].y, p);
        const dist = Math.sqrt((cx-mx)**2 + (cy-my)**2);
        if(dist < minDist) {
            minDist = dist;
            closest = points[i];
        }
    }
    
    if(closest) {
        let exactHtml = '';
        let errHtml = '';
        if(compiledTrue) {
            const exact = evaluateTrue(compiledTrue, closest.x);
            const err = Math.abs(closest.y - exact);
            exactHtml = `<br>Exact: ${exact.toFixed(4)}`;
            errHtml = `<br>Error: ${err.toFixed(4)}`;
        }
        tooltip.innerHTML = `X: ${closest.x.toFixed(4)}<br>Y: ${closest.y.toFixed(4)}<br>dy/dx: ${closest.slope.toFixed(4)}${exactHtml}${errHtml}`;
        tooltip.style.left = (e.clientX - rect.left + 15) + 'px';
        tooltip.style.top = (e.clientY - rect.top + 15) + 'px';
        tooltip.style.opacity = 1;
    } else {
        tooltip.style.opacity = 0;
    }
  });
  
  appCanvas.addEventListener('click', () => {
    if(tooltip.style.opacity == 1) toolTipLocked = !toolTipLocked;
  });
"""

html = html.replace('appCanvas.addEventListener(\'mousedown\', (e) => { isPanning = true; panStart = { x: e.clientX, y: e.clientY }; });', tooltip_js + "\n  appCanvas.addEventListener('mousedown', (e) => { isPanning = true; panStart = { x: e.clientX, y: e.clientY }; });")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

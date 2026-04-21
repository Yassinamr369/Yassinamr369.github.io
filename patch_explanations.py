with open('index copy.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_css = ".method-btn.active-rk4    { border-color: #a78bfa; color: #a78bfa; background: rgba(167,139,250,0.08); }"
new_css = old_css + """

  .info-icon { font-style: normal; opacity: 0.6; margin-left: 3px; font-size: 9px; vertical-align: top; }
  .method-btn:hover .info-icon { opacity: 1; }

  .method-details {
    margin-top: 12px;
    font-size: 11px;
    line-height: 1.4;
    color: var(--text-muted);
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px;
    transition: all 0.3s ease;
  }
  .method-details summary {
    cursor: pointer;
    font-family: var(--font-mono);
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-main);
    outline: none;
    font-weight: 700;
  }
  .method-details summary::-webkit-details-marker {
    display: none;
  }
  .method-details summary::before {
    content: '▶ ';
    font-size: 8px;
    display: inline-block;
    transition: transform 0.2s;
    margin-right: 4px;
    color: var(--accent-blue);
  }
  .method-details[open] summary::before {
    transform: rotate(90deg);
  }
  .details-content {
    margin-top: 12px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .details-content p {
    margin: 0;
  }
  .details-content strong {
    color: var(--text-main);
    display: block;
    margin-bottom: 3px;
    font-family: var(--font-mono);
  }
  .comparison-note {
    margin-top: 6px;
    border-top: 1px dashed var(--border);
    padding-top: 10px;
    color: var(--text-main);
  }
  .comparison-note span { display: block; margin-bottom: 4px; }
  .comp-euler { color: #ffffff; }
  .comp-heun { color: #3b82f6; }
  .comp-rk4 { color: #a78bfa; }
"""
content = content.replace(old_css, new_css)

old_html = """      <!-- Method Selector -->
      <div>
        <h3 class="section-title">Method</h3>
        <div class="method-selector">
          <button class="method-btn active-euler" data-method="euler" id="mbEuler">Euler</button>
          <button class="method-btn" data-method="heun"  id="mbHeun">Heun's</button>
          <button class="method-btn" data-method="rk4"   id="mbRK4">RK4</button>
        </div>
      </div>"""

new_html = """      <!-- Method Selector -->
      <div>
        <h3 class="section-title">Method</h3>
        <div class="method-selector">
          <button class="method-btn active-euler" data-method="euler" id="mbEuler" title="Euler Method (Basic)&#10;Follows slope once per step">Euler <span class="info-icon">ℹ️</span></button>
          <button class="method-btn" data-method="heun" id="mbHeun" title="Heun Method (Improved Euler)&#10;Average of two slopes">Heun's <span class="info-icon">ℹ️</span></button>
          <button class="method-btn" data-method="rk4" id="mbRK4" title="Runge-Kutta 4 (RK4)&#10;Combines 4 slopes for high accuracy">RK4 <span class="info-icon">ℹ️</span></button>
        </div>
        
        <details class="method-details">
          <summary>Learn More about Methods</summary>
          <div class="details-content">
            <p><strong>Euler Method (Basic)</strong>This method moves step by step using the slope at the current point. It is simple and fast, but not very accurate because it only looks at one direction.</p>
            <p><strong>Heun Method (Improved Euler)</strong>This method improves Euler by checking the slope at the start and the end of the step, then taking the average. This makes it more accurate than Euler.</p>
            <p><strong>Runge-Kutta 4 (RK4)</strong>This method calculates the slope four times in each step and combines them. It is much more accurate and widely used in engineering and physics.</p>
            
            <div class="comparison-note">
              <span class="comp-euler"><strong>Euler:</strong> simplest but least accurate</span>
              <span class="comp-heun"><strong>Heun:</strong> better accuracy</span>
              <span class="comp-rk4"><strong>RK4:</strong> most accurate and recommended</span>
            </div>
          </div>
        </details>
      </div>"""
content = content.replace(old_html, new_html)

with open('index copy.html', 'w', encoding='utf-8') as f:
    f.write(content)

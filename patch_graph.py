with open('index copy.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Limit the table output to first 5 and last 5 if points.length > 15
old_build_table = """    let html = '';
    for (let i = 0; i < points.length; i++) {
      const pt   = points[i];"""
new_build_table = """    let html = '';
    const maxRows = 15;
    for (let i = 0; i < points.length; i++) {
      if (points.length > maxRows && i > 5 && i < points.length - 5) {
        if (i === 6) {
          html += `<tr class="skipped-row"><td colspan="10" style="text-align:center; color: var(--text-muted); opacity: 0.5;">... showing only first and last few points to avoid clutter ...</td></tr>`;
        }
        continue;
      }
      const pt   = points[i];"""
text = text.replace(old_build_table, new_build_table)

# For graph extending, let's just make the grid lines span the visible canvas regardless of xend/yrange parameters, by using the zoomed viewport. 
old_grid = """  function drawGridAndAxes(p) {
    ctx.clearRect(0, 0, appCanvas.width, appCanvas.height);
    
    ctx.strokeStyle = Theme.grid;
    ctx.lineWidth = 1;
    ctx.font = `10px "JetBrains Mono"`;
    ctx.fillStyle = Theme.text;
    
    const xSteps = 10;
    const ySteps = 10;
    
    ctx.textAlign = 'center';
    for (let i = 0; i <= xSteps; i++) {
      const x = p.x0 + i*(p.xend - p.x0)/xSteps;
      const [cx] = mapToCanvas(x, 0, p);
      ctx.beginPath(); ctx.moveTo(cx, Margins.top); ctx.lineTo(cx, appCanvas.height - Margins.bottom); ctx.stroke();
      ctx.fillText(x.toFixed(1), cx, appCanvas.height - Margins.bottom + 20);
    }
    
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    for (let i = 0; i <= ySteps; i++) {
      const y = -p.yrange + i * p.yrange * 2 / ySteps;
      const [, cy] = mapToCanvas(0, y, p);
      ctx.beginPath(); ctx.moveTo(Margins.left, cy); ctx.lineTo(appCanvas.width - Margins.right, cy); ctx.stroke();
      if(Math.abs(y) > 0.001) ctx.fillText(y.toFixed(1), Margins.left - 10, cy);
    }"""
new_grid = """  function drawGridAndAxes(p) {
    ctx.clearRect(0, 0, appCanvas.width, appCanvas.height);
    
    ctx.strokeStyle = Theme.grid;
    ctx.lineWidth = 1;
    ctx.font = `10px "JetBrains Mono"`;
    ctx.fillStyle = Theme.text;
    
    // Dynamically calculate grid limits based on current zoom so it extends indefinitely
    // calculate bounds in Math coordinates based on canvas pixel bounds
    function unmapX(px) {
       return p.x0 + ((px - zoomState.offsetX) / zoomState.scale - Margins.left) / (appCanvas.width - Margins.left - Margins.right) * (p.xend - p.x0);
    }
    function unmapY(py) {
       return p.yrange - ((py - zoomState.offsetY) / zoomState.scale - Margins.top) / (appCanvas.height - Margins.top - Margins.bottom) * (p.yrange * 2);
    }

    const minX = unmapX(Margins.left), maxX = unmapX(appCanvas.width - Margins.right);
    const minY = unmapY(appCanvas.height - Margins.bottom), maxY = unmapY(Margins.top);

    const xRange = maxX - minX;
    const yRange = maxY - minY;

    const xStep = Math.pow(10, Math.floor(Math.log10(xRange))) / 2;
    const yStep = Math.pow(10, Math.floor(Math.log10(yRange))) / 2;

    ctx.textAlign = 'center';
    let curX = Math.floor(minX / xStep) * xStep;
    while(curX <= maxX) {
      if(curX >= p.x0 - 500 && curX <= p.xend + 500) { // arbitrary wide boundary
         const [cx] = mapToCanvas(curX, 0, p);
         ctx.beginPath(); ctx.moveTo(cx, Margins.top); ctx.lineTo(cx, appCanvas.height - Margins.bottom); ctx.stroke();
         ctx.fillText(curX.toFixed(1), cx, appCanvas.height - Margins.bottom + 20);
      }
      curX += xStep;
    }
    
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    let curY = Math.floor(minY / yStep) * yStep;
    while(curY <= maxY) {
      const [, cy] = mapToCanvas(0, curY, p);
      ctx.beginPath(); ctx.moveTo(Margins.left, cy); ctx.lineTo(appCanvas.width - Margins.right, cy); ctx.stroke();
      if(Math.abs(curY) > 0.001) ctx.fillText(curY.toFixed(1), Margins.left - 10, cy);
      curY += yStep;
    }"""
text = text.replace(old_grid, new_grid)


# Increase n max to larger number to allow users to generate more points if they want
text = text.replace('max="100"', 'max="1000"')

with open('index copy.html', 'w', encoding='utf-8') as f:
    f.write(text)

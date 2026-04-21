import re

def add_nav_banner(file_name, version_text, other_text, other_link):
    with open(file_name, 'r', encoding='utf-8') as f:
        html = f.read()

    css_banner = """
  /* ─── VERSION BANNER ───────────────────── */
  .version-banner {
    position: fixed;
    top: 0; left: 0; right: 0;
    background: var(--accent-blue);
    color: #fff;
    text-align: center;
    padding: 10px;
    font-family: var(--font-mono);
    font-size: 13px;
    font-weight: 700;
    z-index: 9999;
    box-shadow: 0 4px 10px rgba(0,0,0,0.5);
  }
  .version-banner a {
    color: #fff;
    text-decoration: underline;
    margin-left: 15px;
  }
  .version-banner a:hover {
    color: #e2e8f0;
  }
"""
    if "/* ─── VERSION BANNER ───────────────────── */" not in html:
        html = html.replace('/* ─── SCROLLBAR ───────────────────────── */', css_banner + '  /* ─── SCROLLBAR ───────────────────────── */')

    banner_html = f"""
<div class="version-banner">
  {version_text} | <a href="{other_link}">View {other_text}</a>
</div>
"""
    
    if "class=\"version-banner\"" not in html:
        html = html.replace('<body>', f'<body>\n{banner_html}')

    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(html)

add_nav_banner('index.html', 'Version 1 (Single Method View)', 'Version 2 (Multi-Method View)', 'index%20copy.html')
add_nav_banner('index copy.html', 'Version 2 (Multi-Method View)', 'Version 1 (Single Method View)', 'index.html')


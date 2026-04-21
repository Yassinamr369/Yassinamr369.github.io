with open('index copy.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_scroll = """    const target = tbody.querySelector(`tr[data-row="${idx}"]`);
    if (target) {
      target.classList.add('active-row');
      // smooth scroll into view within the wrapper
      target.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }"""
new_scroll = """    const target = tbody.querySelector(`tr[data-row="${idx}"]`);
    if (target) {
      target.classList.add('active-row');
      // scroll only the wrapper box, not the entire browser window
      const wrapper = target.closest('.table-wrapper');
      if (wrapper) {
        wrapper.scrollTo({
          top: target.offsetTop - wrapper.clientHeight/2 + target.clientHeight/2,
          behavior: 'smooth'
        });
      }
    }"""

content = content.replace(old_scroll, new_scroll)

with open('index copy.html', 'w', encoding='utf-8') as f:
    f.write(content)

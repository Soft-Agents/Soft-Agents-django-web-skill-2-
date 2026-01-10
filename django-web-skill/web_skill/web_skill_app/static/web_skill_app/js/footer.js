// Archivo: src/scripts/footer-hover.js

document.addEventListener('DOMContentLoaded', () => {
    const footer = document.getElementById('footer-container');
    const glow = document.getElementById('footer-glow');
  
    if (!footer || !glow) return;
  
    footer.addEventListener('mousemove', (e) => {
      const rect = footer.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
  
      glow.style.transform = `translate(${x}px, ${y}px)`;
      glow.style.opacity = '1';
    });
  
    footer.addEventListener('mouseleave', () => {
      glow.style.opacity = '0';
    });
  });

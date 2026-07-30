(() => {
  const root = document.documentElement;
  const spanish = (root.lang || 'es').toLowerCase().startsWith('es');
  const text = {
    skip: spanish ? 'Saltar al contenido principal' : 'Skip to main content',
    nav: spanish ? 'Navegación principal' : 'Primary navigation',
    unavailable: spanish ? 'Versión en inglés próximamente' : 'English version coming soon',
    newTab: spanish ? 'Abre en una pestaña nueva' : 'Opens in a new tab'
  };

  const main = document.querySelector('main');
  if (main) {
    if (!main.id) main.id = 'main-content';
    const skip = document.createElement('a');
    skip.className = 'skip-link';
    skip.href = `#${main.id}`;
    skip.textContent = text.skip;
    document.body.prepend(skip);
  }

  document.querySelectorAll('nav').forEach((nav, index) => {
    if (!nav.hasAttribute('aria-label')) nav.setAttribute('aria-label', index ? `${text.nav} ${index + 1}` : text.nav);
  });

  const primaryNav = document.querySelector('.nav-menu');
  const navToggle = document.querySelector('.nav-toggle');
  if (primaryNav && navToggle) {
    if (!primaryNav.id) primaryNav.id = 'primary-navigation';
    navToggle.setAttribute('aria-controls', primaryNav.id);
    document.addEventListener('keydown', event => {
      if (event.key !== 'Escape' || navToggle.getAttribute('aria-expanded') !== 'true') return;
      primaryNav.classList.remove('active');
      navToggle.classList.remove('active');
      navToggle.setAttribute('aria-expanded', 'false');
      navToggle.focus();
    });
  }

  const currentFile = decodeURIComponent(location.pathname.split('/').pop() || 'index.html').toLowerCase();
  document.querySelectorAll('nav a[href]').forEach(link => {
    const raw = link.getAttribute('href');
    if (!raw || raw === '#') {
      link.setAttribute('aria-disabled', 'true');
      link.setAttribute('tabindex', '-1');
      link.setAttribute('title', text.unavailable);
      return;
    }
    const destination = raw.split('#')[0].split('/').pop().toLowerCase();
    if (destination && destination === currentFile) link.setAttribute('aria-current', 'page');
  });

  document.querySelectorAll('a[target="_blank"]').forEach(link => {
    if (!link.hasAttribute('aria-description')) link.setAttribute('aria-description', text.newTab);
    const rel = new Set((link.getAttribute('rel') || '').split(/\s+/).filter(Boolean));
    rel.add('noopener');
    rel.add('noreferrer');
    link.setAttribute('rel', [...rel].join(' '));
  });

  document.querySelectorAll('input, textarea, select').forEach(control => {
    const labelled = control.hasAttribute('aria-label') || control.hasAttribute('aria-labelledby') || (control.id && document.querySelector(`label[for="${CSS.escape(control.id)}"]`)) || control.closest('label');
    if (!labelled) control.setAttribute('aria-label', control.placeholder || control.name || control.id || (spanish ? 'Campo de formulario' : 'Form field'));
  });

  document.querySelectorAll('[data-full-src], [data-video-id]').forEach(card => {
    if (!card.hasAttribute('tabindex')) card.tabIndex = 0;
    if (!card.hasAttribute('role')) card.setAttribute('role', 'button');
    card.addEventListener('keydown', event => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        card.click();
      }
    });
  });

  document.querySelectorAll('[tabindex="0"]').forEach(element => {
    if (element.matches('a, button, input, textarea, select, [data-full-src], [data-video-id], #modeling-lab-stage')) return;
    element.addEventListener('keydown', event => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        element.click();
      }
    });
  });

  const chatOutput = document.querySelector('#chat-output, #chat-messages, #chat-historial, .chat-messages');
  if (chatOutput) {
    chatOutput.setAttribute('role', 'log');
    chatOutput.setAttribute('aria-live', 'polite');
    chatOutput.setAttribute('aria-relevant', 'additions text');
  }

  if (matchMedia('(prefers-reduced-motion: reduce)').matches) {
    document.querySelectorAll('video[autoplay]').forEach(video => {
      video.removeAttribute('autoplay');
      video.pause();
    });
  }
})();

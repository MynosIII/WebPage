(() => {
  if (!window.AOS) {
    document.querySelectorAll('[data-aos]').forEach((element) => {
      element.removeAttribute('data-aos');
      element.removeAttribute('data-aos-delay');
      element.removeAttribute('data-aos-duration');
    });
  }

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
    const navbar = navToggle.closest('.navbar');
    const navContainer = navbar?.querySelector('.container');
    const languageSwitch = document.querySelector('.language-switch');
    const openLabel = spanish ? 'Abrir menú' : 'Open menu';
    const closeLabel = spanish ? 'Cerrar menú' : 'Close menu';
    const mobileNavigation = matchMedia('(max-width: 1050px)');
    const backdrop = document.createElement('button');
    let menuOpen = false;

    if (!primaryNav.id) primaryNav.id = 'primary-navigation';
    navToggle.setAttribute('aria-controls', primaryNav.id);
    navToggle.type = 'button';

    if (languageSwitch && navContainer) {
      languageSwitch.classList.add('language-switch--nav');
      navContainer.insertBefore(languageSwitch, navToggle);
    }

    backdrop.type = 'button';
    backdrop.className = 'legacy-nav-backdrop';
    backdrop.setAttribute('aria-label', closeLabel);
    backdrop.tabIndex = -1;
    navbar?.after(backdrop);

    const background = () => [document.querySelector('[data-portfolio-rail]'), main, document.querySelector('footer')].filter(Boolean);
    const setMenuState = (open, restoreFocus = false) => {
      menuOpen = Boolean(open && mobileNavigation.matches);
      navbar?.classList.toggle('nav-open', menuOpen);
      primaryNav.classList.toggle('active', menuOpen);
      navToggle.classList.toggle('active', menuOpen);
      document.body.classList.toggle('menu-open', menuOpen);
      navToggle.setAttribute('aria-expanded', String(menuOpen));
      navToggle.setAttribute('aria-label', menuOpen ? closeLabel : openLabel);
      primaryNav.inert = mobileNavigation.matches && !menuOpen;
      backdrop.tabIndex = menuOpen ? 0 : -1;
      background().forEach(element => { element.inert = menuOpen; });

      if (menuOpen) primaryNav.querySelector('a[href]')?.focus();
      else if (restoreFocus) navToggle.focus();
    };

    navToggle.addEventListener('click', event => {
      event.preventDefault();
      event.stopImmediatePropagation();
      setMenuState(!menuOpen);
    }, true);
    backdrop.addEventListener('click', () => setMenuState(false, true));
    primaryNav.addEventListener('click', event => {
      if (event.target.closest('a[href]') && mobileNavigation.matches) setMenuState(false);
    });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && menuOpen) {
        event.preventDefault();
        setMenuState(false, true);
        return;
      }
      if (event.key !== 'Tab' || !menuOpen) return;

      const focusable = [navToggle, ...primaryNav.querySelectorAll('a[href]:not([tabindex="-1"])')]
        .filter(element => element.getClientRects().length > 0);
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last?.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first?.focus();
      }
    });
    mobileNavigation.addEventListener('change', () => setMenuState(false));
    setMenuState(false);
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

(() => {
  if (document.querySelector('script[data-site-search]')) return;
  const current = document.currentScript;
  if (!current?.src) return;
  const searchScript = document.createElement('script');
  searchScript.src = new URL('site-search.js', current.src).href;
  searchScript.dataset.siteSearch = '';
  document.head.appendChild(searchScript);
})();

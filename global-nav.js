(() => {
  const nav = document.querySelector('[data-global-nav]');
  if (!nav) return;
  const button = nav.querySelector('[data-global-nav-toggle]');
  const menu = nav.querySelector('[data-global-nav-menu]');
  if (!button || !menu) return;

  const spanish = (document.documentElement.lang || 'es').toLowerCase().startsWith('es');
  const openLabel = spanish ? 'Abrir menú' : 'Open menu';
  const closeLabel = spanish ? 'Cerrar menú' : 'Close menu';
  const mobile = matchMedia('(max-width: 1040px)');
  const backdrop = document.createElement('button');
  let menuOpen = false;

  menu.querySelectorAll('a[href*="SEO"]').forEach((link) => {
    if (/^chat\s*mat/i.test(link.textContent.trim())) link.closest('li')?.remove();
  });

  backdrop.type = 'button';
  backdrop.className = 'global-nav__backdrop';
  backdrop.setAttribute('aria-label', closeLabel);
  backdrop.tabIndex = -1;
  nav.after(backdrop);

  const background = () => [document.querySelector('[data-portfolio-rail]'), document.querySelector('main'), document.querySelector('footer')].filter(Boolean);
  const setMenu = (open, { restoreFocus = false } = {}) => {
    menuOpen = Boolean(open && mobile.matches);
    nav.classList.toggle('is-open', menuOpen);
    document.body.classList.toggle('menu-open', menuOpen);
    button.setAttribute('aria-expanded', String(menuOpen));
    button.setAttribute('aria-label', menuOpen ? closeLabel : openLabel);
    menu.inert = mobile.matches && !menuOpen;
    backdrop.tabIndex = menuOpen ? 0 : -1;
    background().forEach((element) => { element.inert = menuOpen; });

    if (menuOpen) menu.querySelector('a[href]')?.focus();
    else if (restoreFocus) button.focus();
  };

  button.addEventListener('click', () => setMenu(!menuOpen));
  backdrop.addEventListener('click', () => setMenu(false, { restoreFocus: true }));
  menu.addEventListener('click', (event) => {
    if (event.target.closest('a[href]')) setMenu(false);
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && menuOpen) {
      event.preventDefault();
      setMenu(false, { restoreFocus: true });
      return;
    }
    if (event.key !== 'Tab' || !menuOpen) return;
    const focusable = [button, ...menu.querySelectorAll('a[href]:not([tabindex="-1"])')].filter((element) => element.getClientRects().length > 0);
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
  mobile.addEventListener('change', () => setMenu(false));
  setMenu(false);
})();

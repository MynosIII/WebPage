(() => {
  const header = document.querySelector('[data-site-header]');
  const menuButton = document.querySelector('[data-menu-button]');
  const navigation = document.querySelector('[data-site-nav]');
  const backdrop = document.querySelector('[data-menu-backdrop]');
  const main = document.querySelector('main');
  const footer = document.querySelector('footer');
  const mobileQuery = window.matchMedia('(max-width: 1050px)');

  if (!header || !menuButton || !navigation || !backdrop) return;

  let menuOpen = false;

  const focusableElements = () => [
    menuButton,
    ...navigation.querySelectorAll('a[href]'),
  ].filter((element) => !element.hidden && element.getClientRects().length > 0);

  const setPageInert = (inert) => {
    [main, footer].forEach((element) => {
      if (!element) return;
      element.inert = inert;
      if (inert) element.setAttribute('aria-hidden', 'true');
      else element.removeAttribute('aria-hidden');
    });
  };

  const setMenu = (open, { restoreFocus = false } = {}) => {
    menuOpen = Boolean(open && mobileQuery.matches);
    header.classList.toggle('nav-open', menuOpen);
    document.body.classList.toggle('menu-open', menuOpen);
    menuButton.setAttribute('aria-expanded', String(menuOpen));
    menuButton.setAttribute(
      'aria-label',
      menuOpen ? menuButton.dataset.closeLabel : menuButton.dataset.openLabel,
    );
    navigation.inert = mobileQuery.matches && !menuOpen;
    backdrop.tabIndex = menuOpen ? 0 : -1;
    setPageInert(menuOpen);

    if (menuOpen) {
      navigation.querySelector('a[href]')?.focus();
    } else if (restoreFocus) {
      menuButton.focus();
    }
  };

  const handleViewportChange = () => setMenu(false);

  menuButton.addEventListener('click', () => setMenu(!menuOpen));
  backdrop.addEventListener('click', () => setMenu(false, { restoreFocus: true }));
  navigation.addEventListener('click', (event) => {
    if (event.target.closest('a[href]') && mobileQuery.matches) setMenu(false);
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && menuOpen) {
      event.preventDefault();
      setMenu(false, { restoreFocus: true });
      return;
    }

    if (event.key !== 'Tab' || !menuOpen) return;
    const focusable = focusableElements();
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (!first || !last) return;

    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  });

  mobileQuery.addEventListener('change', handleViewportChange);
  window.addEventListener('scroll', () => {
    header.classList.toggle('is-scrolled', window.scrollY > 12);
  }, { passive: true });

  setMenu(false);
})();

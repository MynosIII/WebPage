(() => {
  const nav = document.querySelector('[data-global-nav]');
  if (!nav) return;
  const button = nav.querySelector('[data-global-nav-toggle]');
  const menu = nav.querySelector('[data-global-nav-menu]');
  if (!button || !menu) return;

  const close = () => {
    nav.classList.remove('is-open');
    button.setAttribute('aria-expanded', 'false');
  };
  button.addEventListener('click', () => {
    const opening = !nav.classList.contains('is-open');
    nav.classList.toggle('is-open', opening);
    button.setAttribute('aria-expanded', String(opening));
  });
  menu.addEventListener('click', event => {
    if (event.target.closest('a')) close();
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') close();
  });
  document.addEventListener('click', event => {
    if (!nav.contains(event.target)) close();
  });
})();

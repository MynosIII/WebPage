(() => {
  const email = 'matiasignaciogaglio@gmail.com';
  const spanish = (document.documentElement.lang || 'es').toLowerCase().startsWith('es');
  const labels = spanish
    ? { mail: `Enviar email a ${email}`, copy: 'Copiar', copied: 'Copiado', copyAria: `Copiar dirección ${email}` }
    : { mail: `Send email to ${email}`, copy: 'Copy', copied: 'Copied', copyAria: `Copy address ${email}` };
  const scriptBase = document.currentScript?.src || document.baseURI;

  if (!document.querySelector('link[data-contact-actions]')) {
    const styles = document.createElement('link');
    styles.rel = 'stylesheet';
    styles.href = new URL('contact-actions.css?v=20260806a', scriptBase).href;
    styles.dataset.contactActions = '';
    document.head.append(styles);
  }

  const mailIcon = '<svg class="contact-action__icon" aria-hidden="true" viewBox="0 0 24 24" fill="none"><path d="M3.5 6.5h17v11h-17zM4.5 7.5l7.5 6 7.5-6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  const copyIcon = '<svg class="contact-action__icon" aria-hidden="true" viewBox="0 0 24 24" fill="none"><rect x="8" y="8" width="11" height="11" rx="2" stroke="currentColor" stroke-width="1.8"/><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>';

  const copyEmail = async () => {
    try {
      await navigator.clipboard.writeText(email);
    } catch {
      const input = document.createElement('textarea');
      input.value = email;
      input.setAttribute('readonly', '');
      input.style.position = 'fixed';
      input.style.opacity = '0';
      document.body.append(input);
      input.select();
      document.execCommand('copy');
      input.remove();
    }
  };

  const enhanceContact = (link) => {
    if (!(link instanceof HTMLAnchorElement) || link.dataset.contactEnhanced !== undefined) return;
    if (!link.matches('a[href^="mailto:"].button, a[href^="mailto:"].cta-button, a[href^="mailto:"].case-contact-cta')) return;

    link.dataset.contactEnhanced = '';
    const rect = link.getBoundingClientRect();
    const style = getComputedStyle(link);
    const wrapper = document.createElement('span');
    const label = document.createElement('span');
    const detail = document.createElement('span');
    const copy = document.createElement('button');
    const status = document.createElement('span');
    const original = document.createDocumentFragment();

    while (link.firstChild) original.append(link.firstChild);
    label.className = 'contact-action__label';
    label.append(original);
    detail.className = 'contact-action__mail-detail';
    detail.innerHTML = `${mailIcon}<span class="contact-action__email">${email}</span>`;
    copy.type = 'button';
    copy.className = 'contact-action__copy';
    copy.setAttribute('aria-label', labels.copyAria);
    copy.innerHTML = `${copyIcon}<span>${labels.copy}</span>`;
    status.className = 'contact-action__status';
    status.setAttribute('role', 'status');
    status.setAttribute('aria-live', 'polite');

    wrapper.className = 'contact-action';
    wrapper.style.setProperty('--contact-action-collapsed-width', `${Math.max(48, Math.ceil(rect.width))}px`);
    wrapper.style.setProperty('--contact-action-open-width', `${Math.max(420, Math.ceil(rect.width))}px`);
    wrapper.style.setProperty('--contact-action-height', `${Math.max(44, Math.ceil(rect.height))}px`);
    wrapper.style.setProperty('--contact-action-background', style.background);
    wrapper.style.setProperty('--contact-action-border', `${style.borderTopWidth} ${style.borderTopStyle} ${style.borderTopColor}`);
    wrapper.style.setProperty('--contact-action-color', style.color);
    wrapper.style.font = style.font;
    wrapper.style.letterSpacing = style.letterSpacing;
    wrapper.style.textTransform = style.textTransform;

    link.before(wrapper);
    wrapper.append(link, copy, status);
    link.classList.add('contact-action__mail');
    link.setAttribute('aria-label', labels.mail);
    link.setAttribute('aria-expanded', 'false');
    link.append(label, detail);

    const setOpen = (open) => {
      wrapper.classList.toggle('is-open', open);
      link.setAttribute('aria-expanded', String(open));
    };
    wrapper.addEventListener('pointerenter', () => setOpen(true));
    wrapper.addEventListener('pointerleave', () => {
      if (!wrapper.contains(document.activeElement)) setOpen(false);
    });
    wrapper.addEventListener('focusin', () => setOpen(true));
    wrapper.addEventListener('focusout', () => requestAnimationFrame(() => {
      if (!wrapper.contains(document.activeElement) && !wrapper.matches(':hover')) setOpen(false);
    }));
    link.addEventListener('click', (event) => {
      if ((matchMedia('(hover: none)').matches || innerWidth <= 520) && !wrapper.classList.contains('is-open')) {
        event.preventDefault();
        setOpen(true);
      }
    });
    copy.addEventListener('click', async () => {
      await copyEmail();
      copy.classList.add('is-copied');
      copy.querySelector('span').textContent = labels.copied;
      status.textContent = `${labels.copied}: ${email}`;
      window.setTimeout(() => {
        copy.classList.remove('is-copied');
        copy.querySelector('span').textContent = labels.copy;
      }, 2200);
    });
    wrapper.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        setOpen(false);
        link.focus();
      }
    });
  };

  const enhanceContacts = (root = document) => {
    if (root instanceof HTMLAnchorElement) enhanceContact(root);
    root.querySelectorAll?.('a[href^="mailto:"]').forEach(enhanceContact);
  };

  enhanceContacts();
  document.addEventListener('pointerdown', (event) => {
    if (event.target.closest('.contact-action')) return;
    document.querySelectorAll('.contact-action.is-open').forEach((wrapper) => {
      wrapper.classList.remove('is-open');
      wrapper.querySelector('.contact-action__mail')?.setAttribute('aria-expanded', 'false');
    });
  });
  new MutationObserver((records) => records.forEach(({ addedNodes }) => addedNodes.forEach((node) => {
    if (node instanceof Element) enhanceContacts(node);
  }))).observe(document.body, { childList: true, subtree: true });
})();

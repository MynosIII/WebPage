(() => {
  const progress = document.querySelector('[data-cv-progress]');
  const navLinks = [...document.querySelectorAll('[data-cv-nav]')];
  const sections = [...document.querySelectorAll('[data-cv-section]')];
  const expandButton = document.querySelector('[data-cv-expand]');
  const cases = [...document.querySelectorAll('.cv-case')];

  const updateProgress = () => {
    if (!progress) return;
    const available = document.documentElement.scrollHeight - innerHeight;
    const ratio = available > 0 ? Math.min(1, Math.max(0, scrollY / available)) : 0;
    progress.style.transform = `scaleX(${ratio})`;
  };

  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      const visible = entries.filter((entry) => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (!visible) return;
      navLinks.forEach((link) => link.setAttribute('aria-current', String(link.hash === `#${visible.target.id}`)));
    }, { rootMargin: '-24% 0px -58%', threshold: [0, .15, .4] });
    sections.forEach((section) => observer.observe(section));
  }

  expandButton?.addEventListener('click', () => {
    const shouldOpen = cases.some((item) => !item.open);
    cases.forEach((item) => { item.open = shouldOpen; });
    expandButton.textContent = shouldOpen ? expandButton.dataset.collapseLabel : expandButton.dataset.expandLabel;
    expandButton.setAttribute('aria-expanded', String(shouldOpen));
  });
  document.querySelector('[data-cv-print]')?.addEventListener('click', () => window.print());
  addEventListener('scroll', updateProgress, { passive: true });
  addEventListener('resize', updateProgress);
  updateProgress();
})();

(() => {
  const key = document.body.dataset.videoCase;
  const item = window.ecommerceVideoCases?.[key];
  if (!item) return;
  document.title = `Conversion Video ${key} — ${item.title} | Matias Gaglio`;
  document.querySelector('[data-case-eyebrow]').textContent = `Conversion video ${key} · ${item.eyebrow} · ${item.duration}`;
  document.querySelector('[data-case-title]').textContent = item.title;
  document.querySelector('[data-case-lead]').textContent = item.lead;
  document.querySelector('.animation-breakdown h2').textContent = item.breakdownTitle;
  document.querySelector('.animation-skill-list').innerHTML = item.skills.map((skill) => `<span>${skill}</span>`).join('');
  document.querySelector('.animation-section-number').textContent = 'After Effects breakdown';
  const video = document.querySelector('[data-case-video]');
  video.setAttribute('aria-label', item.media);
  video.dataset.mediaDescription = item.media;
  video.querySelector('source').src = `creatives/ecommerce-video/${item.source}`;
  video.load();
  video.play().catch(() => {});
  document.querySelector('[data-case-notes]').innerHTML = item.notes.map((note, index) => `<article><b>${String(index + 1).padStart(2, '0')}</b><h3>${note[0]}</h3><p>${note[1]}</p></article>`).join('');
})();

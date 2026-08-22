(() => {
  const storage = window.localStorage;
  const slug = document.body.dataset.storySlug;
  const language = document.body.dataset.language || 'ko';
  if (!slug) return;
  const prefix = `webnovel:${slug}`;

  function migrateLegacy(name, legacy) {
    const key = `${prefix}:${name}`;
    if (slug === 'murim-abolitionist' && storage.getItem(key) === null) {
      const value = storage.getItem(legacy);
      if (value !== null) storage.setItem(key, value);
    }
    return key;
  }

  const readKey = migrateLegacy('read-chapters', 'murim-read-chapters');
  const lastKey = migrateLegacy('last-chapter', 'murim-last-chapter');
  let read = new Set();
  try {
    read = new Set(JSON.parse(storage.getItem(readKey) || '[]'));
  } catch (_) {
    storage.removeItem(readKey);
  }
  document.querySelectorAll('[data-chapter-link]').forEach((link) => {
    if (read.has(Number(link.dataset.chapterLink))) link.dataset.read = 'true';
  });
  const resume = document.querySelector('[data-resume]');
  const last = Number(storage.getItem(lastKey) || 0);
  const target = document.querySelector(`[data-chapter-link="${last}"]`);
  if (resume && last > 0 && target) {
    resume.href = target.getAttribute('href');
    resume.innerHTML = language === 'en' ? `Continue with chapter ${last} →` : `${last}화부터 이어 읽기 →`;
  }
})();

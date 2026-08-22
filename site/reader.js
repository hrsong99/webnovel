(() => {
  const root = document.documentElement;
  const storage = window.localStorage;
  const slug = document.body.dataset.storySlug;
  if (!slug) return;
  const prefix = `webnovel:${slug}`;
  const language = document.body.dataset.language || 'ko';
  const currentChapter = Number(document.body.dataset.chapter || 0);

  function migratedKey(name, legacy) {
    const key = `${prefix}:${name}`;
    if (slug === 'murim-abolitionist' && storage.getItem(key) === null) {
      const value = storage.getItem(legacy);
      if (value !== null) storage.setItem(key, value);
    }
    return key;
  }
  const settingsKey = migratedKey('reader-settings', 'murim-reader-settings');
  const readKey = migratedKey('read-chapters', 'murim-read-chapters');
  const lastKey = migratedKey('last-chapter', 'murim-last-chapter');
  function loadSettings() {
    try { return JSON.parse(storage.getItem(settingsKey)) || {}; } catch (_) { return {}; }
  }
  function saveSettings(value) { storage.setItem(settingsKey, JSON.stringify(value)); }
  const settings = loadSettings();
  root.dataset.theme = settings.theme || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  root.style.setProperty('--reader-size', `${settings.fontSize || 19}px`);
  document.querySelector('[data-action="theme"]')?.addEventListener('click', () => {
    const order = ['light', 'sepia', 'dark'];
    const next = order[(order.indexOf(root.dataset.theme) + 1) % order.length];
    root.dataset.theme = next;
    saveSettings({ ...loadSettings(), theme: next });
  });
  document.querySelectorAll('[data-font-step]').forEach((button) => button.addEventListener('click', () => {
    const current = parseInt(getComputedStyle(root).getPropertyValue('--reader-size'), 10) || 19;
    const next = Math.max(17, Math.min(26, current + Number(button.dataset.fontStep)));
    root.style.setProperty('--reader-size', `${next}px`);
    saveSettings({ ...loadSettings(), fontSize: next });
  }));
  const progress = document.querySelector('.read-progress span');
  function updateProgress() {
    if (!progress) return;
    const height = root.scrollHeight - window.innerHeight;
    const percent = height > 0 ? Math.min(100, (window.scrollY / height) * 100) : 100;
    progress.style.width = `${percent}%`;
    progress.parentElement.setAttribute('aria-valuenow', String(Math.round(percent)));
  }
  window.addEventListener('scroll', updateProgress, { passive: true });
  updateProgress();
  if (currentChapter) {
    let read = new Set();
    try { read = new Set(JSON.parse(storage.getItem(readKey) || '[]')); } catch (_) { storage.removeItem(readKey); }
    read.add(currentChapter);
    storage.setItem(readKey, JSON.stringify([...read].sort((a, b) => a - b)));
    storage.setItem(lastKey, String(currentChapter));
  }
  document.addEventListener('keydown', (event) => {
    if (event.altKey || event.ctrlKey || event.metaKey) return;
    if (event.key === 'ArrowLeft') document.querySelector('.chapter-nav .prev')?.click();
    if (event.key === 'ArrowRight') document.querySelector('.chapter-nav .next')?.click();
  });
})();

(() => {
  const root = document.documentElement;
  const storage = window.localStorage;
  const key = 'murim-reader-settings';
  const currentChapter = Number(document.body.dataset.chapter || 0);

  function loadSettings() {
    try {
      return JSON.parse(storage.getItem(key)) || {};
    } catch (_) {
      return {};
    }
  }

  function saveSettings(settings) {
    storage.setItem(key, JSON.stringify(settings));
  }

  const settings = loadSettings();
  const preferredTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  root.dataset.theme = settings.theme || preferredTheme;
  root.style.setProperty('--reader-size', `${settings.fontSize || 20}px`);

  const themeButton = document.querySelector('[data-action="theme"]');
  if (themeButton) {
    themeButton.addEventListener('click', () => {
      const order = ['light', 'sepia', 'dark'];
      const next = order[(order.indexOf(root.dataset.theme) + 1) % order.length];
      root.dataset.theme = next;
      const updated = loadSettings();
      updated.theme = next;
      saveSettings(updated);
      themeButton.setAttribute('aria-label', `읽기 테마: ${next}`);
    });
  }

  document.querySelectorAll('[data-font-step]').forEach((button) => {
    button.addEventListener('click', () => {
      const current = parseInt(getComputedStyle(root).getPropertyValue('--reader-size'), 10) || 20;
      const next = Math.max(17, Math.min(26, current + Number(button.dataset.fontStep)));
      root.style.setProperty('--reader-size', `${next}px`);
      const updated = loadSettings();
      updated.fontSize = next;
      saveSettings(updated);
    });
  });

  const progress = document.querySelector('.read-progress span');
  function updateProgress() {
    if (!progress) return;
    const height = document.documentElement.scrollHeight - window.innerHeight;
    const percent = height > 0 ? Math.min(100, (window.scrollY / height) * 100) : 100;
    progress.style.width = `${percent}%`;
    progress.parentElement.setAttribute('aria-valuenow', String(Math.round(percent)));
  }
  window.addEventListener('scroll', updateProgress, { passive: true });
  updateProgress();

  if (currentChapter) {
    const read = new Set(JSON.parse(storage.getItem('murim-read-chapters') || '[]'));
    read.add(currentChapter);
    storage.setItem('murim-read-chapters', JSON.stringify([...read].sort((a, b) => a - b)));
    storage.setItem('murim-last-chapter', String(currentChapter));
  }

  document.addEventListener('keydown', (event) => {
    if (event.altKey || event.ctrlKey || event.metaKey) return;
    if (event.key === 'ArrowLeft') document.querySelector('.chapter-nav .prev')?.click();
    if (event.key === 'ArrowRight') document.querySelector('.chapter-nav .next')?.click();
  });
})();

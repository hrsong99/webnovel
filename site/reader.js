(() => {
  const root = document.documentElement;
  const storage = window.localStorage;
  const slug = document.body.dataset.storySlug;
  if (!slug) return;

  const prefix = `webnovel:${slug}`;
  const currentChapter = Number(document.body.dataset.chapter || 0);
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

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

  function saveSettings(value) {
    storage.setItem(settingsKey, JSON.stringify(value));
  }

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

  const prose = document.querySelector('.prose');
  const glossaryDialog = document.querySelector('.glossary-dialog');
  const glossaryHeading = glossaryDialog?.querySelector('#glossary-heading');
  const glossaryTranslation = glossaryDialog?.querySelector('.glossary-translation');
  const glossaryNote = glossaryDialog?.querySelector('.glossary-note');
  const focusButton = document.querySelector('[data-action="focus"]');
  const focusGuide = document.querySelector('.focus-guide');
  const focusUnits = [...document.querySelectorAll('[data-focus-unit]')];
  let focusActive = false;
  let activeFocusIndex = -1;
  let animationFrame = 0;
  let animationRunning = false;
  let focusSyncTimer = 0;
  let pointerStart = null;
  let suppressNextClick = false;

  prose?.addEventListener('click', (event) => {
    const term = event.target.closest('.glossary-term');
    if (!term || !glossaryDialog) return;
    event.preventDefault();
    event.stopPropagation();
    glossaryHeading.textContent = term.dataset.term || term.textContent;
    glossaryTranslation.textContent = term.dataset.translation || '';
    glossaryNote.textContent = term.dataset.note || '';
    glossaryNote.hidden = !glossaryNote.textContent;
    glossaryDialog.showModal();
  });

  glossaryDialog?.querySelector('[data-action="close-glossary"]')?.addEventListener('click', () => glossaryDialog.close());
  glossaryDialog?.addEventListener('click', (event) => {
    if (event.target === glossaryDialog) glossaryDialog.close();
  });

  function nearestFocusIndex() {
    const center = window.innerHeight * 0.5;
    let nearest = 0;
    let distance = Number.POSITIVE_INFINITY;
    focusUnits.forEach((unit, index) => {
      const rect = unit.getBoundingClientRect();
      const unitCenter = rect.top + Math.min(rect.height, window.innerHeight) * 0.5;
      const nextDistance = Math.abs(unitCenter - center);
      if (nextDistance < distance) {
        nearest = index;
        distance = nextDistance;
      }
    });
    return nearest;
  }

  function targetScrollY(unit) {
    const barHeight = document.querySelector('.reader-bar')?.getBoundingClientRect().height || 0;
    const rect = unit.getBoundingClientRect();
    const usableHeight = window.innerHeight - barHeight;
    const centered = window.scrollY + rect.top - barHeight - Math.max(24, (usableHeight - Math.min(rect.height, usableHeight * 0.72)) * 0.45);
    return Math.max(0, Math.min(root.scrollHeight - window.innerHeight, centered));
  }

  function animateScrollTo(unit) {
    cancelAnimationFrame(animationFrame);
    const start = window.scrollY;
    const destination = targetScrollY(unit);
    const delta = destination - start;
    if (reduceMotion.matches || Math.abs(delta) < 2) {
      animationRunning = true;
      window.scrollTo(0, destination);
      window.requestAnimationFrame(() => window.requestAnimationFrame(() => { animationRunning = false; }));
      return;
    }
    const duration = Math.max(220, Math.min(420, 220 + Math.abs(delta) * 0.12));
    const started = performance.now();
    animationRunning = true;
    const tick = (now) => {
      const elapsed = Math.min(1, (now - started) / duration);
      const eased = 1 - Math.pow(1 - elapsed, 3);
      window.scrollTo(0, start + delta * eased);
      if (elapsed < 1) {
        animationFrame = requestAnimationFrame(tick);
      } else {
        animationRunning = false;
      }
    };
    animationFrame = requestAnimationFrame(tick);
  }

  function markFocus(index, shouldScroll = true) {
    if (!focusUnits.length) return;
    activeFocusIndex = Math.max(0, Math.min(focusUnits.length - 1, index));
    focusUnits.forEach((unit, unitIndex) => {
      const active = unitIndex === activeFocusIndex;
      unit.classList.toggle('is-focus-active', active);
      unit.classList.toggle('is-focus-near', Math.abs(unitIndex - activeFocusIndex) === 1);
      if (active) unit.setAttribute('aria-current', 'true');
      else unit.removeAttribute('aria-current');
    });
    if (focusGuide) focusGuide.textContent = focusGuide.dataset.default || focusGuide.textContent;
    if (shouldScroll) animateScrollTo(focusUnits[activeFocusIndex]);
  }

  function setFocusMode(active) {
    focusActive = Boolean(active && focusUnits.length);
    document.body.classList.toggle('focus-reading', focusActive);
    focusButton?.setAttribute('aria-pressed', String(focusActive));
    if (focusActive) {
      markFocus(nearestFocusIndex());
    } else {
      cancelAnimationFrame(animationFrame);
      animationRunning = false;
      focusUnits.forEach((unit) => {
        unit.classList.remove('is-focus-active', 'is-focus-near');
        unit.removeAttribute('aria-current');
      });
      activeFocusIndex = -1;
    }
  }

  function stepFocus(direction) {
    if (!focusActive) return;
    if (direction > 0 && activeFocusIndex === focusUnits.length - 1) {
      if (focusGuide) focusGuide.textContent = focusGuide.dataset.end || focusGuide.textContent;
      document.querySelector('.chapter-nav')?.scrollIntoView({ behavior: reduceMotion.matches ? 'auto' : 'smooth', block: 'center' });
      return;
    }
    markFocus(activeFocusIndex + direction);
  }

  focusButton?.addEventListener('click', () => setFocusMode(!focusActive));

  prose?.addEventListener('pointerdown', (event) => {
    pointerStart = { id: event.pointerId, x: event.clientX, y: event.clientY };
    suppressNextClick = false;
  });

  prose?.addEventListener('pointerup', (event) => {
    if (!pointerStart || pointerStart.id !== event.pointerId) return;
    suppressNextClick = Math.hypot(event.clientX - pointerStart.x, event.clientY - pointerStart.y) > 10;
    pointerStart = null;
  });

  prose?.addEventListener('click', (event) => {
    if (event.target.closest('.glossary-term')) return;
    if (!focusActive) return;
    if (suppressNextClick) { suppressNextClick = false; return; }
    const selection = window.getSelection();
    if (selection && !selection.isCollapsed) return;
    const unit = event.target.closest('[data-focus-unit]');
    if (!unit) return;
    const index = focusUnits.indexOf(unit);
    if (index === activeFocusIndex) stepFocus(1);
    else markFocus(index);
  });

  window.addEventListener('scroll', () => {
    if (!focusActive || animationRunning) return;
    clearTimeout(focusSyncTimer);
    focusSyncTimer = window.setTimeout(() => markFocus(nearestFocusIndex(), false), 90);
  }, { passive: true });

  document.addEventListener('keydown', (event) => {
    if (event.altKey || event.ctrlKey || event.metaKey) return;
    const interactive = event.target.closest('a, button, summary, input, textarea, select');
    if (focusActive && !interactive) {
      if (event.key === 'Escape') {
        event.preventDefault();
        setFocusMode(false);
        focusButton?.focus({ preventScroll: true });
        return;
      }
      if (event.key === 'ArrowDown' || event.key === 'PageDown' || (event.key === ' ' && !event.shiftKey) || event.key.toLowerCase() === 'j') {
        event.preventDefault();
        stepFocus(1);
        return;
      }
      if (event.key === 'ArrowUp' || event.key === 'PageUp' || event.key.toLowerCase() === 'k' || (event.key === ' ' && event.shiftKey)) {
        event.preventDefault();
        stepFocus(-1);
        return;
      }
    }
    if (event.key === 'ArrowLeft') document.querySelector('.chapter-nav .prev')?.click();
    if (event.key === 'ArrowRight') document.querySelector('.chapter-nav .next')?.click();
  });

  if (!focusUnits.length && focusButton) focusButton.hidden = true;
})();

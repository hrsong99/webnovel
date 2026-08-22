(() => {
  const storage = window.localStorage;
  const language = document.body.dataset.language || 'ko';
  let read = new Set();
  try {
    read = new Set(JSON.parse(storage.getItem('murim-read-chapters') || '[]'));
  } catch (_) {
    storage.removeItem('murim-read-chapters');
  }

  document.querySelectorAll('[data-chapter-link]').forEach((link) => {
    const chapter = Number(link.dataset.chapterLink);
    if (read.has(chapter)) link.dataset.read = 'true';
  });

  const resume = document.querySelector('[data-resume]');
  const last = Number(storage.getItem('murim-last-chapter') || 0);
  if (resume && last > 0) {
    resume.href = `chapters/${String(last).padStart(2, '0')}.html`;
    resume.innerHTML = language === 'en'
      ? `Continue with chapter ${last} <span>→</span>`
      : `${last}화부터 이어 읽기 <span>→</span>`;
  }
})();

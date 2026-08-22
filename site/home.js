(() => {
  const storage = window.localStorage;
  const read = new Set(JSON.parse(storage.getItem('murim-read-chapters') || '[]'));
  document.querySelectorAll('[data-chapter-link]').forEach((link) => {
    const chapter = Number(link.dataset.chapterLink);
    if (read.has(chapter)) link.dataset.read = 'true';
  });

  const resume = document.querySelector('[data-resume]');
  const last = Number(storage.getItem('murim-last-chapter') || 0);
  if (resume && last > 0) {
    resume.href = `chapters/${String(last).padStart(2, '0')}.html`;
    resume.textContent = `${last}화부터 계속 읽기`;
  }
})();

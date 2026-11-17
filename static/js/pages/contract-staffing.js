// Mobile nav handled canonically in includes/navbar.html

// faq accordion (guarded to avoid double triggering)
document.querySelectorAll('.sv-faq-item').forEach(item => {
  const qBtn = item.querySelector('.sv-faq-q');
  if (!qBtn || qBtn.dataset.faqAttached) return;
  qBtn.dataset.faqAttached = 'true';
  qBtn.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    const wasActive = item.classList.contains('active');
    document.querySelectorAll('.sv-faq-item').forEach(i => i.classList.remove('active'));
    if (!wasActive) item.classList.add('active');
  });
});

// scroll to top
const scrollTop = document.getElementById('scrollTop');
if (scrollTop) {
  window.addEventListener('scroll', () => {
    scrollTop.classList.toggle('show', window.scrollY > 500);
  });
  scrollTop.addEventListener('click', (e) => {
    e.preventDefault();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

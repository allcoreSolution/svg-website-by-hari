// Mobile nav handled canonically in includes/navbar.html

// faq accordion
document.querySelectorAll('.sv-faq-item').forEach(item => {
  item.querySelector('.sv-faq-q').addEventListener('click', () => {
    const wasActive = item.classList.contains('active');
    document.querySelectorAll('.sv-faq-item').forEach(i => i.classList.remove('active'));
    if (!wasActive) item.classList.add('active');
  });
});

// scroll to top
const scrollTop = document.getElementById('scrollTop');
window.addEventListener('scroll', () => {
  scrollTop.classList.toggle('show', window.scrollY > 500);
});
scrollTop.addEventListener('click', (e) => {
  e.preventDefault();
  window.scrollTo({ top: 0, behavior: 'smooth' });
});
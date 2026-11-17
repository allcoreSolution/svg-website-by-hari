// ============ Recruitment & Placement Page Scripts ============

document.addEventListener('DOMContentLoaded', function () {

  /* Mobile nav handled canonically in includes/navbar.html */

  /* ---------- Scroll to top button ---------- */
  const scrollTop = document.getElementById('scrollTop');

  if (scrollTop) {
    window.addEventListener('scroll', function () {
      scrollTop.classList.toggle('show', window.scrollY > 400);
    });

    scrollTop.addEventListener('click', function (e) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  /* ---------- FAQ accordion ---------- */
  const faqItems = document.querySelectorAll('.sv-faq-item');

  faqItems.forEach(function (item) {
    const question = item.querySelector('.sv-faq-q');
    if (!question || question.dataset.faqBound) return;
    question.dataset.faqBound = 'true';

    question.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      const isActive = item.classList.contains('active');

      // close all other FAQ items in same list
      const list = item.closest('.sv-faq-list') || item.parentElement;
      if (list) {
        list.querySelectorAll('.sv-faq-item').forEach(function (other) {
          other.classList.remove('active');
        });
      }

      // toggle the clicked one
      if (!isActive) {
        item.classList.add('active');
      }
    });
  });

});
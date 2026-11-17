// Global CSRF helper for AJAX and fetch requests
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
window.getCookie = getCookie;

// mobile nav and dropdown are handled canonically in includes/navbar.html

// faq accordion
document.querySelectorAll('.sv-faq-item').forEach(item => {
  const question = item.querySelector('.sv-faq-q');
  if (question) {
    question.addEventListener('click', () => {
      const wasActive = item.classList.contains('active');
      document.querySelectorAll('.sv-faq-item').forEach(i => i.classList.remove('active'));
      if (!wasActive) item.classList.add('active');
    });
  }
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

// apply-now popup modal
document.addEventListener("DOMContentLoaded", function () {

    const popup = document.getElementById("applyModalOverlay");
    const closeBtn = document.getElementById("applyModalClose");

    // Agar popup page me nahi hai to kuch mat karo
    if (!popup) return;

    function closePopup() {
        popup.classList.remove("active");
        popup.style.display = "none";
        document.body.style.overflow = "";
        document.body.classList.remove("popup-open");
    }

    // Close button
    if (closeBtn) {
        closeBtn.addEventListener("click", closePopup);
    }

    // Popup ke bahar click
    popup.addEventListener("click", function (e) {
        if (e.target === popup) {
            closePopup();
        }
    });

    // ESC key se close
    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && popup.classList.contains("active")) {
            closePopup();
        }
    });

});

// ===== Scroll reveal for general elements =====
const revealEls = document.querySelectorAll('.reveal');
if (revealEls.length) {
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('in');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15 });
  revealEls.forEach(el => revealObserver.observe(el));
}

// ===== Timeline items reveal =====
const timelineItems = document.querySelectorAll('.timeline-item');
if (timelineItems.length) {
  const tlObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('in');
      }
    });
  }, { threshold: 0.35 });
  timelineItems.forEach(item => tlObserver.observe(item));
}

// ===== Timeline progress line grows with scroll =====
const timelineWrap = document.getElementById('timelineWrap');
const tlProgress = document.getElementById('tlProgress');
if (timelineWrap && tlProgress) {
  const updateTimelineProgress = () => {
    const rect = timelineWrap.getBoundingClientRect();
    const winH = window.innerHeight;
    const total = rect.height;
    const scrolled = winH * 0.75 - rect.top;
    let pct = (scrolled / total) * 100;
    pct = Math.max(0, Math.min(100, pct));
    tlProgress.style.height = pct + '%';
  };
  window.addEventListener('scroll', updateTimelineProgress);
  window.addEventListener('resize', updateTimelineProgress);
  updateTimelineProgress();
}

// ===== Animated counters =====
const counters = document.querySelectorAll('.counter');
if (counters.length) {
  const animateCounter = (el) => {
    const target = parseInt(el.getAttribute('data-target'), 10);
    const duration = 1600;
    const startTime = performance.now();
    const step = (now) => {
      const progress = Math.min((now - startTime) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.floor(eased * target).toLocaleString();
      if (progress < 1) {
        requestAnimationFrame(step);
      } else {
        el.textContent = target.toLocaleString();
      }
    };
    requestAnimationFrame(step);
  };

  const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        counterObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });
  counters.forEach(c => counterObserver.observe(c));
}

// ===== Hero/timeline mobile hamburger toggle (Our Journey page) =====
const hamburger = document.querySelector('.hamburger');
const navEl = document.querySelector('header nav');
if (hamburger && navEl) {
  hamburger.addEventListener('click', () => {
    const isOpen = navEl.style.display === 'block';
    navEl.style.display = isOpen ? 'none' : 'block';
    if (!isOpen) {
      navEl.style.position = 'absolute';
      navEl.style.top = '100%';
      navEl.style.left = '0';
      navEl.style.right = '0';
      navEl.style.background = '#fff';
      navEl.style.boxShadow = '0 10px 20px rgba(13,43,107,0.1)';
      navEl.style.padding = '20px 24px';
      const list = navEl.querySelector('ul');
      if (list) {
        list.style.flexDirection = 'column';
        list.style.alignItems = 'flex-start';
        list.style.gap = '16px';
      }
    }
  });
}
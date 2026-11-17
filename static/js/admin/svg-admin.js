/* =========================================================
   SVG CONSULTANCY — SUPER ADMIN PANEL JS UTILITIES & CHARTS
   ========================================================= */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Mobile Sidebar Toggle
  const hamburgerBtn = document.getElementById('adminHamburgerBtn');
  const sidebar = document.getElementById('adminSidebar');
  const overlay = document.getElementById('adminSidebarOverlay');

  if (hamburgerBtn && sidebar && overlay) {
    hamburgerBtn.addEventListener('click', () => {
      sidebar.classList.toggle('open');
      overlay.style.display = sidebar.classList.contains('open') ? 'block' : 'none';
    });

    overlay.addEventListener('click', () => {
      sidebar.classList.remove('open');
      overlay.style.display = 'none';
    });
  }

  // 2. User Profile Dropdown Toggle
  const profileBtn = document.getElementById('adminProfileBtn');
  const profileMenu = document.getElementById('adminProfileMenu');
  if (profileBtn && profileMenu) {
    profileBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      profileMenu.style.display = (profileMenu.style.display === 'block') ? 'none' : 'block';
    });
    document.addEventListener('click', (e) => {
      if (!profileBtn.contains(e.target) && !profileMenu.contains(e.target)) {
        profileMenu.style.display = 'none';
      }
    });
  }

  // 3. Application Overview Donut Chart
  const appCtx = document.getElementById('appOverviewDonut');
  if (appCtx && typeof Chart !== 'undefined') {
    const applied = parseInt(appCtx.dataset.applied || '8256', 10);
    const shortlisted = parseInt(appCtx.dataset.shortlisted || '4125', 10);
    const interview = parseInt(appCtx.dataset.interview || '3245', 10);
    const offered = parseInt(appCtx.dataset.offered || '1890', 10);
    const rejected = parseInt(appCtx.dataset.rejected || '1240', 10);

    new Chart(appCtx.getContext('2d'), {
      type: 'doughnut',
      data: {
        labels: ['Applied', 'Shortlisted', 'Interview', 'Offered', 'Rejected'],
        datasets: [{
          data: [applied, shortlisted, interview, offered, rejected],
          backgroundColor: ['#2563EB', '#10B981', '#7C3AED', '#EA580C', '#EF4444'],
          borderWidth: 2,
          borderColor: '#FFFFFF'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '74%',
        plugins: { legend: { display: false } }
      }
    });
  }

  // 4. Jobs Overview Donut Chart
  const jobsCtx = document.getElementById('jobsOverviewDonut');
  if (jobsCtx && typeof Chart !== 'undefined') {
    const live = parseInt(jobsCtx.dataset.live || '1845', 10);
    const pending = parseInt(jobsCtx.dataset.pending || '632', 10);
    const draft = parseInt(jobsCtx.dataset.draft || '328', 10);
    const expired = parseInt(jobsCtx.dataset.expired || '440', 10);

    new Chart(jobsCtx.getContext('2d'), {
      type: 'doughnut',
      data: {
        labels: ['Live Jobs', 'Pending Approval', 'Draft Jobs', 'Expired Jobs'],
        datasets: [{
          data: [live, pending, draft, expired],
          backgroundColor: ['#10B981', '#EA580C', '#2563EB', '#EF4444'],
          borderWidth: 2,
          borderColor: '#FFFFFF'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '74%',
        plugins: { legend: { display: false } }
      }
    });
  }

  // 5. Revenue Sparkline Chart
  const revCtx = document.getElementById('revenueLineChart');
  if (revCtx && typeof Chart !== 'undefined') {
    const ctx = revCtx.getContext('2d');
    const gradient = ctx.createLinearGradient(0, 0, 0, 90);
    gradient.addColorStop(0, 'rgba(37, 99, 235, 0.25)');
    gradient.addColorStop(1, 'rgba(37, 99, 235, 0.00)');

    new Chart(ctx, {
      type: 'line',
      data: {
        labels: ['01 May', '08 May', '15 May', '22 May', '29 May'],
        datasets: [{
          data: [6.5, 7.8, 7.1, 8.4, 9.5],
          borderColor: '#2563EB',
          backgroundColor: gradient,
          borderWidth: 2,
          fill: true,
          tension: 0.35,
          pointRadius: 3,
          pointBackgroundColor: '#2563EB'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false }, ticks: { font: { size: 9 }, color: '#94A3B8' } },
          y: { grid: { color: '#F1F5F9' }, ticks: { font: { size: 9 }, color: '#94A3B8' } }
        }
      }
    });
  }

  // 6. Action Dropdown Three Dots Toggle
  function closeAdminActionDropdowns() {
    document.querySelectorAll('.dropdown-menu-popup.show').forEach(m => {
      m.classList.remove('show');
      m.style.display = 'none';
    });
  }

  document.addEventListener('click', (e) => {
    const dotsBtn = e.target.closest('.btn-three-dots');
    if (dotsBtn) {
      e.preventDefault();
      e.stopPropagation();

      const dropdownWrapper = dotsBtn.closest('.action-dropdown-wrapper');
      const menu = dropdownWrapper ? dropdownWrapper.querySelector('.dropdown-menu-popup') : null;
      if (!menu) return;

      const isAlreadyOpen = menu.classList.contains('show');
      closeAdminActionDropdowns();

      if (isAlreadyOpen) return;

      // Show first so offsetHeight & bounds can be measured accurately
      menu.style.display = 'flex';
      menu.classList.add('show');
      menu.style.position = 'fixed';
      menu.style.zIndex = '999999';

      const rect = dotsBtn.getBoundingClientRect();
      const menuHeight = menu.offsetHeight || 220;
      const spaceBelow = window.innerHeight - rect.bottom;

      menu.style.left = 'auto';
      menu.style.right = Math.max(12, (window.innerWidth - rect.right)) + 'px';

      if (spaceBelow < menuHeight && rect.top > menuHeight) {
        menu.style.bottom = (window.innerHeight - rect.top + 4) + 'px';
        menu.style.top = 'auto';
      } else {
        menu.style.top = (rect.bottom + 4) + 'px';
        menu.style.bottom = 'auto';
      }
    } else if (e.target.closest('.dropdown-item-btn')) {
      setTimeout(closeAdminActionDropdowns, 120);
    } else if (!e.target.closest('.dropdown-menu-popup')) {
      closeAdminActionDropdowns();
    }
  });

  window.addEventListener('resize', closeAdminActionDropdowns);
});


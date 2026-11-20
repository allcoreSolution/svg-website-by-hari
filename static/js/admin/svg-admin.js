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

/* =========================================================
   7. MULTI-FORMAT TABLE EXPORT ENGINE (Excel, CSV, PDF, PNG, JPG)
   ========================================================= */

window.closeAdminExportMenus = function() {
  document.querySelectorAll('.admin-export-menu').forEach(menu => {
    menu.style.display = 'none';
  });
};

window.toggleAdminExportMenu = function(btn, event) {
  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }
  const wrapper = btn.closest('.admin-export-dropdown');
  const menu = wrapper ? wrapper.querySelector('.admin-export-menu') : null;
  if (!menu) return;

  const isAlreadyOpen = (menu.style.display === 'block');
  window.closeAdminExportMenus();
  if (window.closeAdminActionDropdowns) window.closeAdminActionDropdowns();

  if (!isAlreadyOpen) {
    menu.style.display = 'block';
  }
};

document.addEventListener('click', (e) => {
  if (!e.target.closest('.admin-export-dropdown')) {
    window.closeAdminExportMenus();
  }
});

window.triggerAdminTableExport = function(format, customSelector, customFileName) {
  window.closeAdminExportMenus();

  // 1. Determine Title and Clean Base File Name
  const titleEl = document.querySelector('.module-title-group h3') || 
                  document.querySelector('.admin-header-title') || 
                  document.querySelector('h1, h2, h3');
  let baseName = customFileName || (titleEl ? titleEl.textContent.trim() : 'SVG_Consultancy_Export');
  baseName = baseName.replace(/[^a-zA-Z0-9_-]/g, '_').replace(/_+/g, '_').toLowerCase();
  if (baseName.startsWith('_')) baseName = baseName.substring(1);
  if (baseName.endsWith('_')) baseName = baseName.substring(0, baseName.length - 1);
  const today = new Date().toISOString().split('T')[0];
  const fileName = `${baseName}_${today}`;

  // 2. Handle PDF via Clean Print Dialog
  if (format === 'pdf') {
    if (window.showAdminToast) window.showAdminToast('Opening Print / Save as PDF dialog...', true);
    setTimeout(() => {
      window.print();
    }, 200);
    return;
  }

  // 3. Find Table Element
  const table = customSelector ? document.querySelector(customSelector) : (document.querySelector('.admin-table') || document.querySelector('table'));
  if (!table) {
    if (window.showAdminToast) window.showAdminToast('No data table found to export.', false);
    return;
  }

  // 4. Handle High-Resolution PNG & JPG Image Export
  if (format === 'png' || format === 'jpg' || format === 'jpeg') {
    const isJpg = (format === 'jpg' || format === 'jpeg');
    const toastMsg = isJpg ? 'Generating high-quality JPG image...' : 'Generating high-resolution PNG image...';
    if (window.showAdminToast) window.showAdminToast(toastMsg, true);

    const performCapture = () => {
      if (typeof html2canvas === 'undefined') {
        if (window.showAdminToast) window.showAdminToast('Image export library loading failed. Please refresh and try again.', false);
        return;
      }

      // Best capture target: table or its immediate responsive container
      const targetWrap = table.closest('.table-responsive-wrap') || table;
      
      html2canvas(targetWrap, {
        scale: 2,
        backgroundColor: '#ffffff',
        useCORS: true,
        logging: false,
        ignoreElements: (el) => {
          if (!el || !el.classList) return false;
          return (
            el.classList.contains('action-dropdown-wrapper') ||
            el.classList.contains('dropdown-menu-popup') ||
            el.classList.contains('admin-export-menu') ||
            (el.tagName === 'BUTTON' && el.textContent.includes('Refresh'))
          );
        }
      }).then(canvas => {
        const link = document.createElement('a');
        link.download = `${fileName}.${isJpg ? 'jpg' : 'png'}`;
        link.href = isJpg ? canvas.toDataURL('image/jpeg', 0.95) : canvas.toDataURL('image/png');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        if (window.showAdminToast) window.showAdminToast(`${isJpg ? 'JPG' : 'PNG'} image downloaded successfully!`, true);
      }).catch(err => {
        console.error('Image capture error:', err);
        if (window.showAdminToast) window.showAdminToast('Failed to export image. Please try again.', false);
      });
    };

    if (typeof html2canvas === 'undefined') {
      const script = document.createElement('script');
      script.src = 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js';
      script.onload = performCapture;
      script.onerror = () => {
        if (window.showAdminToast) window.showAdminToast('Failed to load image library.', false);
      };
      document.head.appendChild(script);
    } else {
      performCapture();
    }
    return;
  }

  // 5. Extract Structured Table Data for Excel (.xlsx) & CSV
  const ths = Array.from(table.querySelectorAll('thead th'));
  const validColIndices = [];
  const headers = [];

  ths.forEach((th, idx) => {
    const text = th.innerText.trim();
    // Exclude Actions column
    if (!text.toLowerCase().includes('action') && (idx < ths.length - 1 || th.style.textAlign !== 'right')) {
      headers.push(text || `Column ${idx + 1}`);
      validColIndices.push(idx);
    }
  });

  const rows = [];
  const trs = table.querySelectorAll('tbody tr');
  trs.forEach(tr => {
    if (tr.querySelector('.table-empty') || tr.cells.length < validColIndices.length) return;

    const rowData = [];
    validColIndices.forEach(idx => {
      const cell = tr.cells[idx];
      if (!cell) {
        rowData.push('');
        return;
      }
      const clone = cell.cloneNode(true);
      clone.querySelectorAll('.action-dropdown-wrapper, .dropdown-menu-popup, button, script, noscript, style').forEach(el => el.remove());

      // Format title + subtitle cleanly if present
      const subDiv = clone.querySelector('div[style*="font-size: 11.5px"], div[style*="color: #64748b"], div[style*="color:#64748b"]');
      let cellText = '';
      if (subDiv) {
        const subText = (subDiv.innerText || subDiv.textContent || '').trim();
        subDiv.remove();
        const mainText = (clone.innerText || clone.textContent || '').trim();
        cellText = mainText ? `${mainText} (${subText.replace(/\s+/g, ' ')})` : subText;
      } else {
        cellText = clone.innerText || clone.textContent || '';
      }
      cellText = cellText.replace(/[\r\n]+/g, ' ').replace(/\s+/g, ' ').trim();
      rowData.push(cellText);
    });

    if (rowData.length > 0 && rowData.some(val => val.length > 0)) {
      rows.push(rowData);
    }
  });

  if (rows.length === 0) {
    if (window.showAdminToast) window.showAdminToast('No records found in table to export.', false);
    return;
  }

  // 6. Handle Native Excel (.xlsx) Export
  if (format === 'xlsx' || format === 'excel') {
    const performXlsxExport = () => {
      if (typeof XLSX !== 'undefined') {
        const wb = XLSX.utils.book_new();
        const ws = XLSX.utils.aoa_to_sheet([headers, ...rows]);
        
        // Dynamic column widths for readability
        ws['!cols'] = headers.map((h, i) => {
          const maxL = Math.max(h.length, ...rows.map(r => (r[i] ? String(r[i]).length : 0)));
          return { wch: Math.min(Math.max(maxL + 4, 14), 50) };
        });

        XLSX.utils.book_append_sheet(wb, ws, "Data Export");
        XLSX.writeFile(wb, `${fileName}.xlsx`);
        if (window.showAdminToast) window.showAdminToast('Excel spreadsheet (.xlsx) downloaded successfully!', true);
      } else {
        exportAsCsvFallback();
      }
    };

    if (typeof XLSX === 'undefined') {
      const script = document.createElement('script');
      script.src = 'https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js';
      script.onload = performXlsxExport;
      script.onerror = () => exportAsCsvFallback();
      document.head.appendChild(script);
    } else {
      performXlsxExport();
    }
    return;
  }

  // 7. Handle Universal CSV Export
  if (format === 'csv') {
    exportAsCsvFallback();
    return;
  }

  function exportAsCsvFallback() {
    const csvLines = [];
    csvLines.push(headers.map(h => `"${String(h).replace(/"/g, '""')}"`).join(','));
    rows.forEach(r => {
      csvLines.push(r.map(c => `"${String(c).replace(/"/g, '""')}"`).join(','));
    });
    const csvContent = '\uFEFF' + csvLines.join('\r\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${fileName}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    if (window.showAdminToast) window.showAdminToast('CSV document downloaded successfully!', true);
  }
};



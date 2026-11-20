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

/* =========================================================
   8. EMPLOYER POSTED JOBS & APPLICANTS MODAL CONTROLLER
   ========================================================= */

window.closeEmployerJobsModal = function() {
  const modal = document.getElementById('employerJobsModal');
  if (modal) modal.style.display = 'none';
};

window.toggleJobApplicants = function(elId, btn) {
  const el = document.getElementById(elId);
  if (!el) return;
  const isHidden = (el.style.display === 'none' || !el.style.display);
  el.style.display = isHidden ? 'block' : 'none';
  if (btn) {
    btn.innerHTML = `<i class="${isHidden ? 'ti ti-chevron-up' : 'ti ti-chevron-down'}"></i> ${isHidden ? 'Hide Applied Candidates' : 'View Applied Candidates'}`;
  }
};

window.openEmployerJobsModal = async function(rawId, model, name) {
  console.log('openEmployerJobsModal invoked:', { rawId, model, name });
  const modal = document.getElementById('employerJobsModal');
  if (!modal) {
    console.error('employerJobsModal DOM element not found!');
    if (window.showAdminToast) window.showAdminToast('Employer modal is initializing, please try again.', false);
    return;
  }

  // Display modal immediately with loading state
  modal.style.display = 'flex';
  const setText = (id, txt) => {
    const el = document.getElementById(id);
    if (el) el.textContent = txt;
  };

  setText('ejmCompName', name || 'Employer Details');
  setText('ejmCompStatus', 'Active');
  setText('ejmContact', 'Loading contact info...');
  setText('ejmEmailPhone', 'Loading...');
  setText('ejmLocation', 'Loading...');
  setText('ejmIndustry', 'Loading...');
  setText('ejmTotalJobsCount', '...');
  setText('ejmActiveJobsCount', '...');
  setText('ejmTotalApplicantsCount', '...');

  const loadingEl = document.getElementById('ejmLoading');
  const emptyEl = document.getElementById('ejmEmpty');
  const container = document.getElementById('ejmJobsContainer');
  if (loadingEl) loadingEl.style.display = 'block';
  if (emptyEl) emptyEl.style.display = 'none';
  if (container) {
    container.style.display = 'none';
    container.innerHTML = '';
  }

  // Build target query URLs (primary by ID, secondary fallback by name)
  let primaryUrl = '';
  if (rawId && rawId !== 'None' && String(rawId).trim() !== '' && !isNaN(parseInt(rawId))) {
    primaryUrl = `/api/admin/companies/${rawId}/jobs/`;
  } else if (name && name.trim() !== '') {
    primaryUrl = `/api/admin/companies/jobs/?name=${encodeURIComponent(name.trim())}`;
  } else {
    primaryUrl = `/api/admin/companies/0/jobs/`;
  }

  try {
    let res = await fetch(primaryUrl);
    let data = null;
    
    // If lookup by ID failed or returned 404, fallback to search by company name
    if (!res.ok && name && name.trim() !== '') {
      console.warn(`Primary lookup ${primaryUrl} returned ${res.status}. Trying fallback by name: ${name}`);
      const fallbackUrl = `/api/admin/companies/jobs/?name=${encodeURIComponent(name.trim())}`;
      const fallbackRes = await fetch(fallbackUrl);
      if (fallbackRes.ok) {
        res = fallbackRes;
      }
    }

    if (res.ok) {
      data = await res.json();
    } else {
      console.error('Fetch company jobs failed with status:', res.status);
    }

    if (loadingEl) loadingEl.style.display = 'none';

    if (data && data.status === 'success') {
      const comp = data.company || {};
      setText('ejmCompName', comp.name || name || 'Employer');
      setText('ejmCompStatus', comp.status || 'Active');
      setText('ejmContact', `${comp.primary_contact_name || 'N/A'} (${comp.primary_contact_designation || 'Contact Person'})`);
      setText('ejmEmailPhone', `${comp.email || 'N/A'} • ${comp.phone || 'N/A'}`);
      setText('ejmLocation', `${comp.city || 'N/A'}, ${comp.state || ''}`.replace(/^, |, $/g, ''));
      setText('ejmIndustry', comp.industry || 'Corporate Employer');

      const stats = data.stats || { total_jobs: 0, active_jobs: 0, total_applicants: 0 };
      setText('ejmTotalJobsCount', stats.total_jobs);
      setText('ejmActiveJobsCount', stats.active_jobs);
      setText('ejmTotalApplicantsCount', stats.total_applicants);

      if (!data.jobs || data.jobs.length === 0) {
        if (emptyEl) emptyEl.style.display = 'block';
      } else {
        if (container) {
          container.innerHTML = data.jobs.map(job => {
            const isLive = (job.status === 'LIVE' || job.status === 'Active' || job.status === 'Approved');
            const isPending = (job.status && job.status.toUpperCase().includes('PENDING'));
            const statusColor = isLive ? '#16a34a' : (isPending ? '#d97706' : '#64748b');
            const statusBg = isLive ? '#dcfce7' : (isPending ? '#fef3c7' : '#f1f5f9');

            let applicantsListHtml = '';
            if (job.applicants && job.applicants.length > 0) {
              applicantsListHtml = `
                <div id="ejm_apps_${job.raw_id}" style="display:none; margin-top:14px; border-top:1px dashed #cbd5e1; padding-top:14px; background:#f8fafc; border-radius:10px; padding:14px;">
                  <div style="font-size:12.5px; font-weight:700; color:#1e293b; margin-bottom:10px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:6px;">
                    <span style="display:flex; align-items:center; gap:6px; color:#2563eb;">
                      <i class="ti ti-user-check"></i> Candidates Who Applied (${job.applicants_count})
                    </span>
                    <a href="/admin-panel/candidates/all/?job_id=${job.raw_id}" target="_blank" style="font-size:11.5px; color:#2563eb; text-decoration:none; font-weight:600;">
                      Manage in Candidate Tracker &rarr;
                    </a>
                  </div>
                  <div style="overflow-x:auto;">
                    <table style="width:100%; border-collapse:collapse; font-size:12px; min-width:620px;">
                      <thead>
                        <tr style="border-bottom:1.5px solid #cbd5e1; color:#475569; font-size:11px; text-transform:uppercase; text-align:left; background:#f1f5f9;">
                          <th style="padding:8px 10px; border-radius:4px 0 0 4px;">ID / Ref</th>
                          <th style="padding:8px 10px;">Candidate Name</th>
                          <th style="padding:8px 10px;">Contact (Email / Phone)</th>
                          <th style="padding:8px 10px;">City & Experience</th>
                          <th style="padding:8px 10px;">Applied Date</th>
                          <th style="padding:8px 10px;">Status</th>
                          <th style="padding:8px 10px; text-align:right; border-radius:0 4px 4px 0;">Resume</th>
                        </tr>
                      </thead>
                      <tbody>
                        ${job.applicants.map(app => `
                          <tr style="border-bottom:1px solid #e2e8f0; background:#ffffff;">
                            <td style="padding:8px 10px; font-weight:700; color:#3b82f6;">${app.id}</td>
                            <td style="padding:8px 10px; font-weight:700; color:#0f172a;">${app.full_name}</td>
                            <td style="padding:8px 10px; color:#334155; line-height:1.3;">
                              <div>${app.email}</div>
                              <small style="color:#64748b; font-weight:500;">${app.phone}</small>
                            </td>
                            <td style="padding:8px 10px; color:#334155; line-height:1.3;">
                              <div>${app.city}</div>
                              <small style="color:#64748b;">${app.experience}</small>
                            </td>
                            <td style="padding:8px 10px; color:#64748b; white-space:nowrap;">${app.applied_on}</td>
                            <td style="padding:8px 10px;">
                              <span class="status-badge" style="background:#e0f2fe; color:#0369a1; font-size:11px; font-weight:600; padding:2px 8px; border-radius:12px; display:inline-block;">
                                ${app.status || 'Applied'}
                              </span>
                            </td>
                            <td style="padding:8px 10px; text-align:right;">
                              ${app.resume_url ? `
                                <a href="${app.resume_url}" target="_blank" class="btn btn-sm" style="padding:3px 9px; font-size:11px; background:#2563eb; color:#ffffff; border-radius:4px; text-decoration:none; display:inline-flex; align-items:center; gap:4px; font-weight:600;">
                                  <i class="ti ti-file-text"></i> Resume
                                </a>
                              ` : `<span style="color:#94a3b8; font-size:11px;">No file</span>`}
                            </td>
                          </tr>
                        `).join('')}
                      </tbody>
                    </table>
                  </div>
                </div>
              `;
            }

            return `
              <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:18px; box-shadow:0 1px 3px rgba(0,0,0,0.04); transition:all 0.2s ease;">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px; flex-wrap:wrap; gap:8px;">
                  <div>
                    <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
                      <span style="font-size:16px; font-weight:800; color:#0f172a;">${job.title}</span>
                      <span style="font-size:11px; font-weight:700; color:#475569; background:#f1f5f9; padding:2px 8px; border-radius:4px; border:1px solid #e2e8f0;">${job.id}</span>
                      <span class="status-badge" style="background:${statusBg}; color:${statusColor}; font-size:11px; font-weight:700; padding:2px 8px; border-radius:12px; border:1px solid rgba(0,0,0,0.05);">${job.status}</span>
                    </div>
                    <div style="font-size:12.5px; color:#64748b; margin-top:6px; display:flex; flex-wrap:wrap; gap:12px;">
                      <span><i class="ti ti-category" style="color:#2563eb;"></i> ${job.category}</span>
                      <span><i class="ti ti-map-pin" style="color:#ef4444;"></i> ${job.location}</span>
                      <span><i class="ti ti-clock" style="color:#8b5cf6;"></i> ${job.employment_type}</span>
                      <span><i class="ti ti-coin" style="color:#16a34a;"></i> ${job.salary}</span>
                    </div>
                  </div>
                  <div style="text-align:right;">
                    <span style="font-size:11.5px; color:#64748b;"><i class="ti ti-calendar"></i> Posted: <strong>${job.created_at}</strong></span>
                  </div>
                </div>

                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:14px; padding-top:12px; border-top:1px solid #f1f5f9; flex-wrap:wrap; gap:8px;">
                  <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">
                    <span style="background:${job.applicants_count > 0 ? '#eff6ff' : '#f8fafc'}; color:${job.applicants_count > 0 ? '#1d4ed8' : '#64748b'}; font-size:13px; font-weight:700; padding:6px 14px; border-radius:20px; border:1px solid ${job.applicants_count > 0 ? '#bfdbfe' : '#e2e8f0'}; display:inline-flex; align-items:center; gap:6px;">
                      <i class="ti ti-users"></i> ${job.applicants_count} Candidate${job.applicants_count === 1 ? '' : 's'} Applied
                    </span>
                    ${job.applicants_count > 0 ? `
                      <button type="button" class="btn-admin" style="font-size:12px; font-weight:600; padding:6px 14px; background:#f8fafc; color:#1e293b; border:1px solid #cbd5e1; border-radius:6px; cursor:pointer; display:inline-flex; align-items:center; gap:6px; box-shadow:0 1px 2px rgba(0,0,0,0.03);" onclick="toggleJobApplicants('ejm_apps_${job.raw_id}', this)">
                        <i class="ti ti-chevron-down"></i> View Applied Candidates (${job.applicants_count})
                      </button>
                    ` : ''}
                  </div>
                  <div>
                    <a href="/admin-panel/candidates/all/?job_id=${job.raw_id}" target="_blank" class="btn-admin btn-admin-secondary" style="font-size:12px; padding:6px 12px; text-decoration:none; display:inline-flex; align-items:center; gap:6px; font-weight:600;">
                      <i class="ti ti-external-link"></i> Candidate Tracker
                    </a>
                  </div>
                </div>
                ${applicantsListHtml}
              </div>
            `;
          }).join('');
          container.style.display = 'flex';
        }
      }
    } else {
      if (emptyEl) emptyEl.style.display = 'block';
    }
  } catch (err) {
    console.error('Error fetching company jobs:', err);
    if (loadingEl) loadingEl.style.display = 'none';
    if (emptyEl) emptyEl.style.display = 'block';
  }
};

// Dedicated navigation for Employer Posted Jobs & Hiring Status Page
window.openEmployerJobsModal = function(rawId, model, name) {
  if (rawId) {
    window.location.href = `/admin-panel/companies/${rawId}/jobs/`;
  } else if (name) {
    window.location.href = `/admin-panel/companies/detail/?name=${encodeURIComponent(name)}`;
  } else {
    window.location.href = '/admin-panel/companies/all/';
  }
};

// Delegated click listener for employer company name links
document.addEventListener('click', (e) => {
  const link = e.target.closest('.employer-company-name-link');
  if (link) {
    e.preventDefault();
    e.stopPropagation();
    const rawId = link.getAttribute('data-raw-id') || link.dataset.rawId;
    const name = link.getAttribute('data-name') || link.dataset.name || link.innerText.trim();
    if (rawId) {
      window.location.href = `/admin-panel/companies/${rawId}/jobs/`;
    } else if (name) {
      window.location.href = `/admin-panel/companies/detail/?name=${encodeURIComponent(name)}`;
    } else {
      window.location.href = '/admin-panel/companies/all/';
    }
  }
});




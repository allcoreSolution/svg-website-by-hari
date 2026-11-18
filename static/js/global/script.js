// Global CSRF cookie helper

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



console.log("JavaScript Connected Successfully");



document.addEventListener("DOMContentLoaded", () => {



  /* =========================================================

     SWIPERS

  ========================================================= */

  if (document.querySelector(".jobSwiper")) {

    new Swiper(".jobSwiper", {

      loop: true,

      speed: 2500,

      spaceBetween: 20,

      centeredSlides: false,

      autoplay: { delay: 800, disableOnInteraction: false },

      breakpoints: {

        0: { slidesPerView: 2, slidesPerGroup: 2 },

        576: { slidesPerView: 2, slidesPerGroup: 2 },

        768: { slidesPerView: 3, slidesPerGroup: 3 },

        992: { slidesPerView: 4, slidesPerGroup: 4 },

        1200: { slidesPerView: 5, slidesPerGroup: 5 },

        1400: { slidesPerView: 6, slidesPerGroup: 6 }

      }

    });

  }



  if (document.querySelector(".employerSwiper")) {

    new Swiper(".employerSwiper", {

      slidesPerView: 1,

      spaceBetween: 30,

      loop: true,

      speed: 800,

      autoplay: { delay: 3500, disableOnInteraction: false },

      navigation: {

        nextEl: ".swiper-button-next",

        prevEl: ".swiper-button-prev"

      }

    });

  }



  /* =========================================================

     LATEST JOB FILTER

  ========================================================= */

  const filterBtns = document.querySelectorAll(".filter-btn");



  filterBtns.forEach((btn) => {

    btn.addEventListener("click", () => {

      filterBtns.forEach((b) => b.classList.remove("active"));

      btn.classList.add("active");

      const filterValue = (btn.getAttribute("data-filter") || "").toLowerCase().trim();



      const jobCards = document.querySelectorAll(".latest-job-card, .job-card, .jc-icon-card");

      jobCards.forEach((card) => {

        const category = (card.getAttribute("data-category") || "").toLowerCase().trim();

        const matchesFilter = filterValue === "all" ||

                              category === filterValue ||

                              (filterValue === "wfh" && (category === "wfh" || category.includes("work") || category.includes("home") || category.includes("remote"))) ||

                              (filterValue === "fulltime" && (category === "fulltime" || category.includes("full"))) ||

                              (filterValue === "parttime" && (category === "parttime" || category.includes("part"))) ||

                              (filterValue === "other" && (category === "other" || (!category.includes("full") && !category.includes("part") && !category.includes("home") && !category.includes("remote") && !category.includes("wfh"))));



        if (matchesFilter) {

          card.style.display = "";

          card.removeAttribute("hidden");

        } else {

          card.style.display = "none";

          card.setAttribute("hidden", "");

        }

      });

    });

  });



  /* =========================================================

     DYNAMIC LATEST JOBS LOADER (From Backend API)

  ========================================================= */

  async function loadLatestJobsFromAPI() {

    const jobsGrid = document.querySelector(".jobs-grid") || document.querySelector(".latest-jobs-grid") || document.getElementById("ljGrid") || document.querySelector(".latest-job-grid");

    if (!jobsGrid) return;



    // If server-rendered Django template cards already exist, do not inject duplicates!

    if (jobsGrid.querySelectorAll(".job-card, .jc-icon-card").length > 0) return;



    const apiBase = window.location.origin;



    try {

      const response = await fetch(`${apiBase}/api/jobs`);

      if (!response.ok) return;

      const jobs = await response.json();

      if (!Array.isArray(jobs) || jobs.length === 0) return;



      const isDetailGrid = jobsGrid.id === "ljGrid" || jobsGrid.classList.contains("latest-job-grid");



      function getJobTheme(title, filterTag) {

        const t = (title || "").toLowerCase();

        if (t.includes("sales") || t.includes("marketing") || t.includes("executive")) {

          return { ribbon: "#3654FF", iconBg: "#E7ECFF", icon: "fa-chart-line" };

        } else if (t.includes("bpo") || t.includes("customer") || t.includes("tele") || t.includes("call") || t.includes("support")) {

          return { ribbon: "#7C3AED", iconBg: "#F3E8FF", icon: "fa-headset" };

        } else if (t.includes("delivery") || t.includes("driver") || t.includes("logistics")) {

          return { ribbon: "#E0620F", iconBg: "#FEEEE0", icon: "fa-truck-fast" };

        } else if (t.includes("computer") || t.includes("data") || t.includes("operator") || t.includes("office")) {

          return { ribbon: "#0284C7", iconBg: "#E0F2FE", icon: "fa-laptop-code" };

        } else if (t.includes("developer") || t.includes("designer") || t.includes("it") || t.includes("software")) {

          return { ribbon: "#2563EB", iconBg: "#EFF6FF", icon: "fa-code" };

        } else if (t.includes("hr") || t.includes("recruiter") || t.includes("manager") || t.includes("admin")) {

          return { ribbon: "#059669", iconBg: "#ECFDF5", icon: "fa-user-tie" };

        }



        if (filterTag === "wfh") return { ribbon: "#7C3AED", iconBg: "#F3E8FF", icon: "fa-house-laptop" };

        if (filterTag === "parttime") return { ribbon: "#E0620F", iconBg: "#FEEEE0", icon: "fa-clock" };

        return { ribbon: "#3654FF", iconBg: "#E7ECFF", icon: "fa-briefcase" };

      }



      function getJobSkills(title, reqs) {

        const t = (title || "").toLowerCase();

        let skills = [];



        if (reqs && reqs.length > 5 && !reqs.toLowerCase().includes("relevant")) {

          skills = reqs.split(/[,;\n•]/).map(s => s.trim()).filter(s => s.length > 1 && s.length < 25);

        }



        if (skills.length === 0) {

          if (t.includes("sales")) skills = ["Communication", "Lead Generation", "Negotiation", "CRM Software", "Target Achievement"];

          else if (t.includes("marketing")) skills = ["Digital Marketing", "Social Media", "Lead Gen", "Content Strategy"];

          else if (t.includes("delivery") || t.includes("driver")) skills = ["Navigation", "Time Management", "Vehicle Driving", "Customer Handling"];

          else if (t.includes("computer") || t.includes("data") || t.includes("operator")) skills = ["MS Office", "Excel Data Entry", "Typing Speed", "Office Admin"];

          else if (t.includes("bpo") || t.includes("customer") || t.includes("support")) skills = ["Customer Support", "Communication", "Problem Solving", "Calling Skills"];

          else if (t.includes("developer") || t.includes("web") || t.includes("it")) skills = ["HTML/CSS", "JavaScript", "Problem Solving", "Code Quality"];

          else if (t.includes("hr") || t.includes("recruiter")) skills = ["Sourcing", "Interviewing", "Screening", "Team Handling"];

          else skills = ["Communication", "Teamwork", "Problem Solving", "Work Dedication"];

        }



        return skills.slice(0, 5).map(s => `<span>${s}</span>`).join("");

      }



      let dynamicCardsHTML = "";

      jobs.forEach(job => {

        const typeLower = (job.employment_type || "Full Time").toLowerCase().replace(/\s+/g, "");

        let typeClass = "full-time";

        let filterTag = "fulltime";



        if (typeLower.includes("part")) {

          typeClass = "part-time";

          filterTag = "parttime";

        } else if (typeLower.includes("home") || typeLower.includes("wfh") || typeLower.includes("remote")) {

          typeClass = "work-home";

          filterTag = "wfh";

        }



        let rawDesc = job.description || (job.category ? job.category + ' hiring requirement' : 'Find your dream career opportunity.');

        let cleanDesc = rawDesc

          .replace(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g, '')

          .replace(/(\+?\d{1,4}[\s-]?)?\(?\d{3,5}\)?[\s-]?\d{3,5}[\s-]?\d{3,5}/g, '')

          .replace(/Contact Recruiter:\s*/gi, '')

          .replace(/\(\s*,\s*\)/g, '')

          .replace(/\(\s*\)/g, '')

          .replace(/\s+/g, ' ')

          .trim();



        let cleanCompany = (job.category || 'Corporate Employer').replace(/\s*\([^)]*\)/g, '').trim() || 'Corporate Employer';



        if (isDetailGrid) {

          let theme = getJobTheme(job.title, filterTag);

          let skillsTags = getJobSkills(job.title, job.requirements);

          let expText = (job.experience && job.experience.trim() !== '' && isNaN(job.experience) && job.experience !== '1') ? job.experience : 'Graduate (Any Stream)';



          dynamicCardsHTML += `

            <div class="jc-icon-card jc-detail-card" data-category="${filterTag}" data-field="all" style="--ribbon-color:${theme.ribbon};">

              <div class="jc-detail-ribbon"></div>

              <div class="jc-detail-header">

                <div class="jc-detail-icon" style="background:${theme.iconBg};color:${theme.ribbon};"><i class="fa-solid ${theme.icon}"></i></div>

                <h4>${job.title}</h4>

              </div>

              <ul class="jc-detail-info">

                <li><i class="fa-solid fa-building"></i> ${cleanCompany}</li>

                <li><i class="fa-solid fa-location-dot"></i> ${job.location || 'Lucknow, UP'}</li>

                <li><i class="fa-solid fa-indian-rupee-sign"></i> ${job.salary || 'Best in Industry'}</li>

                <li><i class="fa-solid fa-briefcase"></i> Job Type: ${job.employment_type || 'Full Time'}</li>

                <li><i class="fa-solid fa-graduation-cap"></i> ${expText}</li>

              </ul>

              <div class="jc-detail-skills">

                <span class="jc-detail-skills-label">Key Skills</span>

                <div class="jc-detail-skills-tags">

                  ${skillsTags}

                </div>

              </div>

              <div class="jc-detail-footer">

                <span><i class="far fa-clock"></i> Fresh Opening</span>

                <div class="job-actions-btns">

                  <button type="button" class="job-action-btn js-share-job-btn" data-job-id="${job.id}" data-job-title="${job.title}" title="Share Job">

                    <i class="fa-solid fa-share-nodes"></i>

                  </button>

                  <button type="button" class="job-action-btn js-save-job-btn" data-job-id="${job.id}" data-job-title="${job.title}" title="Save Job">

                    <i class="fa-regular fa-bookmark"></i>

                  </button>

                </div>

                <a href="#" class="apply-btn open-job-modal-btn" data-job-id="${job.id}" data-job-title="${job.title}">Apply Now</a>

                <span class="jc-detail-caption"><i class="fa-solid fa-shield-halved"></i> Sky Vision Verified</span>

              </div>

            </div>

          `;

        } else {

          dynamicCardsHTML += `

            <div class="job-card" data-category="${filterTag}" data-job-id="${job.id}">

              <span class="job-type ${typeClass}">${job.employment_type || 'Full Time'}</span>

              <div class="job-logo"><i class="fa-solid fa-building"></i></div>

              <h3>${job.title}</h3>

              <p>${cleanDesc}</p>

              <div class="job-meta">

                <span><i class="fas fa-map-marker-alt"></i> ${job.location || 'Lucknow'}</span>

                <span><i class="fas fa-money-bill-wave"></i> ${job.salary || 'Best in Industry'}</span>

              </div>

              <div class="job-footer">

                <span><i class="far fa-clock"></i> Fresh Opening</span>

                <div class="job-actions-btns">

                  <button type="button" class="job-action-btn js-share-job-btn" data-job-id="${job.id}" data-job-title="${job.title}" title="Share Job">

                    <i class="fa-solid fa-share-nodes"></i>

                  </button>

                  <button type="button" class="job-action-btn js-save-job-btn" data-job-id="${job.id}" data-job-title="${job.title}" title="Save Job">

                    <i class="fa-regular fa-bookmark"></i>

                  </button>

                </div>

                <a href="#" class="apply-btn open-job-modal-btn" data-job-id="${job.id}" data-job-title="${job.title}">Apply Now</a>

              </div>

            </div>

          `;

        }

      });



      if (dynamicCardsHTML) {

        jobsGrid.insertAdjacentHTML('afterbegin', dynamicCardsHTML);

        const activeFilterBtn = document.querySelector(".filter-btn.active, .lj-filter-btn.active");

        if (activeFilterBtn) {

          activeFilterBtn.click();

        }

        if (typeof ensureJobCardActionButtons === "function") {

          ensureJobCardActionButtons();

        }

      }

    } catch (err) {

      console.log("Latest jobs API load note:", err);

    }

  }



  loadLatestJobsFromAPI();



  /* =========================================================

     APPLY POPUP MODAL (#applyModalOverlay)

  ========================================================= */

  const popup = document.getElementById("applyModalOverlay");

  const popupClose = document.getElementById("applyModalClose");



  function openApplyModal() {

    if (popup) {

      popup.classList.add("active");

      popup.style.display = "flex";

      document.body.classList.add("popup-open");

    }

  }



  function closeApplyModal() {

    if (popup) {

      popup.classList.remove("active");

      popup.style.display = "none";

      document.body.classList.remove("popup-open");

    }

  }



  if (popup) {

    if (popupClose) {

      popupClose.addEventListener("click", closeApplyModal);

    }



    popup.addEventListener("click", (e) => {

      if (e.target === popup) {

        closeApplyModal();

      }

    });



    document.addEventListener("keydown", (e) => {

      if (e.key === "Escape" && popup.classList.contains("active")) {

        closeApplyModal();

      }

    });

  }



  // Open triggers for #applyModalOverlay (service apply buttons)

  document.querySelectorAll(".js-apply-modal, .js-apply-modal-open, .apply-service-btn, .apply-franchise-btn").forEach((btn) => {

    btn.addEventListener("click", (e) => {

      e.preventDefault();

      openApplyModal();

    });

  });



  /* =========================================================

     ANIMATED STAT COUNTERS

  ========================================================= */

  const stats = document.querySelectorAll(".stat h3[data-count]");

  if (stats.length) {

    const animateCount = (el) => {

      const target = parseInt(el.getAttribute("data-count"), 10);

      const duration = 1400;

      const start = performance.now();

      const step = (now) => {

        const progress = Math.min((now - start) / duration, 1);

        const eased = 1 - Math.pow(1 - progress, 3);

        el.textContent = Math.floor(eased * target).toLocaleString("en-IN");

        if (progress < 1) requestAnimationFrame(step);

        else el.textContent = target.toLocaleString("en-IN") + "+";

      };

      requestAnimationFrame(step);

    };



    const statObserver = new IntersectionObserver((entries) => {

      entries.forEach((entry) => {

        if (entry.isIntersecting) {

          animateCount(entry.target);

          statObserver.unobserve(entry.target);

        }

      });

    }, { threshold: 0.4 });



    stats.forEach((el) => statObserver.observe(el));

  }



  /* =========================================================

     FEATURED CANDIDATES / EMPLOYERS CAROUSEL

  ========================================================= */

  const track = document.querySelector(".carousel-track");

  const prevBtn = document.getElementById("prevEmp");

  const nextBtn = document.getElementById("nextEmp");



  if (track && prevBtn && nextBtn) {

    const scrollAmount = () => track.querySelector(".employer-card").offsetWidth + 22;

    prevBtn.addEventListener("click", () => track.scrollBy({ left: -scrollAmount(), behavior: "smooth" }));

    nextBtn.addEventListener("click", () => track.scrollBy({ left: scrollAmount(), behavior: "smooth" }));

  }



  /* =========================================================
     MOBILE NAV TOGGLE & DROPDOWN (Handled in includes/navbar.html)
  ========================================================= */
  // Mobile nav and dropdown listeners are handled canonically in includes/navbar.html
  // to prevent double-toggle and event listener conflicts.



  /* =========================================================

     FAQ ACCORDION

  ========================================================= */

  document.querySelectorAll(".sv-faq-item, .faq-item").forEach((item) => {

    const q = item.querySelector(".sv-faq-q, .faq-q");

    if (!q || q.dataset.faqBound || q.dataset.faqAttached) return;

    q.dataset.faqBound = "true";

    q.dataset.faqAttached = "true";

    q.addEventListener("click", (e) => {

      e.preventDefault();

      e.stopPropagation();

      const wasActive = item.classList.contains("active");

      const list = item.closest(".sv-faq-list, .po-faq-grid, .cs-benefits-faq-grid") || item.parentElement;

      if (list) {

        list.querySelectorAll(".sv-faq-item, .faq-item").forEach((i) => i.classList.remove("active"));

      }

      if (!wasActive) item.classList.add("active");

    });

  });



  /* =========================================================

     SCROLL TO TOP

  ========================================================= */

  const scrollTopBtn = document.getElementById("scrollTop");

  if (scrollTopBtn) {

    window.addEventListener("scroll", () => {

      scrollTopBtn.classList.toggle("show", window.scrollY > 400);

    });

    scrollTopBtn.addEventListener("click", (e) => {

      e.preventDefault();

      window.scrollTo({ top: 0, behavior: "smooth" });

    });

  }



});

/* =========================================================

   LIVE UPDATE WIDGET — counters

========================================================= */

document.addEventListener("DOMContentLoaded", () => {



  const jobsEl = document.getElementById("todayJobs");

  const candidatesEl = document.getElementById("todayCandidate");

  const closeBtn = document.getElementById("liveWidgetClose");

  const widget = document.getElementById("liveWidget");



  if (!jobsEl || !candidatesEl) return;



  let jobs = 128;

  let candidates = 54;



  jobsEl.textContent = jobs;

  candidatesEl.textContent = candidates;



  // demo "live" increase — replace with real API data when available

  const liveTimer = setInterval(() => {

    jobs += Math.random() < 0.5 ? 1 : 0;

    candidates += Math.random() < 0.3 ? 1 : 0;

    jobsEl.textContent = jobs;

    candidatesEl.textContent = candidates;

  }, 4000);



  if (closeBtn && widget) {

    closeBtn.addEventListener("click", () => {

      widget.style.display = "none";

      clearInterval(liveTimer);

    });

  }

});

/* =========================================================

   LATEST JOBS — filter pills + View All (expand in place)

========================================================= */

document.addEventListener("DOMContentLoaded", () => {



  const filterBtns = document.querySelectorAll(".lj-filter-btn");

  const grid = document.getElementById("ljGrid");

  const viewAllBtn = document.getElementById("ljViewAllBtn");



  if (!grid || !filterBtns.length) return;



  let currentFilter = "all";

  let expanded = false;



  function render() {

    const cards = grid.querySelectorAll(".jc-icon-card, .job-card, .latest-job-card");

    let visibleCount = 0;



    cards.forEach((card) => {

      const category = (card.getAttribute("data-category") || "").toLowerCase().trim();

      const matchesFilter = currentFilter === "all" ||

                            category === currentFilter ||

                            (currentFilter === "wfh" && (category === "wfh" || category.includes("work") || category.includes("home") || category.includes("remote"))) ||

                            (currentFilter === "fulltime" && (category === "fulltime" || category.includes("full"))) ||

                            (currentFilter === "parttime" && (category === "parttime" || category.includes("part"))) ||

                            (currentFilter === "other" && (category === "other" || (!category.includes("full") && !category.includes("part") && !category.includes("home") && !category.includes("remote") && !category.includes("wfh"))));



      if (!matchesFilter) {

        card.style.display = "none";

        return;

      }



      const isExtra = card.classList.contains("lj-extra");



      if (currentFilter === "all" && isExtra && !expanded) {

        card.style.display = "none";

      } else {

        card.style.display = "";

      }



      visibleCount++;

    });



    // Only show the View All button when browsing "All Jobs" and there

    // are extra cards to reveal.

    const hasExtra = grid.querySelectorAll(".lj-extra").length > 0;



    if (viewAllBtn) {

      if (currentFilter === "all" && hasExtra) {

        viewAllBtn.style.display = "inline-flex";

        viewAllBtn.innerHTML = expanded

          ? 'View Less <i class="fa-solid fa-chevron-up"></i>'

          : 'View All Jobs <i class="fa-solid fa-chevron-down"></i>';

      } else {

        viewAllBtn.style.display = "none";

      }

    }

  }



  filterBtns.forEach((btn) => {

    btn.addEventListener("click", () => {

      filterBtns.forEach((b) => b.classList.remove("active"));

      btn.classList.add("active");

      currentFilter = (btn.getAttribute("data-filter") || "").toLowerCase().trim();

      expanded = false;

      render();

    });

  });



  if (viewAllBtn) {

    viewAllBtn.addEventListener("click", () => {

      expanded = !expanded;

      render();

      if (expanded) {

        viewAllBtn.scrollIntoView({ behavior: "smooth", block: "nearest" });

      }

    });

  }



  render();

});

/* =========================================================

   LATEST JOBS — filter by field via URL (?field=sales etc.)

   Triggered when a job-pill on index.html is clicked.

========================================================= */

document.addEventListener("DOMContentLoaded", () => {



  const params = new URLSearchParams(window.location.search);

  const field = params.get("field");

  if (!field) return;



  const grid = document.getElementById("ljGrid");

  if (!grid) return;



  const cards = grid.querySelectorAll(".jc-icon-card");

  let matchCount = 0;



  cards.forEach((card) => {

    const fields = (card.getAttribute("data-field") || "").split(" ");

    const isMatch = fields.includes(field);

    card.style.display = isMatch ? "flex" : "none";

    if (isMatch) matchCount++;

  });



  // Keep the employment-type pills on "All Jobs" so they don't visually

  // clash with this field-based filter.

  document.querySelectorAll(".lj-filter-btn").forEach((btn) => {

    btn.classList.toggle("active", btn.getAttribute("data-filter") === "all");

  });



  // Hide "View All Jobs" — every matching job is already visible.

  const viewAllBtn = document.getElementById("ljViewAllBtn");

  if (viewAllBtn) viewAllBtn.style.display = "none";



  // Friendly empty state if this field has no jobs yet.

  if (matchCount === 0) {

    const empty = document.createElement("p");

    empty.className = "lj-empty-msg";

    empty.textContent = "No openings in this category right now — check back soon or browse all jobs below.";

    grid.after(empty);

  }



  const section = grid.closest("section");

  if (section) {

    window.scrollTo({ top: section.offsetTop - 90, behavior: "smooth" });

  }

});

/* =========================================================

   JOB CATEGORIES — click a tile to see matching jobs inline,

   with a Back button to return to the category grid.

========================================================= */

document.addEventListener("DOMContentLoaded", () => {



  const catTiles = document.querySelectorAll(".job-cat-tile[data-field]");

  const catGrid = document.getElementById("jobCatGrid");

  const catView = document.getElementById("categoryJobsView");

  const catViewGrid = document.getElementById("categoryJobsGrid");

  const catViewTitle = document.getElementById("categoryJobsTitle");

  const backBtn = document.getElementById("categoryBackBtn");

  const masterGrid = document.getElementById("ljGrid");



  if (!catTiles.length || !catGrid || !catView || !catViewGrid || !masterGrid) return;



  catTiles.forEach((tile) => {

    tile.addEventListener("click", (e) => {

      e.preventDefault();

      const field = tile.getAttribute("data-field");

      const label = tile.querySelector("b") ? tile.querySelector("b").textContent : "Jobs";



      catViewGrid.innerHTML = "";



      const allCards = masterGrid.querySelectorAll(".jc-icon-card");

      let count = 0;



      allCards.forEach((card) => {

        const cardRaw = (card.getAttribute("data-field") || "").toLowerCase();

        const fld = (field || "").toLowerCase();

        const fields = cardRaw.split(/\s+/);

        const cardNormalized = cardRaw.replace(/[^a-z0-9]/g, "");

        const fldNormalized = fld.replace(/[^a-z0-9]/g, "");



        if (

          fields.includes(fld) ||

          cardRaw.includes(fld) ||

          (fldNormalized && cardNormalized.includes(fldNormalized))

        ) {

          const clone = card.cloneNode(true);

          clone.classList.remove("lj-hidden", "lj-extra");

          clone.style.display = "flex";

          catViewGrid.appendChild(clone);

          count++;

        }

      });



      if (count === 0) {

        catViewGrid.innerHTML = '<p class="lj-empty-msg">No openings in this category right now — check back soon.</p>';

      }



      if (catViewTitle) catViewTitle.textContent = label;



      catGrid.style.display = "none";

      catView.style.display = "block";

      catView.scrollIntoView({ behavior: "smooth", block: "start" });

    });

  });



  if (backBtn) {

    backBtn.addEventListener("click", () => {

      catView.style.display = "none";

      catGrid.style.display = "grid";

      catGrid.scrollIntoView({ behavior: "smooth", block: "start" });

    });

  }

});

const jobTypeTiles = document.querySelectorAll(".job-type-tile");



jobTypeTiles.forEach(tile => {

  tile.addEventListener("click", function (e) {

    e.preventDefault();

    const filter = (this.dataset.filter || "").toLowerCase();



    const filterTarget = document.querySelector("#ljFilterPills, .job-filter");

    if (filterTarget) {

      filterTarget.scrollIntoView({ behavior: "smooth" });

    }



    const btn = document.querySelector(

      `.lj-filter-btn[data-filter="${filter}"], .filter-btn[data-filter="${filter}"]`

    );



    if (btn) {

      btn.click();

    } else {

      const allFilterBtns = document.querySelectorAll(".lj-filter-btn");

      allFilterBtns.forEach(b => b.classList.remove("active"));



      const cards = document.querySelectorAll("#ljGrid .jc-icon-card, #ljGrid .job-card, #ljGrid .latest-job-card");

      cards.forEach(card => {

        const cat = (card.getAttribute("data-category") || "").toLowerCase();

        const info = (card.textContent || "").toLowerCase();

        if (cat.includes(filter) || info.includes(filter)) {

          card.style.display = "";

        } else {

          card.style.display = "none";

        }

      });

    }

  });

});

/* =========================================================

   SCROLL REVEAL — auto-applies to homepage cards & sections

   No HTML edits needed — this finds the elements itself.

========================================================= */

document.addEventListener("DOMContentLoaded", () => {



  const selectors = [

    ".section-title",

    ".hero-copy",

    ".hero-stat-badge",

    ".job-cat-tile",

    ".service-card",

    ".why-card",

    ".industry-item",

    ".internship-card",

    ".employer-card",

    ".job-card",

    ".gallery-card",

    ".gallery-info-box",

    ".info-box"

  ];



  const els = document.querySelectorAll(selectors.join(","));

  if (!els.length) return;



  // Stagger elements that share the same parent, so grids/lists

  // animate one after another instead of all at once.

  const delayCounters = new WeakMap();



  els.forEach((el) => {

    el.classList.add("reveal");

    const parent = el.parentElement;

    const count = delayCounters.get(parent) || 0;

    delayCounters.set(parent, count + 1);

    el.style.transitionDelay = Math.min(count * 0.08, 0.48) + "s";

  });



  if (!("IntersectionObserver" in window)) {

    // Fallback: just show everything immediately

    els.forEach((el) => el.classList.add("in-view"));

    return;

  }



  const io = new IntersectionObserver((entries) => {

    entries.forEach((entry) => {

      if (entry.isIntersecting) {

        entry.target.classList.add("in-view");

        io.unobserve(entry.target);

      }

    });

  }, { threshold: 0.15, rootMargin: "0px 0px -60px 0px" });



  els.forEach((el) => io.observe(el));

});

document.addEventListener("DOMContentLoaded", () => {



  const currentPage = window.location.pathname.split("/").pop() || "index.html";



  document.querySelectorAll(".navbar a").forEach(link => {



    const linkPage = link.getAttribute("href").split("/").pop();



    if (linkPage === currentPage) {

      link.classList.add("active");

    }



  });



});

document.addEventListener("DOMContentLoaded", () => {



  const params = new URLSearchParams(window.location.search);

  const field = params.get("field");



  if (!field) return;



  const tile = document.querySelector(

    `.job-cat-tile[data-field="${field}"]`

  );



  if (tile) {



    // Scroll

    tile.scrollIntoView({

      behavior: "smooth",

      block: "center"

    });



    // Highlight

    tile.classList.add("active");



    // Agar click event bana hua hai

    setTimeout(() => {

      tile.click();

    }, 300);

  }



});

/* =========================================================

   NEW: JOB APPLICATION MODAL (reusable)

   Same code structure as the rest of this file

   (DOMContentLoaded + getElementById/querySelectorAll pattern).



   Opens the SAME modal (#jobApplyOverlay) for TWO different

   triggers, without duplicating any modal-control logic:

     1) "Apply Internship" buttons  -> class="js-internship-popup"

     2) "Apply Now" buttons on job cards -> class="apply-btn"



   Does NOT touch the existing #applyModalOverlay logic above —

   that modal keeps working exactly as before.

========================================================= */

document.addEventListener("DOMContentLoaded", () => {



  const jobOverlay = document.getElementById("jobApplyOverlay");

  const jobClose = document.getElementById("jobApplyClose");

  const jobForm = document.getElementById("jobApplyForm");

  const jobTitleInput = document.getElementById("jobApplyTitleInput");

  const coverLetter = document.getElementById("jobApplyCoverLetter");

  const charCount = document.getElementById("jobApplyCharCount");

  const jobResumeFile = document.getElementById("jobApplyResumeFile");

  const jobDropzone = document.getElementById("jobApplyDropzone");

  const jobPreview = document.getElementById("jobApplyFilePreview");

  const jobFileName = document.getElementById("jobApplyFileName");

  const jobFileSize = document.getElementById("jobApplyFileSize");

  const jobFileRemove = document.getElementById("jobApplyFileRemove");



  if (!jobOverlay) return; // safety check — modal not present on this page



  // ---- Reusable auth check helper ----

  async function checkCandidateAuth() {

    if (typeof window.IS_CANDIDATE_LOGGED_IN !== 'undefined') {

      if (!window.IS_CANDIDATE_LOGGED_IN) {

        promptLogin();

        return false;

      }

      return true;

    }

    const apiBase = window.location.origin;

    try {

      const res = await fetch(`${apiBase}/api/candidate/me/`, { credentials: "include" });

      if (res.ok) {

        const data = await res.json();

        if (data.status === "success" && data.candidate) {

          return true;

        }

      }

    } catch (e) {}



    promptLogin();

    return false;

  }



  function promptLogin() {

    const apiBase = window.location.origin;

    if (confirm("Job apply karne ke liye please Candidate Register ya Login karein.\n\nKya aap Candidate Login page par jana chahte hain?")) {

      window.location.href = `${apiBase}/candidate/login/?next=` + encodeURIComponent(window.location.pathname);

    }

  }



  // ---- Reusable open/close helpers (avoids duplicating logic per button) ----

  async function openJobModal(jobTitle, jobId) {

    const isAuthed = await checkCandidateAuth();

    if (!isAuthed) return;

    if (jobTitleInput) jobTitleInput.value = jobTitle || "";

    const jobIdInput = document.getElementById("jobApplyIdInput");

    if (jobIdInput) jobIdInput.value = jobId || "";



    // Auto-fill applicant info if candidate is currently logged in

    try {

      const apiBase = window.location.origin;

      fetch(`${apiBase}/api/candidate/me/`, { credentials: "include" })

        .then(r => r.json())

        .then(data => {

          if (data && data.candidate && jobForm) {

            const c = data.candidate;

            const nameInput = jobForm.querySelector("input[name='full_name']");

            const emailInput = jobForm.querySelector("input[name='email']");

            const phoneInput = jobForm.querySelector("input[name='phone']");

            const cityInput = jobForm.querySelector("input[name='city']");

            if (nameInput && !nameInput.value) nameInput.value = c.name || "";

            if (emailInput && !emailInput.value) emailInput.value = c.email || "";

            if (phoneInput && !phoneInput.value) phoneInput.value = c.phone || "";

            if (cityInput && !cityInput.value) cityInput.value = c.city || "";

          }

        }).catch(() => {});

    } catch(e) {}



    jobOverlay.classList.add("active");

    document.body.classList.add("popup-open");

  }



  function closeJobModal() {

    jobOverlay.classList.remove("active");

    document.body.classList.remove("popup-open");

  }



  // 1) "Apply Internship" buttons — open dedicated Internship Modal (#internshipApplyOverlay)

  const internOverlay = document.getElementById("internshipApplyOverlay");

  const internClose = document.getElementById("internshipApplyClose");

  const internForm = document.getElementById("internshipApplyForm");

  const internIdInput = document.getElementById("internshipApplyIdInput");

  const internDomainSelect = document.getElementById("internshipApplyDomainSelect");

  const internMessage = document.getElementById("internshipApplyMessage");

  const internCharCount = document.getElementById("internshipApplyCharCount");

  const internResumeFile = document.getElementById("internshipApplyResumeFile");

  const internDropzone = document.getElementById("internshipApplyDropzone");

  const internPreview = document.getElementById("internshipApplyFilePreview");

  const internFileName = document.getElementById("internshipApplyFileName");

  const internFileSize = document.getElementById("internshipApplyFileSize");

  const internFileRemove = document.getElementById("internshipApplyFileRemove");



  function openInternshipModal(internshipId, domainTitle) {

    if (!internOverlay) return;

    if (internIdInput) internIdInput.value = internshipId || "";



    // Set Domain selection if passed

    if (domainTitle && internDomainSelect) {

      const trimmed = domainTitle.trim();

      let matched = false;

      for (let opt of internDomainSelect.options) {

        if (opt.value.toLowerCase().includes(trimmed.toLowerCase()) || trimmed.toLowerCase().includes(opt.value.toLowerCase())) {

          internDomainSelect.value = opt.value;

          matched = true;

          break;

        }

      }

      if (!matched && trimmed && trimmed !== 'Internship') {

        const opt = new Option(trimmed, trimmed, true, true);

        internDomainSelect.add(opt);

      }

    }



    // Auto-fill applicant info if candidate is currently logged in

    try {

      const apiBase = window.location.origin;

      fetch(`${apiBase}/api/candidate/me/`, { credentials: "include" })

        .then(r => r.json())

        .then(data => {

          if (data && data.candidate && internForm) {

            const c = data.candidate;

            const nameInput = internForm.querySelector("input[name='full_name']");

            const emailInput = internForm.querySelector("input[name='email']");

            const phoneInput = internForm.querySelector("input[name='phone']");

            const collegeInput = internForm.querySelector("input[name='college']");

            if (nameInput && !nameInput.value) nameInput.value = c.full_name || c.name || "";

            if (emailInput && !emailInput.value) emailInput.value = c.email || "";

            if (phoneInput && !phoneInput.value) phoneInput.value = c.phone || "";

            if (collegeInput && !collegeInput.value) collegeInput.value = c.college || c.qualification || "";

          }

        }).catch(() => {});

    } catch(e) {}



    internOverlay.classList.add("active");

    document.body.classList.add("popup-open");

  }



  function closeInternshipModal() {

    if (!internOverlay) return;

    internOverlay.classList.remove("active");

    document.body.classList.remove("popup-open");

  }



  document.addEventListener("click", (e) => {

    const btn = e.target.closest(".js-internship-popup");

    if (btn) {

      e.preventDefault();

      const internshipId = btn.getAttribute("data-internship-id") || "";

      const domain = btn.getAttribute("data-internship-domain") || btn.getAttribute("data-job-title") || "";

      openInternshipModal(internshipId, domain);

    }

  });



  if (internClose) internClose.addEventListener("click", closeInternshipModal);

  if (internOverlay) {

    internOverlay.addEventListener("click", (e) => {

      if (e.target === internOverlay) closeInternshipModal();

    });

  }



  document.addEventListener("keydown", (e) => {

    if (e.key === "Escape" && internOverlay && internOverlay.classList.contains("active")) {

      closeInternshipModal();

    }

  });



  if (internMessage && internCharCount) {

    internMessage.addEventListener("input", () => {

      internCharCount.textContent = internMessage.value.length;

    });

  }



  if (internDropzone && internResumeFile) {

    internDropzone.addEventListener("click", () => {

      internResumeFile.click();

    });



    ["dragenter", "dragover"].forEach((evtName) => {

      internDropzone.addEventListener(evtName, (e) => {

        e.preventDefault();

        e.stopPropagation();

        internDropzone.classList.add("drag-over");

      });

    });



    ["dragleave", "drop"].forEach((evtName) => {

      internDropzone.addEventListener(evtName, (e) => {

        e.preventDefault();

        e.stopPropagation();

        internDropzone.classList.remove("drag-over");

      });

    });



    internDropzone.addEventListener("drop", (e) => {

      if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {

        internResumeFile.files = e.dataTransfer.files;

        internResumeFile.dispatchEvent(new Event("change"));

      }

    });

  }



  if (internResumeFile) {

    internResumeFile.addEventListener("change", () => {

      const file = internResumeFile.files[0];

      if (file) {

        if (file.size > 5 * 1024 * 1024) {

          alert("Resume file size must not exceed 5 MB.");

          internResumeFile.value = "";

          if (internPreview) internPreview.style.display = "none";

          if (internDropzone) internDropzone.style.display = "flex";

          return;

        }

        if (internFileName) internFileName.textContent = file.name;

        if (internFileSize) internFileSize.textContent = (file.size / 1024).toFixed(1) + " KB";

        if (internPreview) internPreview.style.display = "flex";

        if (internDropzone) internDropzone.style.display = "none";

      }

    });

  }



  if (internFileRemove) {

    internFileRemove.addEventListener("click", () => {

      if (internResumeFile) internResumeFile.value = "";

      if (internPreview) internPreview.style.display = "none";

      if (internDropzone) internDropzone.style.display = "flex";

    });

  }



  if (internForm) {

    internForm.addEventListener("submit", async (e) => {

      e.preventDefault();



      if (internResumeFile && internResumeFile.files.length > 0) {

        const file = internResumeFile.files[0];

        if (file.size > 5 * 1024 * 1024) {

          alert("Resume file size must not exceed 5 MB.");

          return;

        }

      }



      const submitBtn = internForm.querySelector("button[type='submit']");

      if (submitBtn) { submitBtn.disabled = true; submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...'; }



      const formData = new FormData(internForm);



      try {

        const response = await fetch("/api/internship-apply/", {

          method: "POST",

          headers: {

            "X-CSRFToken": getCookie("csrftoken") || ""

          },

          body: formData

        });

        const result = await response.json();



        if (response.ok && (result.status === "success" || result.success)) {

          alert(result.message || "✓ Your internship application has been submitted successfully!");

          internForm.reset();

          if (internPreview) internPreview.style.display = "none";

          if (internDropzone) internDropzone.style.display = "flex";

          closeInternshipModal();

        } else {

          alert(result.message || "Error submitting internship application.");

        }

      } catch (err) {

        alert("Network error while submitting internship application.");

      } finally {

        if (submitBtn) { submitBtn.disabled = false; submitBtn.innerHTML = '<i class="fa-solid fa-paper-plane"></i> Submit Internship Application'; }

      }

    });

  }



  // 2) "Apply Now" buttons on job cards — auto-fill job title from the card (using event delegation)

  document.addEventListener("click", (e) => {

    const btn = e.target.closest(".apply-btn, .open-job-modal-btn");

    if (btn) {

      e.preventDefault();

      const card = btn.closest(".job-card, .jc-icon-card");

      const titleAttr = btn.getAttribute("data-job-title");

      const jobId = btn.getAttribute("data-job-id") || (card ? card.getAttribute("data-job-id") : "");

      const cardTitle = card ? (card.querySelector("h3, h4") ? card.querySelector("h3, h4").textContent.trim() : "") : "";

      openJobModal(titleAttr || cardTitle || "Job Opening", jobId);

    }

  });



  // Close via the × button

  if (jobClose) {

    jobClose.addEventListener("click", closeJobModal);

  }



  // Close by clicking outside the modal box (on the dark overlay itself)

  jobOverlay.addEventListener("click", (e) => {

    if (e.target === jobOverlay) closeJobModal();

  });



  // Close on Escape key, for keyboard users

  document.addEventListener("keydown", (e) => {

    if (e.key === "Escape" && jobOverlay.classList.contains("active")) {

      closeJobModal();

    }

  });



  // Live character counter for the optional cover letter field

  if (coverLetter && charCount) {

    coverLetter.addEventListener("input", () => {

      charCount.textContent = coverLetter.value.length;

    });

  }



  // Resume upload handling for Job Apply Modal

  function resetJobResumeUI() {

    if (jobResumeFile) jobResumeFile.value = "";

    if (jobPreview) jobPreview.style.display = "none";

    if (jobDropzone) {

      jobDropzone.style.display = "flex";

      jobDropzone.classList.remove("drag-over");

    }

  }



  if (jobDropzone && jobResumeFile) {

    jobDropzone.dataset.uploadInitialized = "true";



    jobDropzone.addEventListener("click", (e) => {

      if (e.target !== jobResumeFile) {

        jobResumeFile.click();

      }

    });



    jobDropzone.addEventListener("keydown", (e) => {

      if (e.key === "Enter" || e.key === " ") {

        e.preventDefault();

        jobResumeFile.click();

      }

    });



    ["dragenter", "dragover"].forEach((evtName) => {

      jobDropzone.addEventListener(evtName, (e) => {

        e.preventDefault();

        e.stopPropagation();

        jobDropzone.classList.add("drag-over");

      });

    });



    ["dragleave", "drop"].forEach((evtName) => {

      jobDropzone.addEventListener(evtName, (e) => {

        e.preventDefault();

        e.stopPropagation();

        jobDropzone.classList.remove("drag-over");

      });

    });



    jobDropzone.addEventListener("drop", (e) => {

      if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {

        jobResumeFile.files = e.dataTransfer.files;

        jobResumeFile.dispatchEvent(new Event("change"));

      }

    });

  }



  if (jobResumeFile) {

    jobResumeFile.dataset.uploadInitialized = "true";



    jobResumeFile.addEventListener("change", () => {

      const file = jobResumeFile.files && jobResumeFile.files[0];

      if (file) {

        const ext = file.name.split('.').pop().toLowerCase();

        if (!['pdf', 'doc', 'docx'].includes(ext)) {

          alert("Please upload a valid resume file (PDF, DOC, DOCX).");

          resetJobResumeUI();

          return;

        }



        if (file.size > 10 * 1024 * 1024) {

          alert("Resume file size must not exceed 10 MB.");

          resetJobResumeUI();

          return;

        }



        if (jobFileName) jobFileName.textContent = file.name;

        if (jobFileSize) {

          jobFileSize.textContent = file.size < 1024 * 1024

            ? (file.size / 1024).toFixed(1) + " KB"

            : (file.size / (1024 * 1024)).toFixed(1) + " MB";

        }

        if (jobPreview) jobPreview.style.display = "flex";

        if (jobDropzone) jobDropzone.style.display = "none";

      }

    });

  }



  if (jobFileRemove) {

    jobFileRemove.addEventListener("click", (e) => {

      e.stopPropagation();

      resetJobResumeUI();

    });

  }



  // #jobApplyForm AJAX Submit Handler

  if (jobForm) {

    jobForm.addEventListener("reset", () => {

      resetJobResumeUI();

      if (charCount) charCount.textContent = "0";

    });



    jobForm.addEventListener("submit", async (e) => {

      e.preventDefault();

      const submitBtn = jobForm.querySelector("button[type='submit']");

      if (submitBtn) { submitBtn.disabled = true; submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...'; }



      const formData = new FormData(jobForm);



      try {

        const response = await fetch("/api/apply/", {

          method: "POST",

          headers: {

            "X-CSRFToken": getCookie("csrftoken") || ""

          },

          body: formData

        });

        const result = await response.json();



        if (response.ok && result.status === "success") {

          alert(result.message || "✓ Your application has been submitted successfully!");

          jobForm.reset();

          resetJobResumeUI();

          closeJobModal();

        } else if (result.status === "login_required" || response.status === 401) {

          if (confirm(result.message || "Please log in or register a candidate account to apply for jobs. Would you like to log in now?")) {

            window.location.href = result.redirect_url || "/candidate/login/";

          }

        } else {

          alert(result.message || "Error submitting application.");

        }

      } catch (err) {

        alert("Network error while submitting application.");

      } finally {

        if (submitBtn) { submitBtn.disabled = false; submitBtn.innerHTML = 'Submit Application <i class="fas fa-arrow-right"></i>'; }

      }

    });

  }







});

/* =========================================================

   NEW: HIRE TALENT MODAL (3rd popup, reusable)

   Same code structure as the other two modal blocks above

   (DOMContentLoaded + getElementById/querySelectorAll pattern).



   Opens a NEW modal (#hireTalentModalOverlay) — visually it's

   the exact same design as the very first modal because the HTML

   reuses the .apply-modal-* classes, so this file only needs the

   open/close wiring, no styling logic.



   Trigger: "Hire Talent" button in the hero -> class="js-hire-talent-popup"



   Does NOT touch #applyModalOverlay or #jobApplyOverlay logic

   above — both existing popups keep working exactly as before.

========================================================= */

document.addEventListener("DOMContentLoaded", () => {



  const hireOverlay = document.getElementById("hireTalentModalOverlay");

  const hireClose = document.getElementById("hireTalentModalClose");

  const hireForm = document.getElementById("hireTalentForm");

  const hireTriggers = document.querySelectorAll(".js-hire-talent-popup");



  if (!hireOverlay) return; // safety check — modal not present on this page



  // ---- Reusable open/close helpers (same pattern as the job-apply modal) ----

  function openHireModal() {

    hireOverlay.classList.add("active");

    document.body.classList.add("popup-open");

  }



  function closeHireModal() {

    hireOverlay.classList.remove("active");

    document.body.classList.remove("popup-open");

  }



  // Open the modal from the "Hire Talent" button(s)

  hireTriggers.forEach((btn) => {

    btn.addEventListener("click", (e) => {

      e.preventDefault();

      openHireModal();

    });

  });



  // Close via the × button

  if (hireClose) {

    hireClose.addEventListener("click", closeHireModal);

  }



  // Close by clicking outside the modal box (on the dark overlay itself)

  hireOverlay.addEventListener("click", (e) => {

    if (e.target === hireOverlay) closeHireModal();

  });



  // #hireTalentForm AJAX Submit Handler

  if (hireForm) {

    hireForm.addEventListener("submit", async (e) => {

      e.preventDefault();

      const submitBtn = hireForm.querySelector("button[type='submit']");

      if (submitBtn) { submitBtn.disabled = true; submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...'; }



      const formData = new FormData(hireForm);

      const dataObj = {};

      formData.forEach((val, key) => { dataObj[key] = val; });



      try {

        const response = await fetch("/api/company-enquiry/", {

          method: "POST",

          headers: { 

            "Content-Type": "application/json",

            "X-CSRFToken": getCookie("csrftoken") || ""

          },

          body: JSON.stringify(dataObj)

        });

        const result = await response.json();



        if (response.ok && result.status === "success") {

          alert(result.message || "✓ Thank you! Your hiring requirement has been submitted. Our team will contact you shortly.");

          hireForm.reset();

          closeHireModal();

        } else {

          alert(result.message || "Error submitting hiring requirement.");

        }

      } catch (err) {

        alert("Network error. Please try again later.");

      } finally {

        if (submitBtn) { submitBtn.disabled = false; submitBtn.innerHTML = 'Submit Hiring Requirement <i class="fas fa-arrow-right"></i>'; }

      }

    });

  }







});

/* =========================================================================

   CLIENT TESTIMONIALS & SUCCESS STORIES — behavior

   Vanilla JS. No dependencies. Include after the DOM (defer, or bottom of body).

========================================================================= */

(function () {

  "use strict";



  /* ---------------------------------------------------------------------

     1) SCROLL REVEAL (fade-up)

  --------------------------------------------------------------------- */

  function initReveal() {

    var items = document.querySelectorAll(".testimonials-section [data-reveal]");

    if (!("IntersectionObserver" in window) || !items.length) {

      items.forEach(function (el) { el.classList.add("in-view"); });

      return;

    }

    var io = new IntersectionObserver(function (entries) {

      entries.forEach(function (entry) {

        if (entry.isIntersecting) {

          entry.target.classList.add("in-view");

          io.unobserve(entry.target);

        }

      });

    }, { threshold: 0.05, rootMargin: "0px 0px 50px 0px" });

    items.forEach(function (el) { io.observe(el); });



    // Fallback timer: ensure all are revealed even if observer doesn't trigger

    setTimeout(function () {

      items.forEach(function (el) { el.classList.add("in-view"); });

    }, 1200);

  }



  /* ---------------------------------------------------------------------

     2) ANIMATED COUNTERS

  --------------------------------------------------------------------- */

  function initCounters() {

    var counters = document.querySelectorAll(".testimonials-section [data-count]");

    if (!counters.length) return;



    function animate(el) {

      var target = parseFloat(el.getAttribute("data-count"));

      var suffix = el.getAttribute("data-suffix") || "";

      var duration = 1600;

      var start = null;



      function step(ts) {

        if (!start) start = ts;

        var progress = Math.min((ts - start) / duration, 1);

        var eased = 1 - Math.pow(1 - progress, 3);

        var value = Math.floor(eased * target);

        el.textContent = value.toLocaleString("en-IN") + suffix;

        if (progress < 1) requestAnimationFrame(step);

        else el.textContent = target.toLocaleString("en-IN") + suffix;

      }

      requestAnimationFrame(step);

    }



    if (!("IntersectionObserver" in window)) {

      counters.forEach(animate);

      return;

    }

    var io = new IntersectionObserver(function (entries) {

      entries.forEach(function (entry) {

        if (entry.isIntersecting) {

          animate(entry.target);

          io.unobserve(entry.target);

        }

      });

    }, { threshold: 0.4 });

    counters.forEach(function (el) { io.observe(el); });

  }



  /* ---------------------------------------------------------------------

     3) INFINITE AUTO-SCROLL CAROUSEL

     - Duplicates the track content so the loop is seamless

     - Auto-scrolls continuously in the given direction

     - Pauses on hover, supports mouse-drag and touch swipe

  --------------------------------------------------------------------- */

  function initMarquee(viewportEl, options) {

    if (!viewportEl) return;

    var track = viewportEl.querySelector(".tt-track");

    if (!track) return;



    var speed = options.speed || 0.6;          // px per frame

    var direction = options.direction === "rtl" ? -1 : 1; // 1 = moves left, -1 = moves right



    // Duplicate cards until track is at least 2x the viewport width for a seamless loop

    var originalHTML = track.innerHTML;

    var viewportWidth = viewportEl.offsetWidth || 1200;

    var guard = 0;

    while (track.scrollWidth < viewportWidth * 2.2 && guard < 6) {

      track.innerHTML += originalHTML;

      guard++;

    }

    // one more full duplicate so the second copy can scroll fully into view before reset

    track.innerHTML += track.innerHTML;



    var loopWidth = track.scrollWidth / 2;

    var pos = 0;

    var paused = false;

    var dragging = false;

    var dragStartX = 0;

    var dragStartPos = 0;

    var lastDragX = 0;

    var dragVelocity = 0;



    function setTransform() {

      track.style.transform = "translate3d(" + (-pos) + "px,0,0)";

    }



    function wrap() {

      if (pos >= loopWidth) pos -= loopWidth;

      if (pos < 0) pos += loopWidth;

    }



    function frame() {

      if (!dragging && !paused) {

        pos += speed * direction;

        wrap();

        setTransform();

      }

      requestAnimationFrame(frame);

    }

    requestAnimationFrame(frame);



    // pause on hover (desktop only — touch handles its own pause via dragging)

    viewportEl.addEventListener("mouseenter", function () { paused = true; });

    viewportEl.addEventListener("mouseleave", function () { paused = false; });



    // pointer drag (mouse + touch unified)

    function pointerDown(clientX) {

      dragging = true;

      dragStartX = clientX;

      lastDragX = clientX;

      dragStartPos = pos;

      dragVelocity = 0;

      viewportEl.classList.add("dragging");

    }

    function pointerMove(clientX) {

      if (!dragging) return;

      var delta = clientX - dragStartX;

      dragVelocity = clientX - lastDragX;

      lastDragX = clientX;

      pos = dragStartPos - delta * direction;

      wrap();

      setTransform();

    }

    function pointerUp() {

      if (!dragging) return;

      dragging = false;

      viewportEl.classList.remove("dragging");

      // small inertia based on last drag velocity

      var inertia = -dragVelocity * direction * 0.4;

      var inertiaFrames = 18;

      var i = 0;

      (function inertiaStep() {

        if (i >= inertiaFrames) return;

        pos += (inertia / inertiaFrames);

        wrap();

        setTransform();

        i++;

        requestAnimationFrame(inertiaStep);

      })();

    }



    // mouse events

    viewportEl.addEventListener("mousedown", function (e) {

      pointerDown(e.clientX);

      e.preventDefault();

    });

    window.addEventListener("mousemove", function (e) {

      if (dragging) pointerMove(e.clientX);

    });

    window.addEventListener("mouseup", pointerUp);



    // touch events

    viewportEl.addEventListener("touchstart", function (e) {

      pointerDown(e.touches[0].clientX);

    }, { passive: true });

    viewportEl.addEventListener("touchmove", function (e) {

      pointerMove(e.touches[0].clientX);

    }, { passive: true });

    viewportEl.addEventListener("touchend", pointerUp);



    // arrow buttons (nudge position)

    var block = viewportEl.closest(".tt-slider-block");

    if (block) {

      var prevBtn = block.querySelector(".tt-arrow-btn.prev");

      var nextBtn = block.querySelector(".tt-arrow-btn.next");

      var nudge = 340;

      if (prevBtn) prevBtn.addEventListener("click", function () {

        pos -= nudge * direction; wrap(); setTransform();

      });

      if (nextBtn) nextBtn.addEventListener("click", function () {

        pos += nudge * direction; wrap(); setTransform();

      });

    }

  }



  /* ---------------------------------------------------------------------

     INIT

  --------------------------------------------------------------------- */

  function init() {

    initReveal();

    initCounters();

    initMarquee(document.getElementById("ttCandidateViewport"), { speed: 0.55, direction: "ltr" });

    initMarquee(document.getElementById("ttEmployerViewport"), { speed: 0.45, direction: "rtl" });

  }



  if (document.readyState === "loading") {

    document.addEventListener("DOMContentLoaded", init);

  } else {

    init();

  }

})();

// Mobile nav toggle

const hamburger = document.getElementById('hamburger');

const navLinks = document.getElementById('navLinks');



if (hamburger && navLinks) {



    hamburger.addEventListener('click', () => {

        navLinks.classList.toggle('open');

    });



    navLinks.querySelectorAll('a').forEach(a => {

        a.addEventListener('click', () => {

            navLinks.classList.remove('open');

        });

    });



}

// Scroll reveal

const revealEls = document.querySelectorAll('.reveal');

const io = new IntersectionObserver((entries) => {

  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });

}, { threshold: .15 });

revealEls.forEach(el => io.observe(el));



// Counter animation

const counters = document.querySelectorAll('.stat-num[data-count]');

const counterIO = new IntersectionObserver((entries) => {

  entries.forEach(entry => {

    if (!entry.isIntersecting) return;

    const el = entry.target;

    const target = parseInt(el.getAttribute('data-count'), 10);

    const suffix = el.getAttribute('data-suffix') || '';

    let current = 0;

    const step = Math.max(1, Math.ceil(target / 60));

    const timer = setInterval(() => {

      current += step;

      if (current >= target) { current = target; clearInterval(timer); }

      el.textContent = current + suffix;

    }, 25);

    counterIO.unobserve(el);

  });

}, { threshold: .5 });

counters.forEach(c => counterIO.observe(c));



// Departments data + marquee build (duplicated for seamless infinite scroll)

const departments = [

  { icon: '👔', name: 'Recruitment', desc: 'End-to-end hiring solutions for permanent and contract roles.', img: 'https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=400&q=80' },

  { icon: '📋', name: 'HR Consulting', desc: 'Strategic HR advisory for policy, process, and workforce planning.', img: 'https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=400&q=80' },

  { icon: '💻', name: 'IT Hiring', desc: 'Specialized tech talent sourcing across engineering and IT roles.', img: 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&q=80' },

  { icon: '📞', name: 'BPO Hiring', desc: 'High-volume staffing for voice and non-voice BPO operations.', img: 'https://images.unsplash.com/photo-1600880292089-90a7e086ee0c?w=400&q=80' },

  { icon: '📊', name: 'Finance & Accounts', desc: 'Skilled finance professionals for accounting and audit functions.', img: 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=400&q=80' },

  { icon: '🏥', name: 'Healthcare Recruitment', desc: 'Connecting hospitals and clinics with qualified healthcare talent.', img: 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=400&q=80' },

  { icon: '📈', name: 'Sales & Marketing', desc: 'Building high-performing sales and marketing teams for growth.', img: 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&q=80' },

  { icon: '🎧', name: 'Customer Support', desc: 'Reliable support staffing to keep client experience seamless.', img: 'https://images.unsplash.com/photo-1553877522-43269d4ea984?w=400&q=80' },

  { icon: '🎓', name: 'Training & Development', desc: 'Upskilling programs that prepare candidates for the workplace.', img: 'https://images.unsplash.com/photo-1543269865-cbf427effbad?w=400&q=80' },

  { icon: '🧭', name: 'Career Counseling', desc: 'Personalized guidance to help candidates find the right path.', img: 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=400&q=80' }

];



const track = document.getElementById('marqueeTrack');



if (track && !track.children.length) {

  const buildCards = () => departments.map(d => `

    <div class="dept-card">

      <div class="dept-img">

        <img src="${d.img}" alt="${d.name} department at Sky Vision">

        <div class="dept-icon-badge">${d.icon}</div>

      </div>

      <div class="dept-body">

        <h4>${d.name}</h4>

        <p>${d.desc}</p>

      </div>

    </div>`).join('');

  track.innerHTML = buildCards() + buildCards();

}





console.log("JavaScript Connected Successfully");



document.addEventListener("DOMContentLoaded", () => {



  /* =========================================================

     SCROLL REVEAL — Our Journey timeline, stats, values, CTA

  ========================================================= */

  const selectors = [

    ".section-title",

    ".tl-card",

    ".tl-node",

    ".stat",

    ".value-card",

    ".cta"

  ];



  const els = document.querySelectorAll(selectors.join(","));

  if (!els.length) return;



  // Stagger elements that share the same parent, so grids/rows

  // animate one after another instead of all at once.

  const delayCounters = new WeakMap();



  els.forEach((el) => {

    el.classList.add("reveal");

    const parent = el.parentElement;

    const count = delayCounters.get(parent) || 0;

    delayCounters.set(parent, count + 1);

    el.style.transitionDelay = Math.min(count * 0.08, 0.48) + "s";

  });



  if (!("IntersectionObserver" in window)) {

    // Fallback: just show everything immediately

    els.forEach((el) => el.classList.add("in-view"));

    return;

  }



  const io = new IntersectionObserver((entries) => {

    entries.forEach((entry) => {

      if (entry.isIntersecting) {

        entry.target.classList.add("in-view");

        io.unobserve(entry.target);

      }

    });

  }, { threshold: 0.15, rootMargin: "0px 0px -60px 0px" });



  els.forEach((el) => io.observe(el));



});

/* =========================================================

   FLOATING CONTACT BUTTONS — click feedback + touch tooltip

========================================================= */

document.addEventListener("DOMContentLoaded", () => {



  const fcb = document.getElementById("floatingContactButtons");

  if (!fcb) return; // safety check — not present on this page



  const buttons = fcb.querySelectorAll(".fcb-btn");



  buttons.forEach((btn) => {



    // brief "pressed" animation on click/tap

    btn.addEventListener("click", () => {

      btn.classList.add("fcb-clicked");

      setTimeout(() => btn.classList.remove("fcb-clicked"), 250);

    });



    // on touch devices there's no hover, so tapping briefly reveals the tooltip

    btn.addEventListener("touchstart", () => {

      buttons.forEach((b) => b.classList.remove("fcb-show-tip"));

      btn.classList.add("fcb-show-tip");

      setTimeout(() => btn.classList.remove("fcb-show-tip"), 1500);

    }, { passive: true });



  });



});

/* =========================================================

   RESUME UPLOAD MODAL — standalone, self-contained script.

   Does NOT modify or reuse any logic from script.js.

   All ids/classes are unique (rm- / resume-modal- prefixed).

========================================================= */

document.addEventListener("DOMContentLoaded", () => {



  const trigger   = document.getElementById("resumeUploadTrigger");

  const overlay   = document.getElementById("resumeModalOverlay");

  if (!overlay) return; // safety check — overlay must be present on page



  const modalBox   = overlay.querySelector(".resume-modal");

  const closeBtn   = document.getElementById("resumeModalClose");

  const cancelBtn  = document.getElementById("resumeModalCancel");

  const form       = document.getElementById("resumeModalForm");

  const successBox = document.getElementById("resumeModalSuccess");

  const okBtn      = document.getElementById("resumeModalOk");



  const fileInput    = document.getElementById("rmResumeFile");

  const uploadArea   = document.getElementById("rmUploadArea");

  const fileNameBox  = document.getElementById("rmFileNameBox");

  const fileNameText = document.getElementById("rmFileNameText");

  const removeFileBtn = document.getElementById("rmRemoveFile");



  let lastFocusedEl = null;

  const MAX_FILE_MB = 5;

  const ALLOWED_EXT = [".pdf", ".doc", ".docx"];



  /* ---------------- Open / Close ---------------- */



  function getFocusable() {

    return modalBox ? modalBox.querySelectorAll(

      'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'

    ) : [];

  }



  function openModal() {

    lastFocusedEl = document.activeElement;

    overlay.classList.add("is-open");

    overlay.setAttribute("aria-hidden", "false");

    document.body.classList.add("resume-modal-open");



    resetToFormView();



    const focusables = getFocusable();

    if (focusables.length) focusables[0].focus();



    document.addEventListener("keydown", onKeydown);

  }



  function closeModal() {

    overlay.classList.remove("is-open");

    overlay.setAttribute("aria-hidden", "true");

    document.body.classList.remove("resume-modal-open");

    document.removeEventListener("keydown", onKeydown);

    if (lastFocusedEl) lastFocusedEl.focus();

  }



  function onKeydown(e) {

    if (e.key === "Escape") {

      closeModal();

      return;

    }

    if (e.key === "Tab") {

      const focusables = Array.from(getFocusable());

      if (!focusables.length) return;

      const first = focusables[0];

      const last = focusables[focusables.length - 1];



      if (e.shiftKey && document.activeElement === first) {

        e.preventDefault();

        last.focus();

      } else if (!e.shiftKey && document.activeElement === last) {

        e.preventDefault();

        first.focus();

      }

    }

  }



  if (trigger) {

    trigger.addEventListener("click", (e) => {

      e.preventDefault();

      openModal();

    });

  }



  document.querySelectorAll(".js-resume-trigger, [data-open-modal='resume']").forEach((btn) => {

    btn.addEventListener("click", (e) => {

      e.preventDefault();

      openModal();

    });

  });



  if (closeBtn) closeBtn.addEventListener("click", closeModal);

  if (cancelBtn) cancelBtn.addEventListener("click", (e) => { e.preventDefault(); closeModal(); });



  overlay.addEventListener("click", (e) => {

    if (e.target === overlay) closeModal();

  });



  if (okBtn) {

    okBtn.addEventListener("click", () => {

      closeModal();

    });

  }



  /* ---------------- Field error helpers ---------------- */



  function setError(fieldWrap, errorEl, message) {

    fieldWrap.classList.add("has-error");

    if (errorEl) {

      errorEl.textContent = message;

      errorEl.classList.add("show");

    }

  }



  function clearError(fieldWrap, errorEl) {

    fieldWrap.classList.remove("has-error");

    if (errorEl) {

      errorEl.textContent = "";

      errorEl.classList.remove("show");

    }

  }



  function validateRequiredText(input, wrap, errorEl, message) {

    const value = input.value.trim();

    if (!value) {

      setError(wrap, errorEl, message);

      return false;

    }

    clearError(wrap, errorEl);

    return true;

  }



  function validateMobile(input, wrap, errorEl) {

    const value = input.value.trim();

    const digitsOnly = /^[0-9]{10}$/;

    if (!value) {

      setError(wrap, errorEl, "Mobile number is required.");

      return false;

    }

    if (!digitsOnly.test(value)) {

      setError(wrap, errorEl, "Enter a valid 10-digit mobile number.");

      return false;

    }

    clearError(wrap, errorEl);

    return true;

  }



  function validateEmail(input, wrap, errorEl) {

    const value = input.value.trim();

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!value) {

      setError(wrap, errorEl, "Email address is required.");

      return false;

    }

    if (!emailPattern.test(value)) {

      setError(wrap, errorEl, "Enter a valid email address.");

      return false;

    }

    clearError(wrap, errorEl);

    return true;

  }



  function validateFile() {

    const wrap = uploadArea;

    const errorEl = document.getElementById("rmFileError");



    if (!fileInput.files || !fileInput.files.length) {

      setError(wrap, errorEl, "Please upload your resume (PDF, DOC or DOCX).");

      return false;

    }



    const file = fileInput.files[0];

    const nameLower = file.name.toLowerCase();

    const hasValidExt = ALLOWED_EXT.some((ext) => nameLower.endsWith(ext));



    if (!hasValidExt) {

      setError(wrap, errorEl, "Only PDF, DOC or DOCX files are accepted.");

      return false;

    }



    const maxBytes = MAX_FILE_MB * 1024 * 1024;

    if (file.size > maxBytes) {

      setError(wrap, errorEl, `File size must be under ${MAX_FILE_MB}MB.`);

      return false;

    }



    clearError(wrap, errorEl);

    return true;

  }



  /* ---------------- Live-clear on input ---------------- */



  form.querySelectorAll("input, select, textarea").forEach((el) => {

    el.addEventListener("input", () => {

      const wrap = el.closest(".resume-modal-input-wrap, .resume-modal-textarea-wrap");

      const errorEl = wrap ? wrap.parentElement.querySelector(".resume-modal-error") : null;

      if (wrap) clearError(wrap, errorEl);

    });

  });



  /* ---------------- Upload area: drag & drop + click ---------------- */



  function updateFileNameDisplay() {

    if (fileInput.files && fileInput.files.length) {

      fileNameText.textContent = fileInput.files[0].name;

      fileNameBox.classList.add("show");

    } else {

      fileNameText.textContent = "";

      fileNameBox.classList.remove("show");

    }

  }



  fileInput.addEventListener("change", () => {

    updateFileNameDisplay();

    validateFile();

  });



  if (removeFileBtn) {

    removeFileBtn.addEventListener("click", (e) => {

      e.stopPropagation();

      fileInput.value = "";

      updateFileNameDisplay();

    });

  }



  ["dragenter", "dragover"].forEach((evtName) => {

    uploadArea.addEventListener(evtName, (e) => {

      e.preventDefault();

      e.stopPropagation();

      uploadArea.classList.add("is-dragover");

    });

  });



  ["dragleave", "drop"].forEach((evtName) => {

    uploadArea.addEventListener(evtName, (e) => {

      e.preventDefault();

      e.stopPropagation();

      uploadArea.classList.remove("is-dragover");

    });

  });



  uploadArea.addEventListener("drop", (e) => {

    const dt = e.dataTransfer;

    if (dt && dt.files && dt.files.length) {

      fileInput.files = dt.files;

      updateFileNameDisplay();

      validateFile();

    }

  });



  /* ---------------- Submit ---------------- */



  function resetToFormView() {

    form.style.display = "flex";

    successBox.classList.remove("show");

  }



  function showSuccessView() {

    form.style.display = "none";

    successBox.classList.add("show");

    const focusTarget = okBtn || successBox;

    if (focusTarget) focusTarget.focus();

  }



  form.addEventListener("submit", (e) => {

    e.preventDefault();



    const fullName   = document.getElementById("rmFullName");

    const mobile     = document.getElementById("rmMobile");

    const email      = document.getElementById("rmEmail");



    const fullNameWrap = fullName.closest(".resume-modal-input-wrap");

    const mobileWrap   = mobile.closest(".resume-modal-input-wrap");

    const emailWrap    = email.closest(".resume-modal-input-wrap");



    const fullNameError = fullNameWrap.parentElement.querySelector(".resume-modal-error");

    const mobileError   = mobileWrap.parentElement.querySelector(".resume-modal-error");

    const emailError    = emailWrap.parentElement.querySelector(".resume-modal-error");



    const isNameValid   = validateRequiredText(fullName, fullNameWrap, fullNameError, "Full name is required.");

    const isMobileValid = validateMobile(mobile, mobileWrap, mobileError);

    const isEmailValid  = validateEmail(email, emailWrap, emailError);

    const isFileValid   = validateFile();



    if (!isNameValid || !isMobileValid || !isEmailValid || !isFileValid) {

      const firstInvalid = form.querySelector(".has-error");

      if (firstInvalid) {

        const focusEl = firstInvalid.querySelector("input, select") || firstInvalid;

        focusEl.focus();

      }

      return;

    }



    const apiBase = "";

    const formData = new FormData();

    formData.append("full_name", fullName.value.trim());

    formData.append("mobile", mobile.value.trim());

    formData.append("email", email.value.trim());

    formData.append("city", document.getElementById("rmCity")?.value?.trim() || "");

    formData.append("qualification", document.getElementById("rmQualification")?.value?.trim() || "");

    formData.append("experience", document.getElementById("rmExperience")?.value || "");

    formData.append("applying_for", document.getElementById("rmApplyingFor")?.value?.trim() || "");

    formData.append("message", document.getElementById("rmMessage")?.value?.trim() || "");



    const resumeFile = fileInput.files[0];

    if (resumeFile) {

      formData.append("resume", resumeFile);

    }



    fetch(`${apiBase}/api/upload-resume`, {

      method: "POST",

      headers: {

        "X-CSRFToken": getCookie("csrftoken") || ""

      },

      body: formData

    })

    .then(r => r.json())

    .then(res => {

      if (res.status === "success") {

        showSuccessView();

        form.reset();

        updateFileNameDisplay();

      } else {

        alert("❌ " + (res.message || "Upload failed."));

      }

    })

    .catch(err => {

      console.error("Upload error:", err);

      alert("Server Error! Please ensure the backend is running.");

    });

  });



  /* =========================================================

     GLOBAL SHARE & SAVE JOB FUNCTIONALITY & TOASTS

  ========================================================= */



  function showSvgToast(message, type = 'info') {

    let container = document.querySelector('.svg-toast-container');

    if (!container) {

      container = document.createElement('div');

      container.className = 'svg-toast-container';

      document.body.appendChild(container);

    }

    

    const toast = document.createElement('div');

    toast.className = `svg-toast svg-toast-${type}`;

    const iconClass = type === 'success' ? 'fa-circle-check' : 'fa-circle-info';

    toast.innerHTML = `<i class="fa-solid ${iconClass}"></i> <span>${message}</span>`;

    

    container.appendChild(toast);

    

    setTimeout(() => {

      toast.classList.add('show');

    }, 10);

    

    setTimeout(() => {

      toast.classList.remove('show');

      setTimeout(() => {

        toast.remove();

      }, 300);

    }, 3500);

  }



  function getLocalSavedJobs() {

    try {

      return JSON.parse(localStorage.getItem('svg_saved_jobs') || '[]');

    } catch(e) {

      return [];

    }

  }



  function setLocalSavedJobs(jobsArr) {

    try {

      localStorage.setItem('svg_saved_jobs', JSON.stringify(jobsArr));

    } catch(e) {}

  }



  function syncSavedJobButtonsState() {

    const savedJobs = getLocalSavedJobs();

    document.querySelectorAll('.js-save-job-btn').forEach(btn => {

      const title = btn.getAttribute('data-job-title') || '';

      const id = btn.getAttribute('data-job-id') || '';

      const key = id ? `id_${id}` : title;

      

      if (savedJobs.includes(key) || (id && savedJobs.includes(`id_${id}`)) || (title && savedJobs.includes(title))) {

        btn.classList.add('active', 'saved');

        const icon = btn.querySelector('i');

        if (icon) {

          icon.className = 'fa-solid fa-bookmark';

        }

      } else {

        btn.classList.remove('active', 'saved');

        const icon = btn.querySelector('i');

        if (icon) {

          icon.className = 'fa-regular fa-bookmark';

        }

      }

    });

  }



  window.ensureJobCardActionButtons = function() {

    const cardSelectors = '.job-card, .jc-detail-card, .jc-icon-card, .latest-job-card, [class*="job-card"], [class*="jc-card"], [class*="job-item"]';

    document.querySelectorAll(cardSelectors).forEach(card => {

      let footer = card.querySelector('.job-footer, .jc-detail-footer, .card-footer');

      const applyBtn = card.querySelector('.apply-btn, .jc-detail-apply, .open-job-modal-btn, a.op-apply, a[href*="apply"]');

      

      // If no footer container found, use parent of applyBtn or card itself

      const container = footer || (applyBtn ? applyBtn.parentElement : card);

      

      if (container && !container.querySelector('.job-actions-btns') && !card.querySelector('.job-actions-btns')) {

        const jobTitle = card.querySelector('h3, h4, .job-title')?.textContent?.trim() || 'Job Opening';

        const jobId = card.dataset.jobId || card.getAttribute('data-job-id') || '';

        

        const btnsDiv = document.createElement('div');

        btnsDiv.className = 'job-actions-btns';

        btnsDiv.innerHTML = `

          <button type="button" class="job-action-btn js-share-job-btn" data-job-title="${jobTitle}" data-job-id="${jobId}" title="Share Job">

            <i class="fa-solid fa-share-nodes"></i>

          </button>

          <button type="button" class="job-action-btn js-save-job-btn" data-job-title="${jobTitle}" data-job-id="${jobId}" title="Save Job">

            <i class="fa-regular fa-bookmark"></i>

          </button>

        `;

        

        if (applyBtn && applyBtn.parentNode) {

          applyBtn.parentNode.insertBefore(btnsDiv, applyBtn);

        } else {

          container.appendChild(btnsDiv);

        }

      }

    });

    syncSavedJobButtonsState();

  };



  ensureJobCardActionButtons();

  setTimeout(ensureJobCardActionButtons, 300);

  setTimeout(ensureJobCardActionButtons, 1000);

  setTimeout(ensureJobCardActionButtons, 2500);



  // MutationObserver to catch dynamically rendered cards instantly

  try {

    const observer = new MutationObserver((mutations) => {

      let shouldRun = false;

      for (const m of mutations) {

        if (m.addedNodes.length > 0) {

          shouldRun = true;

          break;

        }

      }

      if (shouldRun) {

        ensureJobCardActionButtons();

      }

    });

    observer.observe(document.body, { childList: true, subtree: true });

  } catch(e) {}



  function copyToClipboard(text, successMsg) {

    if (navigator.clipboard && window.isSecureContext) {

      navigator.clipboard.writeText(text).then(() => {

        showSvgToast(successMsg, 'success');

      }).catch(() => {

        fallbackCopyText(text, successMsg);

      });

    } else {

      fallbackCopyText(text, successMsg);

    }

  }



  function fallbackCopyText(text, successMsg) {

    const textArea = document.createElement("textarea");

    textArea.value = text;

    textArea.style.position = "fixed";

    textArea.style.left = "-9999px";

    document.body.appendChild(textArea);

    textArea.focus();

    textArea.select();

    try {

      document.execCommand('copy');

      showSvgToast(successMsg, 'success');

    } catch (err) {

      showSvgToast("Failed to copy link.", "info");

    }

    document.body.removeChild(textArea);

  }



  document.addEventListener('click', function(e) {

    // 1. SHARE JOB BUTTON

    const shareBtn = e.target.closest('.js-share-job-btn');

    if (shareBtn) {

      e.preventDefault();

      e.stopPropagation();

      

      const card = shareBtn.closest('.job-card, .jc-detail-card');

      const jobTitle = shareBtn.getAttribute('data-job-title') || card?.querySelector('h3, h4')?.textContent?.trim() || 'Job Opening';

      const shareUrl = window.location.href;

      const shareText = `Check out this job opening: "${jobTitle}" at Sky Vision Group of Consultancy!\nApply here: ${shareUrl}`;

      

      if (navigator.share) {

        navigator.share({

          title: jobTitle,

          text: shareText,

          url: shareUrl

        }).catch(() => {

          copyToClipboard(shareText, `Link for "${jobTitle}" copied to clipboard!`);

        });

      } else {

        copyToClipboard(shareText, `Link for "${jobTitle}" copied to clipboard!`);

      }

      return;

    }

    

    // 2. SAVE JOB BUTTON

    const saveBtn = e.target.closest('.js-save-job-btn');

    if (saveBtn) {

      e.preventDefault();

      e.stopPropagation();

      

      const card = saveBtn.closest('.job-card, .jc-detail-card, .jc-icon-card');

      const jobTitle = saveBtn.getAttribute('data-job-title') || card?.querySelector('h3, h4')?.textContent?.trim() || 'Job Opening';

      const jobId = saveBtn.getAttribute('data-job-id') || card?.dataset?.jobId || '';

      const key = jobId ? `id_${jobId}` : jobTitle;

      

      let savedJobs = getLocalSavedJobs();

      const isCurrentlySaved = savedJobs.includes(key) || (jobId && savedJobs.includes(`id_${jobId}`)) || (jobTitle && savedJobs.includes(jobTitle));

      

      if (isCurrentlySaved) {

        savedJobs = savedJobs.filter(k => k !== key && k !== `id_${jobId}` && k !== jobTitle);

        setLocalSavedJobs(savedJobs);

        showSvgToast(`"${jobTitle}" removed from saved jobs.`, 'info');

      } else {

        savedJobs.push(key);

        setLocalSavedJobs(savedJobs);

        showSvgToast(`"${jobTitle}" saved to your profile!`, 'success');

      }

      

      syncSavedJobButtonsState();



      // Send DB toggle request to candidate portal

      fetch('/api/candidate/saved-jobs/toggle/', {

        method: 'POST',

        headers: {

          'Content-Type': 'application/json',

          'X-CSRFToken': getCookie('csrftoken') || ''

        },

        body: JSON.stringify({ job_id: jobId, job_title: jobTitle })

      })

      .then(r => r.json())

      .then(res => {

        if (res.status === 'success') {

          if (res.action === 'saved') {

            showSvgToast(`"${jobTitle}" saved to Candidate Portal!`, 'success');

          }

        } else if (res.message && (res.message.includes('login') || res.message.includes('Authentication'))) {

          showSvgToast(`Login as Candidate to view saved jobs in your Portal!`, 'info');

        }

      })

      .catch(() => {});



      return;

    }

  });



});
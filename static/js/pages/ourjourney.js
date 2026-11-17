/* =========================================================
   OUR JOURNEY PAGE — standalone script.
   Does NOT modify or depend on script.js logic (that file still
   handles the shared header/footer/mobile-menu/scroll-top behaviour).
   Handles only what's unique to this page:
     1) Scroll-reveal (fade-up) for hero, story, timeline, milestones,
        impact and CTA sections
     2) Animated counters for "Our Journey In Numbers"
========================================================= */
document.addEventListener("DOMContentLoaded", () => {

    /* ---------------------------------------------------------
       1) SCROLL REVEAL
    --------------------------------------------------------- */
    const revealSelectors = [
        ".oj-hero-copy",
        ".oj-hero-visual",
        ".oj-story-visual",
        ".oj-story-copy",
        ".oj-feature-card",
        ".oj-tl-row",
        ".oj-milestone-card",
        ".oj-impact-visual",
        ".oj-impact-item",
        ".oj-number-card",
        ".oj-la-copy"
    ];

    const revealEls = document.querySelectorAll(revealSelectors.join(","));

    if (revealEls.length) {
        const delayCounters = new WeakMap();

        revealEls.forEach((el) => {
            el.classList.add("oj-reveal");
            const parent = el.parentElement;
            const count = delayCounters.get(parent) || 0;
            delayCounters.set(parent, count + 1);
            el.style.transitionDelay = Math.min(count * 0.1, 0.5) + "s";
        });

        if ("IntersectionObserver" in window) {
            const io = new IntersectionObserver((entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("in-view");
                        io.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.15, rootMargin: "0px 0px -60px 0px" });

            revealEls.forEach((el) => io.observe(el));
        } else {
            revealEls.forEach((el) => el.classList.add("in-view"));
        }
    }

    /* ---------------------------------------------------------
       2) ANIMATED COUNTERS — "Our Journey In Numbers"
    --------------------------------------------------------- */
    const counters = document.querySelectorAll(".oj-count[data-count]");

    if (counters.length) {
        const animateCounter = (el) => {
            const target = parseFloat(el.getAttribute("data-count"));
            const suffix = el.getAttribute("data-suffix") || "";
            const duration = 1500;
            const start = performance.now();

            const step = (now) => {
                const progress = Math.min((now - start) / duration, 1);
                const eased = 1 - Math.pow(1 - progress, 3);
                const value = Math.floor(eased * target);
                el.textContent = value.toLocaleString("en-IN") + suffix;
                if (progress < 1) {
                    requestAnimationFrame(step);
                } else {
                    el.textContent = target.toLocaleString("en-IN") + suffix;
                }
            };
            requestAnimationFrame(step);
        };

        if ("IntersectionObserver" in window) {
            const counterIO = new IntersectionObserver((entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        animateCounter(entry.target);
                        counterIO.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.4 });

            counters.forEach((el) => counterIO.observe(el));
        } else {
            counters.forEach(animateCounter);
        }
    }

});
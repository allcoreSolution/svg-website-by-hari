// contact.js - Handles contact form submissions across the website
const API_BASE = "";

function getCsrfToken(form) {
  let token = form ? form.querySelector('input[name="csrfmiddlewaretoken"]')?.value : null;
  if (!token && typeof getCookie === 'function') {
    token = getCookie('csrftoken');
  }
  if (!token) {
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    if (match) token = match[1];
  }
  return token || '';
}

window.handleContactSubmit = async function(e, form) {
  if (e) {
    e.preventDefault();
    e.stopPropagation();
  }
  if (!form) form = e ? e.target : document.getElementById("homeContactForm");

  const submitBtn = form.querySelector('button[type="submit"]') || form.querySelector('.contact-btn');
  const originalText = submitBtn ? submitBtn.innerText : "Submit Now";
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerText = "Submitting...";
  }

  const nameInput = form.querySelector('input[name="name"]') || form.querySelector('#contactName') || form.querySelector('input[type="text"]:not([name="website_url"])');
  const emailInput = form.querySelector('input[name="email"]') || form.querySelector('#contactEmail') || form.querySelector('input[type="email"]');
  const phoneInput = form.querySelector('input[name="phone"]') || form.querySelector('#contactPhone') || form.querySelector('input[type="tel"]');
  const serviceInput = form.querySelector('select[name="service"]') || form.querySelector('#contactService') || form.querySelector('select');
  const messageInput = form.querySelector('textarea[name="message"]') || form.querySelector('#contactMessage') || form.querySelector('textarea');
  const honeypotInput = form.querySelector('input[name="website_url"]') || form.querySelector('input[name="website"]');

  const serviceVal = serviceInput ? serviceInput.value : "";
  const payload = {
    name: nameInput ? nameInput.value.trim() : "",
    email: emailInput ? emailInput.value.trim() : "",
    phone: phoneInput ? phoneInput.value.trim() : "",
    service: (serviceVal && serviceVal !== "Service Required") ? serviceVal : "General Inquiry",
    message: messageInput ? messageInput.value.trim() : "",
    website_url: honeypotInput ? honeypotInput.value : ""
  };

  try {
    const response = await fetch(`${API_BASE}/api/contact/`, {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken(form)
      },
      body: JSON.stringify(payload)
    });
    const result = await response.json();
    if (response.ok && result.status === "success") {
      alert("✓ " + (result.message || "Thank you! Your enquiry has been submitted."));
      form.reset();
    } else if (response.status === 413) {
      alert("❌ Payload too large. Please shorten your message.");
    } else if (response.status === 429) {
      alert("⚠️ " + (result.message || "Too many requests. Please try again later."));
    } else {
      alert("❌ " + (result.message || "Something went wrong. Please check your details."));
    }
  } catch (err) {
    console.error("Contact Form Error:", err);
    alert("Server Error! Please check your network connection.");
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerText = originalText;
    }
  }
  return false;
};

function initContactForm(form) {
  if (!form || form.dataset.contactBound === "true") return;
  form.dataset.contactBound = "true";

  form.addEventListener("submit", function (e) {
    window.handleContactSubmit(e, form);
  });
}


document.addEventListener("DOMContentLoaded", function () {
  // 1. All standalone contact forms (Home page, Gallery page, Contact page, etc.)
  const contactForms = document.querySelectorAll(
    "#contactPageForm, #homeContactForm, #galleryContactForm, .contact-ajax-form, .contact-form form"
  );
  contactForms.forEach(initContactForm);

  // 2. Popup Modal Apply/Contact Form
  const modalForm = document.getElementById("applyModalForm") || document.getElementById("applymodalForm");
  if (modalForm) {
    modalForm.addEventListener("submit", async function (e) {
      e.preventDefault();
      const submitBtn = modalForm.querySelector('button[type="submit"]');
      const originalText = submitBtn ? submitBtn.innerText : "Submit";
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerText = "Submitting...";
      }

      const nameInput = modalForm.querySelector('input[name="name"]') || modalForm.querySelector('input[type="text"]:not([name="website_url"])');
      const emailInput = modalForm.querySelector('input[name="email"]') || modalForm.querySelector('input[type="email"]');
      const phoneInput = modalForm.querySelector('input[name="phone"]') || modalForm.querySelector('input[type="tel"]');
      const serviceInput = modalForm.querySelector("select");
      const messageInput = modalForm.querySelector("textarea");
      const honeypotInput = modalForm.querySelector('input[name="website_url"]');

      const payload = {
        name: nameInput ? nameInput.value.trim() : "",
        email: emailInput ? emailInput.value.trim() : "",
        phone: phoneInput ? phoneInput.value.trim() : "",
        service: serviceInput && serviceInput.value && serviceInput.value !== "Choose Service" ? serviceInput.value : "General Inquiry",
        message: messageInput ? messageInput.value.trim() : "",
        website_url: honeypotInput ? honeypotInput.value : ""
      };

      try {
        const response = await fetch(`${API_BASE}/api/contact/`, {
          method: "POST",
          headers: { 
            "Content-Type": "application/json",
            "X-CSRFToken": getCsrfToken(modalForm)
          },
          body: JSON.stringify(payload)
        });
        const result = await response.json();
        if (response.ok && result.status === "success") {
          alert("✓ " + (result.message || "Thank you! We will contact you soon."));
          modalForm.reset();
          const overlay = document.getElementById("applyModalOverlay");
          if (overlay) {
            overlay.classList.remove("active");
            overlay.style.display = "none";
            document.body.classList.remove("popup-open");
          }
        } else if (response.status === 413) {
          alert("❌ Payload too large. Please shorten your message.");
        } else if (response.status === 429) {
          alert("⚠️ " + (result.message || "Too many requests. Please try again later."));
        } else {
          alert("❌ " + (result.message || "Something went wrong. Please check your details."));
        }
      } catch (err) {
        console.error("Modal Form Error:", err);
        alert("Server Error! Please try again.");
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerText = originalText;
        }
      }
    });
  }
});
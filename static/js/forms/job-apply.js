// job-apply.js - Visual File Upload Confirmation Handler for Django App
document.addEventListener("DOMContentLoaded", function () {
  setupJobApplyFileUpload();
});

function setupJobApplyFileUpload() {
  const fileInputs = document.querySelectorAll('#jobApplyResume, #jobApplyResumeFile, #internshipApplyResumeFile, #opResumeInput, #rmResumeFile, .job-apply-file-input');
  
  fileInputs.forEach((fileInput) => {
    if (!fileInput) return;

    const dropZone = fileInput.closest('.job-apply-upload') || 
                     fileInput.closest('.job-apply-upload-zone') || 
                     fileInput.closest('.resume-upload-area') || 
                     fileInput.parentElement;
    if (!dropZone) return;

    // If already initialized by script.js or previous pass, don't double attach
    if (dropZone.dataset.uploadInitialized === 'true' || fileInput.dataset.uploadInitialized === 'true') {
      return;
    }
    dropZone.dataset.uploadInitialized = 'true';
    fileInput.dataset.uploadInitialized = 'true';

    // Check for a dedicated sibling preview container (.job-apply-file-preview)
    const fieldContainer = dropZone.parentElement;
    const previewContainer = fieldContainer ? fieldContainer.querySelector('.job-apply-file-preview, #jobApplyFilePreview, #internshipApplyFilePreview') : null;
    const previewFileName = previewContainer ? previewContainer.querySelector('.job-apply-file-name, #jobApplyFileName, #internshipApplyFileName') : null;
    const previewFileSize = previewContainer ? previewContainer.querySelector('.job-apply-file-size, #jobApplyFileSize, #internshipApplyFileSize') : null;
    const previewRemoveBtn = previewContainer ? previewContainer.querySelector('.job-apply-file-remove, #jobApplyFileRemove, #internshipApplyFileRemove') : null;

    if (!dropZone.dataset.originalHtml) {
      dropZone.dataset.originalHtml = dropZone.innerHTML;
    }

    const formatFileSize = (bytes) => {
      if (!bytes) return '0 KB';
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
      return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    };

    const validateFile = (file) => {
      if (!file) return false;
      const ext = file.name.split('.').pop().toLowerCase();
      if (!['pdf', 'doc', 'docx'].includes(ext)) {
        alert('❌ Invalid file format. Supported formats: PDF, DOC, DOCX');
        return false;
      }
      const maxBytes = 10 * 1024 * 1024; // 10MB
      if (file.size > maxBytes) {
        alert('❌ File size exceeds 10MB limit. Please select a smaller document.');
        return false;
      }
      return true;
    };

    const resetUI = () => {
      fileInput.value = '';
      if (previewContainer) {
        previewContainer.style.display = 'none';
        dropZone.style.display = 'flex';
        dropZone.classList.remove('drag-over', 'file-selected');
      } else {
        dropZone.classList.remove('file-selected', 'drag-over');
        if (dropZone.dataset.originalHtml) {
          dropZone.innerHTML = dropZone.dataset.originalHtml;
          dropZone.appendChild(fileInput);
          attachInputEvents();
        }
      }
    };

    const updateUIForFile = (file) => {
      if (!file) {
        resetUI();
        return;
      }

      if (!validateFile(file)) {
        resetUI();
        return;
      }

      const fileName = file.name;
      const fileSize = formatFileSize(file.size);

      if (previewContainer) {
        if (previewFileName) previewFileName.textContent = fileName;
        if (previewFileSize) previewFileSize.textContent = fileSize;
        previewContainer.style.display = 'flex';
        dropZone.style.display = 'none';
      } else {
        dropZone.classList.add('file-selected');
        dropZone.classList.remove('drag-over');

        dropZone.innerHTML = `
          <i class="fa-solid fa-file-circle-check" style="font-size: 36px; color: #10b981; margin-bottom: 4px;"></i>
          <span style="color: #047857; font-weight: 700; font-size: 15px; display: block;">✓ Document Uploaded: ${fileName}</span>
          <small style="color: #059669; font-weight: 500; font-size: 12px; display: block; margin-top: 2px;">Size: ${fileSize} — Click or Drag to replace</small>
          <button type="button" class="job-apply-remove-btn" style="margin-top: 8px;"><i class="fa-solid fa-trash-can"></i> Remove File</button>
        `;

        dropZone.appendChild(fileInput);

        const removeBtn = dropZone.querySelector('.job-apply-remove-btn');
        if (removeBtn) {
          removeBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            resetUI();
          });
        }
      }
    };

    // Click on dropzone to trigger native file chooser
    dropZone.addEventListener('click', (e) => {
      if (e.target.closest('.job-apply-remove-btn') || e.target.closest('.job-apply-file-remove')) return;
      if (e.target === fileInput) return;
      fileInput.click();
    });

    // Keyboard support (Enter or Space)
    dropZone.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        fileInput.click();
      }
    });

    if (previewRemoveBtn) {
      previewRemoveBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        resetUI();
      });
    }

    const attachInputEvents = () => {
      const currentInput = dropZone.querySelector('input[type="file"]') || fileInput;
      if (!currentInput) return;

      currentInput.addEventListener('change', function () {
        if (this.files && this.files.length > 0) {
          updateUIForFile(this.files[0]);
        } else {
          resetUI();
        }
      });
    };

    attachInputEvents();

    ['dragenter', 'dragover'].forEach((eventName) => {
      dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.add('drag-over');
      }, false);
    });

    ['dragleave', 'dragend'].forEach((eventName) => {
      dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove('drag-over');
      }, false);
    });

    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.remove('drag-over');

      const dt = e.dataTransfer;
      if (dt && dt.files && dt.files.length > 0) {
        fileInput.files = dt.files;
        updateUIForFile(dt.files[0]);
      }
    }, false);

    const parentForm = fileInput.closest('form');
    if (parentForm) {
      parentForm.addEventListener('reset', () => {
        setTimeout(resetUI, 10);
      });
    }
  });
}
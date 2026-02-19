const fileInput = document.getElementById('file-input');
const uploadLabel = document.getElementById('upload-label');
const uploadText = document.getElementById('upload-text');
const stepUpload = document.getElementById('step-upload');
const stepFormat = document.getElementById('step-format');
const stepProgress = document.getElementById('step-progress');
const stepDownload = document.getElementById('step-download');
const stepError = document.getElementById('step-error');
const formatOptions = document.getElementById('format-options');
const convertBtn = document.getElementById('convert-btn');
const progressBar = document.getElementById('progress-bar');
const progressLabel = document.getElementById('progress-label');
const downloadLink = document.getElementById('download-link');
const errorMessage = document.getElementById('error-message');

let fileId = null;
let selectedFormat = null;

function show(el) { el.classList.remove('hidden'); }
function hide(el) { el.classList.add('hidden'); }

function showError(msg) {
  errorMessage.textContent = msg || 'Something went wrong.';
  hide(stepUpload); hide(stepFormat); hide(stepProgress); hide(stepDownload);
  show(stepError);
}

function reset() {
  fileId = null;
  selectedFormat = null;
  fileInput.value = '';
  uploadText.textContent = 'Click to select a file';
  formatOptions.innerHTML = '';
  convertBtn.disabled = true;
  progressBar.style.width = '0%';
  hide(stepFormat); hide(stepProgress); hide(stepDownload); hide(stepError);
  show(stepUpload);
}

document.getElementById('reset-btn').addEventListener('click', reset);
document.getElementById('back-btn').addEventListener('click', () => {
  hide(stepFormat);
  show(stepUpload);
  fileInput.value = '';
  uploadText.textContent = 'Click to select a file';
  formatOptions.innerHTML = '';
  selectedFormat = null;
  fileId = null;
  convertBtn.disabled = true;
});
document.getElementById('error-reset-btn').addEventListener('click', reset);

fileInput.addEventListener('change', async () => {
  const file = fileInput.files[0];
  if (!file) return;

  uploadText.textContent = `Uploading: ${file.name}`;

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch('/upload', { method: 'POST', body: formData });
    const data = await res.json();

    if (!res.ok) return showError(data.error);

    fileId = data.file_id;
    uploadText.textContent = `Selected: ${file.name}`;

    formatOptions.innerHTML = '';
    selectedFormat = null;
    convertBtn.disabled = true;

    data.options.forEach(fmt => {
      const btn = document.createElement('button');
      btn.textContent = fmt.toUpperCase();
      btn.className = 'format-btn';
      btn.addEventListener('click', () => {
        document.querySelectorAll('.format-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        selectedFormat = fmt;
        convertBtn.disabled = false;
      });
      formatOptions.appendChild(btn);
    });

    hide(stepUpload);
    show(stepFormat);
  } catch {
    showError('Upload failed. Is the server running?');
  }
});

convertBtn.addEventListener('click', async () => {
  if (!fileId || !selectedFormat) return;

  hide(stepFormat);
  show(stepProgress);
  progressLabel.textContent = 'Converting...';

  // Simulated staged progress while conversion runs
  let width = 0;
  const interval = setInterval(() => {
    if (width < 85) { width += 5; progressBar.style.width = `${width}%`; }
  }, 300);

  try {
    const res = await fetch('/convert', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ file_id: fileId, target: selectedFormat }),
    });
    const data = await res.json();

    clearInterval(interval);

    if (!res.ok) return showError(data.error);

    progressBar.style.width = '100%';
    progressLabel.textContent = 'Done!';

    downloadLink.href = `/download/${data.download_id}`;
    downloadLink.download = data.download_id;
    // Show zip note if multi-page
    if (data.download_id.endsWith('.zip')) {
      document.querySelector('#step-download .label').textContent =
        'Your file is ready! (ZIP — one image per page)';
    } else {
      document.querySelector('#step-download .label').textContent = 'Your file is ready!';
    }

    setTimeout(() => { hide(stepProgress); show(stepDownload); }, 500);
  } catch {
    clearInterval(interval);
    showError('Conversion failed. Check server logs.');
  }
});

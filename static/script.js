const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const processBtn = document.getElementById('process-btn');
const uploadSection = document.getElementById('upload-section');
const progressSection = document.getElementById('progress-section');
const resultSection = document.getElementById('result-section');
const progressBar = document.getElementById('progress-bar');
const progressText = document.getElementById('progress-text');
const statusBadge = document.getElementById('status-badge');
const beforeText = document.getElementById('before-text');
const afterText = document.getElementById('after-text');
const downloadLink = document.getElementById('download-link');
const resetBtn = document.getElementById('reset-btn');
const modeSelect = document.getElementById('mode-select');

let selectedFile = null;
let pollInterval = null;

// Drag and Drop Logic
dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('active');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('active');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('active');
    if (e.dataTransfer.files.length) {
        handleFileSelect(e.dataTransfer.files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) {
        handleFileSelect(e.target.files[0]);
    }
});

const liveLog = document.getElementById('live-log');
const originalViewer = document.getElementById('original-viewer');
const processedViewer = document.getElementById('processed-viewer');

let originalPdfBlob = null;

function handleFileSelect(file) {
    if (file.type !== 'application/pdf') {
        alert('Please select a PDF file.');
        return;
    }
    selectedFile = file;
    originalPdfBlob = URL.createObjectURL(file);
    dropZone.querySelector('span').textContent = `Ready: ${file.name}`;
    processBtn.disabled = false;
}

// Processing Logic
processBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('mode', modeSelect.value);

    uploadSection.classList.add('hidden');
    progressSection.classList.remove('hidden');
    liveLog.innerHTML = '<div class="log-entry">Initializing connection...</div>';

    try {
        const response = await fetch('/upload?mode=' + modeSelect.value, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        startPolling(data.task_id);
    } catch (err) {
        console.error(err);
        alert('Upload failed.');
    }
});

function startPolling(taskId) {
    const startTime = Date.now();

    pollInterval = setInterval(async () => {
        try {
            const response = await fetch(`/status/${taskId}`);
            const data = await response.json();

            updateProgress(data);

            if (data.status === 'completed') {
                clearInterval(pollInterval);
                finishProcessing(data, taskId);
            } else if (data.status === 'failed') {
                clearInterval(pollInterval);
                alert(`Error: ${data.error}`);
                resetUI();
            }
        } catch (err) {
            console.error(err);
        }
    }, 1000);
}

function updateProgress(data) {
    const { progress, total_pages, status, sample_text } = data;

    statusBadge.textContent = status.charAt(0).toUpperCase() + status.slice(1) + '...';

    if (total_pages > 0) {
        const percent = (progress / total_pages) * 100;
        progressBar.style.width = `${percent}%`;
        progressText.textContent = `Processing Page ${progress} / ${total_pages}`;

        if (sample_text && sample_text.length > 0) {
            const lastText = sample_text[sample_text.length - 1].text;
            addLog(`Page ${progress}: ${lastText}`);
        }
    }
}

function addLog(msg) {
    const div = document.createElement('div');
    div.className = 'log-entry';
    div.textContent = msg;
    liveLog.prepend(div);
}

async function finishProcessing(data, taskId) {
    progressSection.classList.add('hidden');
    resultSection.classList.remove('hidden');

    downloadLink.href = data.result_url;

    // Set viewer sources
    originalViewer.src = originalPdfBlob;

    // Fetch the result as a blob for the viewer
    const response = await fetch(data.result_url);
    const blob = await response.blob();
    processedViewer.src = URL.createObjectURL(blob);
}

resetBtn.addEventListener('click', resetUI);

function resetUI() {
    resultSection.classList.add('hidden');
    progressSection.classList.add('hidden');
    uploadSection.classList.remove('hidden');
    selectedFile = null;
    processBtn.disabled = true;
    dropZone.querySelector('span').textContent = 'Drag & Drop PDF or click to browse';
    progressBar.style.width = '0%';
}

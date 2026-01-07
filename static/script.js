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

function handleFileSelect(file) {
    if (file.type !== 'application/pdf') {
        alert('Please select a PDF file.');
        return;
    }
    selectedFile = file;
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

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        startPolling(data.task_id);
    } catch (err) {
        console.error(err);
        alert('Upload failed. Check server console.');
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
                finishProcessing(data);
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
    const { progress, total_pages, status } = data;

    statusBadge.textContent = status.charAt(0).toUpperCase() + status.slice(1) + '...';

    if (total_pages > 0) {
        const percent = (progress / total_pages) * 100;
        progressBar.style.width = `${percent}%`;
        progressText.textContent = `Page ${progress} / ${total_pages}`;
    }
}

function finishProcessing(data) {
    progressSection.classList.add('hidden');
    resultSection.classList.remove('hidden');

    downloadLink.href = data.result_url;

    // Update comparison text
    if (data.sample_text && data.sample_text.length > 0) {
        // Since we can't easily get the original garbled text through OCR (it's what we fixed)
        // we'll show a demonstration or leave a placeholder.
        // For real use, we could extract page 1 original text too, but that's overkill for now.
        beforeText.textContent = "d'n'sL ck/fw ;+lxtf...";
        afterText.textContent = data.sample_text.map(b => b.text).join(' ');
    }
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

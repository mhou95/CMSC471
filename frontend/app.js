const API_ENDPOINT = window.location.origin; // Will be API Gateway URL after deployment

async function uploadImage() {
    const fileInput = document.getElementById('imageInput');
    const file = fileInput.files[0];

    if (!file) {
        alert('Please select an image first');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        // Upload image to inbox
        const uploadResponse = await fetch(`${API_ENDPOINT}/api/inbox`, {
            method: 'POST',
            body: formData
        });

        if (!uploadResponse.ok) {
            throw new Error(`Upload failed: ${uploadResponse.statusText}`);
        }

        const uploadData = await uploadResponse.json();
        const objectKey = uploadData.objectKey;

        // Submit job
        const submitResponse = await fetch(`${API_ENDPOINT}/api/jobs`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ imageKey: objectKey })
        });

        if (!submitResponse.ok) {
            throw new Error(`Job submission failed: ${submitResponse.statusText}`);
        }

        const jobData = await submitResponse.json();
        const jobId = jobData.jobId;

        // Show job status
        document.getElementById('jobStatus').classList.remove('hidden');
        document.getElementById('jobId').textContent = jobId;

        // Poll for results
        pollJobStatus(jobId);
    } catch (error) {
        console.error('Error:', error);
        alert(`Error: ${error.message}`);
    }
}

async function pollJobStatus(jobId) {
    const maxAttempts = 60;
    let attempt = 0;

    const pollInterval = setInterval(async () => {
        attempt++;

        try {
            const response = await fetch(`${API_ENDPOINT}/api/jobs/${jobId}`);
            const data = await response.json();

            document.getElementById('status').textContent = data.status;

            if (data.status === 'SUCCEEDED') {
                clearInterval(pollInterval);
                showResults(data.extractedText, jobId);
                loadRecords();
            } else if (data.status === 'FAILED') {
                clearInterval(pollInterval);
                document.getElementById('statusMessage').innerHTML = `<p style="color: red;">Job failed</p>`;
            }
        } catch (error) {
            console.error('Poll error:', error);
        }

        if (attempt >= maxAttempts) {
            clearInterval(pollInterval);
            document.getElementById('statusMessage').innerHTML = `<p style="color: orange;">Job still processing...</p>`;
        }
    }, 2000);
}

function showResults(text, jobId) {
    document.getElementById('results').classList.remove('hidden');
    document.getElementById('extractedText').value = text;
    document.getElementById('extractedText').dataset.jobId = jobId;
}

async function downloadResults() {
    const text = document.getElementById('extractedText').value;
    const jobId = document.getElementById('extractedText').dataset.jobId;
    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', `result-${jobId}.txt`);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}

async function deleteResult() {
    const jobId = document.getElementById('extractedText').dataset.jobId;
    if (!confirm(`Delete record ${jobId}?`)) return;

    try {
        const response = await fetch(`${API_ENDPOINT}/api/records/${jobId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            document.getElementById('results').classList.add('hidden');
            loadRecords();
        } else {
            alert('Delete failed');
        }
    } catch (error) {
        console.error('Delete error:', error);
    }
}

async function loadRecords() {
    try {
        const response = await fetch(`${API_ENDPOINT}/api/records`);
        const records = await response.json();
        const recordsList = document.getElementById('recordsList');
        recordsList.innerHTML = '';

        if (records.length === 0) {
            recordsList.innerHTML = '<p>No records found</p>';
            return;
        }

        records.forEach(record => {
            const div = document.createElement('div');
            div.className = 'record-item';
            div.innerHTML = `
                <p><strong>Job ID:</strong> ${record.jobId}</p>
                <small>${new Date(record.createdAt).toLocaleString()}</small>
                <p>${record.extractedText.substring(0, 100)}...</p>
            `;
            recordsList.appendChild(div);
        });
    } catch (error) {
        console.error('Load records error:', error);
    }
}

// Load records on page load
window.addEventListener('load', loadRecords);

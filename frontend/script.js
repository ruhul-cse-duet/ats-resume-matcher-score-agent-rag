// Global state
let token = null;
let currentUser = null;

// DOM Elements
const loadingOverlay = document.getElementById('loadingOverlay');
const toast = document.getElementById('toast');
const authSection = document.getElementById('authSection');
const appSection = document.getElementById('appSection');
const userEmailEl = document.getElementById('userEmail');
const logoutBtn = document.getElementById('logoutBtn');

// Auth Form Elements
const loginForm = document.getElementById('loginForm');
const signupForm = document.getElementById('signupForm');
const loginEmail = document.getElementById('loginEmail');
const loginPassword = document.getElementById('loginPassword');
const signupEmail = document.getElementById('signupEmail');
const signupPassword = document.getElementById('signupPassword');

// App Form Elements
const analyzeForm = document.getElementById('analyzeForm');
const rewriteForm = document.getElementById('rewriteForm');
const jdInput = document.getElementById('jd');
const resumeInput = document.getElementById('resume');
const rawResumeInput = document.getElementById('rawresume');

// Result Elements
const resultSection = document.getElementById('resultSection');
const rewriteResultSection = document.getElementById('rewriteResultSection');

// Utility Functions
function showLoading(message = 'Processing...') {
    loadingOverlay.classList.add('active');
    loadingOverlay.querySelector('.loading-text').textContent = message;
}

function hideLoading() {
    loadingOverlay.classList.remove('active');
}

function showToast(message, type = 'success') {
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}

function handleError(error, customMessage = null) {
    console.error('Error:', error);
    hideLoading();
    
    let message = customMessage || 'An error occurred. Please try again.';
    
    if (error.message) {
        message = error.message;
    } else if (typeof error === 'string') {
        message = error;
    }
    
    showToast(message, 'error');
}

// API Request Handler with retry logic
async function apiRequest(url, options = {}, retries = 2) {
    let lastError;
    
    for (let i = 0; i <= retries; i++) {
        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    ...options.headers,
                }
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Request failed with status ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            lastError = error;
            
            // Don't retry on client errors (4xx) except 408 and 429
            if (error.message && error.message.includes('40') && 
                !error.message.includes('408') && !error.message.includes('429')) {
                throw error;
            }
            
            // Wait before retry (exponential backoff)
            if (i < retries) {
                await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, i)));
            }
        }
    }
    
    throw lastError;
}

// Tab Switching
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tabName = btn.dataset.tab;
        
        // Update buttons
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Update content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}Tab`).classList.add('active');
    });
});

// File upload display update
if (resumeInput) {
    resumeInput.addEventListener('change', (e) => {
        const fileName = e.target.files[0]?.name || 'Choose file or drag here';
        const fileDisplay = document.querySelector('.file-name');
        if (fileDisplay) {
            fileDisplay.textContent = fileName;
        }
    });
}

// Authentication Functions
async function signup(e) {
    e.preventDefault();
    
    const email = signupEmail.value.trim();
    const password = signupPassword.value;
    
    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email || !emailRegex.test(email)) {
        showToast('Please enter a valid email address', 'error');
        return;
    }
    
    if (!password) {
        showToast('Password is required', 'error');
        return;
    }
    
    if (password.length < 6) {
        showToast('Password must be at least 6 characters', 'error');
        return;
    }
    
    showLoading('Creating your account...');
    
    try {
        const formData = new FormData();
        formData.append('email', email);
        formData.append('password', password);
        
        const data = await apiRequest('/api/auth/signup', {
            method: 'POST',
            body: formData
        });
        
        token = data.access_token;
        currentUser = { id: data.user_id, email };
        
        // Store in localStorage
        localStorage.setItem('token', token);
        localStorage.setItem('userEmail', email);
        
        hideLoading();
        showToast('Account created successfully!', 'success');
        showApp();
        
        // Clear form
        signupForm.reset();
    } catch (error) {
        handleError(error);
    }
}

async function login(e) {
    e.preventDefault();
    
    const email = loginEmail.value.trim();
    const password = loginPassword.value;
    
    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email || !emailRegex.test(email)) {
        showToast('Please enter a valid email address', 'error');
        return;
    }
    
    if (!password) {
        showToast('Password is required', 'error');
        return;
    }
    
    showLoading('Signing you in...');
    
    try {
        const formData = new FormData();
        formData.append('email', email);
        formData.append('password', password);
        
        const data = await apiRequest('/api/auth/login', {
            method: 'POST',
            body: formData
        });
        
        token = data.access_token;
        currentUser = { id: data.user_id, email };
        
        // Store in localStorage
        localStorage.setItem('token', token);
        localStorage.setItem('userEmail', email);
        
        hideLoading();
        showToast('Welcome back!', 'success');
        showApp();
        
        // Clear form
        loginForm.reset();
    } catch (error) {
        handleError(error);
    }
}

function logout() {
    token = null;
    currentUser = null;
    localStorage.removeItem('token');
    localStorage.removeItem('userEmail');
    
    showAuth();
    showToast('Logged out successfully', 'success');
}

function showApp() {
    authSection.style.display = 'none';
    appSection.style.display = 'block';
    userEmailEl.textContent = currentUser.email;
    logoutBtn.style.display = 'block';
}

function showAuth() {
    authSection.style.display = 'block';
    appSection.style.display = 'none';
    userEmailEl.textContent = '';
    logoutBtn.style.display = 'none';
    
    // Clear results
    resultSection.style.display = 'none';
    rewriteResultSection.style.display = 'none';
}

// Analyze Resume
async function analyzeResume(e) {
    e.preventDefault();
    
    if (!token) {
        showToast('Please login first', 'error');
        return;
    }
    
    const file = resumeInput.files[0];
    const jd = jdInput.value.trim();
    
    if (!file) {
        showToast('Please select a resume file', 'error');
        return;
    }
    
    if (!jd || jd.length < 10) {
        showToast('Please enter a job description (at least 10 characters)', 'error');
        return;
    }
    
    // Validate file size (10MB)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
        showToast('File size must be less than 10MB', 'error');
        return;
    }
    
    // Validate file type
    const allowedTypes = ['.pdf', '.docx', '.txt'];
    const fileExt = '.' + file.name.split('.').pop().toLowerCase();
    if (!allowedTypes.includes(fileExt)) {
        showToast('Please upload a PDF, DOCX, or TXT file', 'error');
        return;
    }
    
    showLoading('Analyzing your resume...');
    
    try {
        const formData = new FormData();
        formData.append('resume', file);
        formData.append('jd', jd);
        
        const data = await apiRequest('/api/analyze', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });
        
        hideLoading();
        displayResults(data);
        showToast('Analysis completed successfully!', 'success');
        
    } catch (error) {
        handleError(error, 'Failed to analyze resume');
    }
}


function displayResults(data) {
    // Show result section
    resultSection.style.display = 'block';
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    
    // Animate score
    const scoreNumber = document.getElementById('scoreNumber');
    const scoreRingFill = document.getElementById('scoreRingFill');
    const score = data.score || 0;
    
    // Animate number count
    let currentScore = 0;
    const increment = score / 50;
    const timer = setInterval(() => {
        currentScore += increment;
        if (currentScore >= score) {
            currentScore = score;
            clearInterval(timer);
        }
        scoreNumber.textContent = Math.round(currentScore);
    }, 20);
    
    // Animate ring (339.292 is circumference of circle with radius 54)
    const circumference = 339.292;
    const offset = circumference - (score / 100) * circumference;
    scoreRingFill.style.strokeDashoffset = offset;
    
    // Update ring color based on score
    if (score >= 80) {
        scoreRingFill.style.stroke = '#10b981';
    } else if (score >= 60) {
        scoreRingFill.style.stroke = '#f59e0b';
    } else {
        scoreRingFill.style.stroke = '#ef4444';
    }
    
    // Display keywords
    const keywordsList = document.getElementById('keywordsList');
    const keywords = data.matched_keywords || [];
    
    if (keywords.length > 0) {
        keywordsList.innerHTML = keywords
            .map(k => `<span class="keyword-badge">${escapeHtml(k)}</span>`)
            .join('');
    } else {
        keywordsList.innerHTML = '<p class="keywords-empty">No matching keywords found</p>';
    }
    
    // Display analysis
    const analysisText = document.getElementById('analysisText');
    analysisText.textContent = data.analysis || 'No detailed analysis available.';
}


// Rewrite Resume
async function rewriteResume(e) {
    e.preventDefault();
    
    if (!token) {
        showToast('Please login first', 'error');
        return;
    }
    
    const resumeText = rawResumeInput.value.trim();
    const jd = jdInput.value.trim();
    
    if (!resumeText || resumeText.length < 50) {
        showToast('Please enter resume text (at least 50 characters)', 'error');
        return;
    }
    
    if (!jd || jd.length < 10) {
        showToast('Please enter a job description in the Analyze Resume section', 'error');
        return;
    }
    
    showLoading('Rewriting your resume...');
    
    try {
        const formData = new FormData();
        formData.append('resume_text', resumeText);
        formData.append('jd', jd);
        
        const data = await apiRequest('/api/rewrite', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });
        
        hideLoading();
        displayRewriteResults(data);
        showToast('Resume rewritten successfully!', 'success');
        
    } catch (error) {
        handleError(error, 'Failed to rewrite resume');
    }
}

function displayRewriteResults(data) {
    rewriteResultSection.style.display = 'block';
    rewriteResultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    
    const rewriteResult = document.getElementById('rewriteResult');
    
    // Format the result nicely
    let formattedResult;
    if (typeof data === 'object' && (data.summary || data.experience || data.skills)) {
        formattedResult = '';
        
        if (data.summary) {
            formattedResult += '=== SUMMARY ===\n\n' + data.summary + '\n\n';
        }
        
        if (data.experience && Array.isArray(data.experience)) {
            formattedResult += '=== EXPERIENCE ===\n\n';
            data.experience.forEach((exp, i) => {
                formattedResult += (i + 1) + '. ' + exp + '\n\n';
            });
        }
        
        if (data.skills && Array.isArray(data.skills)) {
            formattedResult += '=== SKILLS ===\n\n';
            formattedResult += data.skills.join(' • ') + '\n';
        }
    } else if (data.rewritten) {
        formattedResult = data.rewritten;
    } else {
        formattedResult = JSON.stringify(data, null, 2);
    }
    
    rewriteResult.textContent = formattedResult;
}

// Utility function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Copy to clipboard
document.getElementById('copyRewrite')?.addEventListener('click', () => {
    const rewriteResult = document.getElementById('rewriteResult');
    const text = rewriteResult.textContent;
    
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success');
    }).catch(() => {
        showToast('Failed to copy', 'error');
    });
});

// Clear results
document.getElementById('clearResults')?.addEventListener('click', () => {
    resultSection.style.display = 'none';
});

document.getElementById('clearRewriteResults')?.addEventListener('click', () => {
    rewriteResultSection.style.display = 'none';
});


// Event Listeners
loginForm?.addEventListener('submit', login);
signupForm?.addEventListener('submit', signup);
logoutBtn?.addEventListener('click', logout);
analyzeForm?.addEventListener('submit', analyzeResume);
rewriteForm?.addEventListener('submit', rewriteResume);

// Check for stored token on page load
window.addEventListener('DOMContentLoaded', () => {
    const storedToken = localStorage.getItem('token');
    const storedEmail = localStorage.getItem('userEmail');
    
    if (storedToken && storedEmail) {
        token = storedToken;
        currentUser = { email: storedEmail };
        showApp();
    } else {
        showAuth();
    }
});

// Add drag and drop support for file upload
if (resumeInput) {
    const fileUploadWrapper = document.querySelector('.file-upload-wrapper');
    
    if (fileUploadWrapper) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            fileUploadWrapper.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        ['dragenter', 'dragover'].forEach(eventName => {
            fileUploadWrapper.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            fileUploadWrapper.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight() {
            fileUploadWrapper.classList.add('drag-over');
        }
        
        function unhighlight() {
            fileUploadWrapper.classList.remove('drag-over');
        }
        
        fileUploadWrapper.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0) {
                resumeInput.files = files;
                const event = new Event('change');
                resumeInput.dispatchEvent(event);
            }
        }
    }
}

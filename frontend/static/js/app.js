/* app.js — Crop Disease Detection Frontend Logic */

const dropZone     = document.getElementById('drop-zone');
const dropInner    = document.getElementById('drop-inner');
const fileInput    = document.getElementById('file-input');
const previewImg   = document.getElementById('preview-img');
const uploadBtn    = document.getElementById('upload-btn');
const clearBtn     = document.getElementById('clear-btn');
const uploadCard   = document.getElementById('upload-card');
const loadingCard  = document.getElementById('loading-card');
const resultCard   = document.getElementById('result-card');
const errorCard    = document.getElementById('error-card');
const resultDisease= document.getElementById('result-disease');
const confidencePct= document.getElementById('confidence-pct');
const confBar      = document.getElementById('conf-bar');
const resultBadge  = document.getElementById('result-badge');
const resultPreview= document.getElementById('result-preview');
const recommendationTitle = document.getElementById('recommendation-title');
const recommendationList  = document.getElementById('recommendation-list');
const errorMsg     = document.getElementById('error-msg');
const chatbotShell = document.getElementById('chatbot-shell');
const chatbotToggle= document.getElementById('chatbot-toggle');
const chatbotPanel = document.getElementById('chatbot-panel');
const chatbotClose = document.getElementById('chatbot-close');
const chatbotForm  = document.getElementById('chatbot-form');
const chatbotInput = document.getElementById('chatbot-input');
const chatbotSend  = document.getElementById('chatbot-send');
const chatbotMessages = document.getElementById('chatbot-messages');
const chatbotContext = document.getElementById('chatbot-context');
const chatbotContextTitle = document.getElementById('chatbot-context-title');

let selectedFile = null;
let latestPrediction = null;
let chatHistory = [];
let chatBusy = false;

// ── File Selection via Click ──────────────────────────
dropZone.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', (e) => {
  if (e.target.files.length > 0) handleFile(e.target.files[0]);
});

// ── Drag & Drop ───────────────────────────────────────
dropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
  dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropZone.classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file) handleFile(file);
});

// ── Handle Selected File ──────────────────────────────
function handleFile(file) {
  const allowed = ['image/jpeg', 'image/png', 'image/webp', 'image/bmp'];
  if (!allowed.includes(file.type)) {
    showError('Unsupported file type. Please upload a JPG, PNG, or WEBP image.');
    return;
  }
  if (file.size > 10 * 1024 * 1024) {
    showError('File too large. Maximum size is 10MB.');
    return;
  }

  selectedFile = file;
  const url = URL.createObjectURL(file);

  // Show preview
  dropInner.style.display = 'none';
  previewImg.src = url;
  previewImg.classList.add('visible');
  dropZone.classList.add('has-preview');
  clearBtn.style.display = 'inline-flex';
  uploadBtn.disabled = false;
}

// ── Clear Selection ───────────────────────────────────
clearBtn.addEventListener('click', resetUpload);

function resetUpload() {
  selectedFile = null;
  fileInput.value = '';
  previewImg.src = '';
  previewImg.classList.remove('visible');
  dropZone.classList.remove('has-preview');
  dropInner.style.display = 'block';
  clearBtn.style.display = 'none';
  uploadBtn.disabled = false;
  confBar.style.width = '0%';
  hide(resultCard);
  hide(errorCard);
  show(uploadCard);
}

// ── Upload & Predict ──────────────────────────────────
uploadBtn.addEventListener('click', async () => {
  if (!selectedFile) {
    fileInput.click();
    return;
  }
  await runPrediction();
});

async function runPrediction() {
  // Show loading
  hide(uploadCard);
  hide(resultCard);
  hide(errorCard);
  show(loadingCard);

  const formData = new FormData();
  formData.append('image', selectedFile);

  try {
    const response = await fetch('/api/predict/', {
      method: 'POST',
      body: formData,
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
      },
    });

    const data = await response.json();

    hide(loadingCard);

    if (!response.ok || !data.success) {
      showError(data.error || `Server error (HTTP ${response.status})`);
      return;
    }

    showResult(data);

  } catch (err) {
    hide(loadingCard);
    showError('Could not connect to server. Make sure Django is running on localhost:8000.');
  }
}

// ── Show Result ───────────────────────────────────────
function showResult(data) {
  resultDisease.textContent = data.prediction;
  resultPreview.src = URL.createObjectURL(selectedFile);

  const pct = Math.round(data.confidence * 100);
  confidencePct.textContent = `${pct}%`;

  // Animate confidence bar
  setTimeout(() => { confBar.style.width = `${pct}%`; }, 50);

  // Badge
  const isHealthy = data.class_raw && data.class_raw.includes('healthy');
  const notDetected = !data.detected;

  resultBadge.className = 'result-badge';
  if (notDetected) {
    resultBadge.textContent = 'No Disease Detected';
    resultBadge.classList.add('badge-none');
  } else if (isHealthy) {
    resultBadge.textContent = 'Healthy Crop';
    resultBadge.classList.add('badge-healthy');
  } else {
    resultBadge.textContent = 'Disease Detected';
    resultBadge.classList.add('badge-disease');
  }

  renderRecommendation(data.recommendation);
  latestPrediction = data;
  updateChatContext(data);
  show(resultCard);
}

function renderRecommendation(recommendation) {
  const fallback = {
    title: 'General Recommendation',
    steps: [
      'Remove visibly affected plant parts if symptoms are spreading.',
      'Improve field hygiene, spacing, drainage, and irrigation practice.',
      'Consult a local agriculture expert before using chemical treatment.',
    ],
  };
  const details = recommendation || fallback;

  recommendationTitle.textContent = details.title || fallback.title;
  recommendationList.innerHTML = '';

  const steps = Array.isArray(details.steps) && details.steps.length > 0
    ? details.steps
    : fallback.steps;

  steps.forEach((step) => {
    const item = document.createElement('li');
    item.textContent = step;
    recommendationList.appendChild(item);
  });
}

// ── Show Error ────────────────────────────────────────
function showError(msg) {
  errorMsg.textContent = msg;
  hide(uploadCard);
  hide(loadingCard);
  show(errorCard);
}

// ── Retry Buttons ─────────────────────────────────────
document.getElementById('retry-btn').addEventListener('click', resetUpload);
document.getElementById('error-retry-btn').addEventListener('click', () => {
  hide(errorCard);
  show(uploadCard);
});

// ── Helpers ───────────────────────────────────────────
function show(el) { el.style.display = 'block'; }
function hide(el) { el.style.display = 'none'; }

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

// ── Groq CropCare Chatbot ────────────────────────────
if (chatbotShell && chatbotToggle && chatbotPanel) {
  chatbotToggle.addEventListener('click', () => {
    if (chatbotShell.classList.contains('open')) {
      closeChatbot();
    } else {
      openChatbot();
    }
  });

  chatbotClose.addEventListener('click', closeChatbot);

  chatbotForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    await sendChatMessage();
  });

  chatbotInput.addEventListener('input', resizeChatInput);

  chatbotInput.addEventListener('keydown', async (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      await sendChatMessage();
    }
  });

  document.querySelectorAll('.chatbot-chip').forEach((chip) => {
    chip.addEventListener('click', async () => {
      openChatbot();
      await sendChatMessage(chip.dataset.prompt);
    });
  });
}

function openChatbot() {
  chatbotShell.classList.add('open');
  chatbotPanel.setAttribute('aria-hidden', 'false');
  chatbotToggle.setAttribute('aria-expanded', 'true');
  setTimeout(() => chatbotInput.focus(), 120);
}

function closeChatbot() {
  chatbotShell.classList.remove('open');
  chatbotPanel.setAttribute('aria-hidden', 'true');
  chatbotToggle.setAttribute('aria-expanded', 'false');
}

async function sendChatMessage(promptOverride = '') {
  if (chatBusy) return;

  const prompt = (promptOverride || chatbotInput.value).trim();
  if (!prompt) return;

  const previousHistory = chatHistory.slice(-8);
  appendChatMessage('user', prompt);
  chatHistory.push({ role: 'user', content: prompt });

  chatbotInput.value = '';
  resizeChatInput();
  setChatBusy(true);

  const pendingMessage = appendChatMessage('assistant', 'Thinking through field guidance...', true);

  try {
    const response = await fetch('/api/chatbot/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      body: JSON.stringify({
        message: prompt,
        history: previousHistory,
        context: buildChatContext(),
      }),
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok || !data.success) {
      throw new Error(data.error || `Chatbot error (HTTP ${response.status})`);
    }

    updateChatMessage(pendingMessage, data.reply || 'No response was returned.');
    chatHistory.push({ role: 'assistant', content: data.reply || '' });
  } catch (err) {
    updateChatMessage(
      pendingMessage,
      err.message || 'Could not connect to the chatbot endpoint.',
      true
    );
  } finally {
    setChatBusy(false);
  }
}

function appendChatMessage(role, content, isLoading = false) {
  const message = document.createElement('div');
  message.className = `chatbot-message ${role === 'user' ? 'user' : 'bot'}`;
  if (isLoading) message.classList.add('is-loading');

  const label = document.createElement('span');
  label.className = 'message-label';
  label.textContent = role === 'user' ? 'You' : 'Advisor';

  const text = document.createElement('p');
  text.textContent = content;

  message.appendChild(label);
  message.appendChild(text);
  chatbotMessages.appendChild(message);
  scrollChatToBottom();
  return message;
}

function updateChatMessage(message, content, isError = false) {
  const text = message.querySelector('p');
  text.textContent = content;
  message.classList.remove('is-loading');
  message.classList.toggle('error', isError);
  scrollChatToBottom();
}

function setChatBusy(isBusy) {
  chatBusy = isBusy;
  chatbotInput.disabled = isBusy;
  chatbotSend.disabled = isBusy;
}

function updateChatContext(data) {
  if (!chatbotContext || !chatbotContextTitle || !data) return;

  const confidence = Number.isFinite(Number(data.confidence))
    ? `${Math.round(Number(data.confidence) * 100)}%`
    : 'confidence unavailable';

  chatbotContextTitle.textContent = `${data.prediction || 'Latest scan'} • ${confidence}`;
  chatbotContext.hidden = false;
}

function buildChatContext() {
  if (!latestPrediction) return null;

  return {
    prediction: latestPrediction.prediction,
    class_raw: latestPrediction.class_raw,
    confidence: latestPrediction.confidence,
    detected: latestPrediction.detected,
    recommendation: latestPrediction.recommendation,
  };
}

function resizeChatInput() {
  chatbotInput.style.height = 'auto';
  chatbotInput.style.height = `${Math.min(chatbotInput.scrollHeight, 110)}px`;
}

function scrollChatToBottom() {
  chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
}

const micBtn = document.getElementById("micBtn");
const chatBox = document.getElementById("chatBox");
const dots = document.getElementById("listeningDots");

let recognition = null;
let isListening = false;
let isSpeaking = false;
let isGenerating = false;
let forceRestart = false;
let availableVoices = [];
let pauseListening = false;

// ---------------------- Message UI ----------------------

function appendMessage(role, text) {
  const msg = document.createElement("div");
  msg.className = role === "user" ? "user-msg" : "bot-msg";
  msg.innerText = text;
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function appendLoading() {
  const loading = document.createElement("div");
  loading.className = "bot-msg";
  loading.id = "loadingBubble";
  loading.innerHTML = `<span class="dot"></span><span class="dot"></span><span class="dot"></span>`;
  chatBox.appendChild(loading);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function removeLoading() {
  const loading = document.getElementById("loadingBubble");
  if (loading) loading.remove();
}

// ---------------------- Voice Loading ----------------------

function loadVoices() {
  availableVoices = speechSynthesis.getVoices();
  if (!availableVoices.length) {
    speechSynthesis.onvoiceschanged = () => {
      availableVoices = speechSynthesis.getVoices();
    };
  }
}
loadVoices();

// ---------------------- Speech Synthesis ----------------------

function speakText(text) {
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "en-US";

  const preferredVoices = ["Samantha", "Google US English", "Microsoft Zira"];
  const chosenVoice = preferredVoices
    .map(name => availableVoices.find(v => v.name === name))
    .find(Boolean);

  if (chosenVoice) {
    utterance.voice = chosenVoice;
  } else {
    console.warn("No preferred voice found. Using default.");
  }

  utterance.onstart = () => {
    isSpeaking = true;
  };

  utterance.onend = () => {
    isSpeaking = false;
    // Always restart recognition after speech ends
    console.log("🔁 Restarting recognition after speaking.");
    forceRestart = true;
    startRecognition();
  };

  speechSynthesis.speak(utterance);
}

// ---------------------- Backend Communication ----------------------

function sendToBackend(text) {
  appendLoading();
  isGenerating = true;

  fetch("/voice", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text })
  })
    .then(res => res.json())
    .then(data => {
      removeLoading();
      isGenerating = false;
      const reply = data.response;
      appendMessage("bot", reply);
      speakText(reply);
    })
    .catch(err => {
      removeLoading();
      isGenerating = false;
      const fail = "Sorry, I couldn't get a response.";
      appendMessage("bot", fail);
      speakText(fail);
    });
}

// ---------------------- Speech Recognition ----------------------

function createRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    alert("Speech recognition not supported in this browser.");
    return null;
  }

  const recog = new SpeechRecognition();
  recog.lang = "en-IN";
  recog.continuous = false;
  recog.interimResults = false;

  recog.onstart = () => {
    console.log("🎙️ Speech recognition started");
    isListening = true;
    if (dots) dots.style.display = "flex";
  };

  recog.onresult = (event) => {
    const text = event.results?.[0]?.[0]?.transcript?.trim();
    if (!text) return;

    console.log("✅ Recognized text:", text);
    appendMessage("user", text);
    if (dots) dots.style.display = "none";
    recog.stop();
    isListening = false;
    sendToBackend(text);
  };

  recog.onerror = (e) => {
    console.error("❌ Speech recognition error:", e.error);
    if (dots) dots.style.display = "none";
    isListening = false;
    recog.stop();
  };

  recog.onend = () => {
    console.log("🛑 Speech recognition ended");
    isListening = false;
    if (!isGenerating && !isSpeaking && forceRestart) {
      console.log("Restarting recognition...");
      startRecognition();
    }
  };

  return recog;
}

function startRecognition() {
  if (pauseListening) {
    console.log("⏸️ Recognition is paused. Not starting.");
    return;
  }

  if (isGenerating || isSpeaking) {
    console.log("⏳ Not starting recognition - generating or speaking.");
    return;
  }

  if (!recognition) {
    recognition = createRecognition();
    if (!recognition) return;
  }

  try {
    recognition.start();
  } catch (err) {
    console.warn("⚠️ Could not start recognition:", err.message);
  }
}
function togglePause() {
  pauseListening = !pauseListening;

  if (pauseListening && recognition) {
    recognition.abort();
    console.log("🛑 Listening paused.");
  } else {
    console.log("▶️ Listening resumed.");
    startRecognition();
  }
}


// ---------------------- Mic Button ----------------------

micBtn.addEventListener("click", () => {
  if (recognition) recognition.abort();
  isGenerating = false;
  isSpeaking = false;
  isListening = false;
  forceRestart = true;
  startRecognition();
});

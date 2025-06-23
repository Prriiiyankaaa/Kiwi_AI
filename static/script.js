const micBtn = document.getElementById("micBtn");
const chatBox = document.getElementById("chatBox");
const dots = document.getElementById("listeningDots");

let recognition;
let isListening = false;
let isSpeaking = false;
let isGenerating = false;

// Add message to chat
function appendMessage(role, text) {
  const msg = document.createElement("div");
  msg.className = role === "user" ? "user-msg" : "bot-msg";
  msg.innerText = text;
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Show loading dots
function appendLoading() {
  const loading = document.createElement("div");
  loading.className = "bot-msg";
  loading.id = "loadingBubble";
  loading.innerHTML = `<span class="dot"></span><span class="dot"></span><span class="dot"></span>`;
  chatBox.appendChild(loading);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Remove loading
function removeLoading() {
  const loading = document.getElementById("loadingBubble");
  if (loading) loading.remove();
}
let availableVoices = [];

speechSynthesis.onvoiceschanged = () => {
  availableVoices = speechSynthesis.getVoices();
};

// Speak text
function speakText(text) {
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "en-US";

  const samantha = availableVoices.find(v => v.name === "Samantha");
  if (samantha) {
    utterance.voice = samantha;
  } else {
    console.warn("Samantha voice not found. Using default voice.");
  }

  utterance.onstart = () => {
    isSpeaking = true;
  };

  utterance.onend = () => {
    isSpeaking = false;
    if (!isGenerating) startRecognition(); // Resume mic after speaking
  };

  speechSynthesis.speak(utterance);
}

// Send text to backend
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
      appendMessage("bot", "Kiwi: " + reply);
      speakText(reply);
    })
    .catch(err => {
      removeLoading();
      isGenerating = false;
      const fail = "Sorry, I couldn't get a response.";
      appendMessage("bot", "Kiwi: " + fail);
      speakText(fail);
    });
}

// Start speech recognition
function startRecognition() {
  if (isGenerating || isSpeaking) {
    console.log("Not starting recognition - still generating or speaking.");
    return;
  }

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    alert("Speech recognition not supported in this browser.");
    return;
  }

  console.log("Starting speech recognition...");
  recognition = new SpeechRecognition();
  recognition.lang = "en-IN";
  recognition.continuous = false;
  recognition.interimResults = false;

  recognition.onstart = () => {
    console.log("🎙️ Speech recognition started");
    isListening = true;
    dots.style.display = "flex";
  };

  recognition.onresult = (event) => {
    const text = event.results[0][0].transcript;
    console.log("✅ Recognized text:", text);
    appendMessage("user", text);
    dots.style.display = "none";
    recognition.stop();
    isListening = false;
    sendToBackend(text);
  };

  recognition.onerror = (e) => {
    console.error("❌ Speech recognition error:", e.error);
    dots.style.display = "none";
    isListening = false;
  };

  recognition.onend = () => {
    console.log("🛑 Speech recognition ended");
    isListening = false;
    if (!isGenerating && !isSpeaking) {
      console.log("Restarting recognition...");
      startRecognition();
    }
  };

  recognition.start();
}


// Mic click starts fresh session
micBtn.addEventListener("click", () => {
  if (recognition) recognition.abort();
  isGenerating = false;
  isSpeaking = false;
  isListening = false;
  startRecognition();
});

let mediaRecorder;
let audioChunks = [];

const recordBtn = document.getElementById("record-btn");
const submitBtn = document.getElementById("submit-btn");
const statusText = document.getElementById("status");
const resultsBox = document.getElementById("results");
const transcriptionEl = document.getElementById("transcription");
const scoreEl = document.getElementById("score");
const feedbackEl = document.getElementById("feedback");

// Handle recording
recordBtn.onclick = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
    mediaRecorder.onstop = () => {
      submitBtn.disabled = false;
      statusText.textContent = "✅ Recording complete. Ready to analyze.";
    };

    mediaRecorder.start();
    statusText.textContent = "🎙️ Recording...";

    // Automatically stop after 3 seconds
    setTimeout(() => mediaRecorder.stop(), 3000);
  } catch (err) {
    statusText.textContent = "❌ Microphone access denied.";
    console.error(err);
  }
};

// Handle submission
submitBtn.onclick = async () => {
  const expectedText = document.getElementById("expected-text").value.trim();
  if (!expectedText) {
    statusText.textContent = "⚠️ Please enter the expected sentence.";
    return;
  }

  const blob = new Blob(audioChunks, { type: "audio/wav" });
  const formData = new FormData();
  formData.append("expected_text", expectedText);
  formData.append("audio", blob, "audio.wav");

  submitBtn.disabled = true;
  statusText.textContent = "⏳ Analyzing... Please wait...";

  try {
    const response = await fetch("https://effective-bassoon-97j55pxrvqx9fxxvq-8000.app.github.dev/analyze/", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const result = await response.json();
    transcriptionEl.textContent = result.transcription;
    scoreEl.textContent = `${result.score}%`;
    feedbackEl.textContent = result.feedback.length > 0 ? result.feedback.join(", ") : "✅ Great job!";

    resultsBox.classList.remove("hidden");
    statusText.textContent = "✅ Analysis complete!";
  } catch (err) {
    console.error(err);
    statusText.textContent = "❌ Submission error: " + err.message;
  } finally {
    submitBtn.disabled = false;
  }
};

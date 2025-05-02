let mediaRecorder;
let audioChunks = [];
let recordedBlob = null;

const recordBtn = document.getElementById("record-btn");
const submitBtn = document.getElementById("submit-btn");
const statusText = document.getElementById("status");

const transcriptionEl = document.getElementById("transcription");
const scoreEl = document.getElementById("score");
const feedbackEl = document.getElementById("feedback");

recordBtn.onclick = async () => {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);
  audioChunks = [];

  mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
  mediaRecorder.onstop = () => {
    recordedBlob = new Blob(audioChunks, { type: "audio/wav" });
    const audioUrl = URL.createObjectURL(recordedBlob);
    playback.src = audioUrl;
    playback.classList.remove("hidden");

    submitBtn.disabled = false;
    statusText.textContent = "🎧 Recording complete. Ready to submit.";
  };

  mediaRecorder.start();
  statusText.textContent = "🎙️ Recording... Speak now!";
  setTimeout(() => mediaRecorder.stop(), 3000);
};

submitBtn.onclick = async () => {
  const expectedText = document.getElementById("expected-text").value.trim();
  if (!expectedText) {
    statusText.textContent = "⚠️ Please enter the expected sentence.";
    return;
  }

  // const blob = new Blob(audioChunks, { type: "audio/wav" });
  const formData = new FormData();
  formData.append("audio", recordedBlob, "audio.wav");
  formData.append("expected_text", expectedText);
  // formData.append("audio", blob, "audio.wav");

  submitBtn.disabled = true;
  statusText.textContent = "⏳ Analyzing... Please wait...";

  try {
    const response = await fetch("https://literate-fortnight-v6qrrx594q5p26p7g-8000.app.github.dev/analyze/", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const result = await response.json();

    // 2. Extract and display feedback
    const transcription = result.transcription || "N/A";
    const score = result.score !== undefined ? `${result.score}%` : "N/A";
    const feedbackText = Array.isArray(result.feedback)
      ? result.feedback.join(", ")
      : result.feedback || "✅ Great job!";

    transcriptionEl.textContent = transcription;
    scoreEl.textContent = score;
    feedbackEl.textContent = feedbackText;

    // 3. Fetch audio feedback
    const ttsResponse = await fetch(`https://crispy-sniffle-r444g7754v9xcxw9p-8000.app.github.dev/tts/?text=${encodeURIComponent(feedbackText)}`);
    const ttsBlob = await ttsResponse.blob();
    const audioUrl = URL.createObjectURL(ttsBlob);
    new Audio(audioUrl).play();

    statusText.textContent = "✅ Analysis complete!";
  } catch (err) {
    console.error(err);
    statusText.textContent = "❌ Submission error: " + err.message;
  } finally {
    submitBtn.disabled = false;
  }
};

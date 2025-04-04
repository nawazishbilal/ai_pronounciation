let mediaRecorder;
let audioChunks = [];

window.onload = () => {
  const recordBtn = document.getElementById("record-btn");
  const submitBtn = document.getElementById("submit-btn");
  const statusText = document.getElementById("status-text");

  recordBtn.onclick = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      mediaRecorder = new MediaRecorder(stream);
      audioChunks = [];

      mediaRecorder.ondataavailable = (e) => {
        audioChunks.push(e.data);
      };

      mediaRecorder.onstop = () => {
        submitBtn.disabled = false;
        statusText.textContent = "🎧 Recording complete. Ready to submit.";
      };

      mediaRecorder.start();
      statusText.textContent = "🎙️ Recording for 3 seconds...";
      setTimeout(() => mediaRecorder.stop(), 3000);

    } catch (err) {
      console.error("Mic access error:", err);
      statusText.textContent = "❌ Mic access denied or not supported.";
    }
  };

  submitBtn.onclick = async () => {
    const blob = new Blob(audioChunks, { type: "audio/wav" });
    const formData = new FormData();
    formData.append("expected_text", document.getElementById("expected-text").value);
    formData.append("audio", blob, "audio.wav");

    statusText.textContent = "⏳ Analyzing...";
    console.log("Expected Text:", formData.get("expected_text"));
    console.log("Audio Blob:", formData.get("audio"));
    
    try {
      const response = await fetch("https://effective-bassoon-97j55pxrvqx9fxxvq-8000.app.github.dev/analyze/", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const result = await response.json();
      statusText.textContent = `✅ Score: ${result.score}%, Feedback: ${result.feedback.join(", ")}`;
    } catch (err) {
      console.error("Submission error:", err);
      statusText.textContent = "❌ Error during analysis. See console.";
    }
  };
};

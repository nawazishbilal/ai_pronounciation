# ai_pronounciation
A git library for the AI Powered Pronounciation Correction Bot

# 🗣️ AI-Powered Pronunciation Correction Web App

This project is an AI-powered web application that analyzes spoken audio and compares it to an expected sentence. It then returns a transcription, a pronunciation accuracy score, and phoneme-level feedback to help users improve their spoken English.

## ✨ Features

- 🎤 Real-time microphone recording from the browser
- 🧠 Wav2Vec2-based speech-to-text transcription (fine-tuned model)
- 🔍 Phoneme-level comparison using `phonemizer` and `eSpeak`
- 📊 Pronunciation scoring and feedback
- ⚡ FastAPI backend and Tailwind CSS frontend for clean UI
- 🚀 Deployed on GitHub Codespaces (or locally)

---

## 🖼️ Screenshot

![App Screenshot](https://via.placeholder.com/800x400?text=App+Interface+Screenshot)

---

## 🛠️ Tech Stack

### 🔙 Backend
- Python 3.10+
- FastAPI
- Hugging Face Transformers (`Wav2Vec2ForCTC`)
- Torch & torchaudio
- Phonemizer + eSpeak
- pydub & ffmpeg-python

### 🔜 Frontend
- HTML5 + Tailwind CSS
- Vanilla JavaScript (uses Web Audio API for recording)

---

## 📦 Requirements

Install Python dependencies:

```bash
pip install -r requirements.txt
```

In Windows, install eSpeak from the internet.

For Ubuntu first check for updates, then install espeak as follows:

```bash
sudo apt update
sudo apt install espeak
```

For Mac (Homebrew): 

```bash
brew install espeak
```
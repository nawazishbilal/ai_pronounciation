import torch
import torchaudio
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import re
from phonemizer import phonemize
from pydub import AudioSegment
import io
import difflib
import wave
import tempfile

device = torch.device("cpu")  # Force CPU use

# Load model and processor
processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-large-960h")
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-large-960h")
model.to(device)
model.eval()

def transcribe(audio_tensor, sample_rate):
    if sample_rate != 16000:
        resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
        audio_tensor = resampler(audio_tensor)

    input_values = processor(audio_tensor.squeeze(), return_tensors="pt", sampling_rate=16000).input_values
    input_values = input_values.to(device)

    with torch.no_grad():
        logits = model(input_values).logits

    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor.decode(predicted_ids[0])
    return transcription.lower()

def clean_text(text):
    return re.sub(r'[^\w\s]', '', text.lower())

def phonemize_text(text):
    return phonemize(text, language="en-us", backend="espeak", strip=True, preserve_punctuation=True)

def compare_phonemes(expected, actual):
    expected_seq = phonemize_text(clean_text(expected)).split()
    actual_seq = phonemize_text(clean_text(actual)).split()

    if not actual_seq:
        return 0, ["No transcription received."]

    matcher = difflib.SequenceMatcher(None, expected_seq, actual_seq)
    matches = sum(triple.size for triple in matcher.get_matching_blocks())
    total = len(expected_seq)
    score = round((matches / total) * 100, 2) if total > 0 else 0

    feedback = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != 'equal':
            feedback.append(f"Expected: {' '.join(expected_seq[i1:i2])}, Got: {' '.join(actual_seq[j1:j2])}")

    return score, feedback

def evaluate_pronunciation(audio_file, expected_text):
    # Read and load the audio
    audio_bytes = audio_file.read()
    audio_tensor, sample_rate = torchaudio.load(io.BytesIO(audio_bytes))

    # Convert stereo to mono if needed
    if audio_tensor.shape[0] > 1:
        audio_tensor = torch.mean(audio_tensor, dim=0, keepdim=True)

    # Transcribe and compare
    actual_transcription = transcribe(audio_tensor, sample_rate)
    score, feedback = compare_phonemes(expected_text, actual_transcription)

    return {
        "score": round(score, 2),
        "transcription": actual_transcription.lower(),
        "feedback": feedback if feedback else []
    }

def convert_to_wav(upload_file):
    audio = AudioSegment.from_file(upload_file)
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

    buffer = io.BytesIO()
    audio.export(buffer, format="wav")
    buffer.seek(0)
    return buffer
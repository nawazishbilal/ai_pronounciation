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

IPA_TO_PLAIN = {
    "oʊ": "oh", "əʊ": "oh", "aɪ": "eye", "aʊ": "ow", "eɪ": "ay", "ɔɪ": "oy",
    "ɪ": "ih", "iː": "ee", "i": "ee", "ʊ": "oo", "uː": "oo", "u": "oo",
    "e": "eh", "ɛ": "eh", "æ": "a", "ɑː": "ah", "ɑ": "ah", "ʌ": "uh", "ə": "uh",
    "ɜː": "er", "ɚ": "er", "ɝ": "er", "ʃ": "sh", "ʒ": "zh", "tʃ": "ch", "dʒ": "j",
    "ŋ": "ng", "θ": "th", "ð": "th", "h": "h", "b": "b", "p": "p", "d": "d",
    "t": "t", "g": "g", "k": "k", "z": "z", "s": "s", "v": "v", "f": "f",
    "m": "m", "n": "n", "l": "l", "r": "r", "w": "w", "j": "y", "ɹ": "r",
    "ː": "", "ˈ": "", "ˌ": "", "ʔ": "", " ": " "
}

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
    phonemes = phonemize(
        text,
        language="en-us",
        backend="espeak",  # or "segments"
        strip=True,
        preserve_punctuation=True,
        njobs=1  # avoid issues on Render/Codespaces
    )
    print(f"[PHONEMIZE] Input: {text} → Output: {phonemes}") #debugging line
    return phonemes

def compare_phonemes(expected, actual):
    expected_seq = phonemize_text(clean_text(expected)).split()
    actual_seq = phonemize_text(clean_text(actual)).split()

    print(f"[COMPARE] Expected Phonemes: {expected_seq}")
    print(f"[COMPARE] Actual Phonemes:   {actual_seq}")

    if not actual_seq:
        return 0, ["No transcription received."]

    matcher = difflib.SequenceMatcher(None, expected_seq, actual_seq)
    matches = sum(triple.size for triple in matcher.get_matching_blocks())
    total = len(expected_seq)
    score = round((matches / total) * 100, 2) if total > 0 else 0

    feedback = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != 'equal':
            expected_readable = readable_phonemes(' '.join(expected_seq[i1:i2]))
            actual_readable = readable_phonemes(' '.join(actual_seq[j1:j2]))
            feedback.append(f"Expected: {expected_readable}, Got: {actual_readable}")


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

def readable_phonemes(ipa_string):
    # Sort by descending key length to prioritize multi-char symbols (like "oʊ" before "o")
    for ipa, plain in sorted(IPA_TO_PLAIN.items(), key=lambda x: -len(x[0])):
        ipa_string = ipa_string.replace(ipa, plain)
    return ipa_string

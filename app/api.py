from fastapi import APIRouter, UploadFile, Form
from app.model import evaluate_pronunciation, convert_to_wav

router = APIRouter()

@router.post("/analyze/")
async def analyze(audio: UploadFile, expected_text: str = Form(...)):
    print("Received expected_text:", expected_text)
    print("Received audio filename:", audio.filename)
    wav_file = convert_to_wav(audio.file)
    result = evaluate_pronunciation(wav_file, expected_text)
    return result

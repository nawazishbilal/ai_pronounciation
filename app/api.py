from fastapi import APIRouter, UploadFile, Form, Query
from fastapi.responses import StreamingResponse
from app.model import evaluate_pronunciation, convert_to_wav
from gtts import gTTS
from io import BytesIO

router = APIRouter()

@router.post("/analyze/")
async def analyze(audio: UploadFile, expected_text: str = Form(...)):
    wav_file = convert_to_wav(audio.file)
    result = evaluate_pronunciation(wav_file, expected_text)

    feedback_text_raw = result.get("feedback", "Great job!")
    if isinstance(feedback_text_raw, list):
        feedback_text = " ".join(str(item) for item in feedback_text_raw)
    else:
        feedback_text = str(feedback_text_raw)

    return {
        "transcription": result.get("transcription", "N/A"),
        "score": result.get("score", None),
        "feedback": feedback_text
    }


@router.get("/tts/")
async def text_to_speech(text: str = Query(...)):
    mp3_fp = BytesIO()
    tts = gTTS(text)
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    return StreamingResponse(mp3_fp, media_type="audio/mpeg")

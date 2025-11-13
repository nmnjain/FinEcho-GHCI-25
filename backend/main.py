import whisper
from TTS.api import TTS
from fastapi import FastAPI, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import os
import json
from sqlalchemy.orm import Session
from pathlib import Path

# Import our package modules
from .nlu import get_dialogue_response
from .database import SessionLocal
from . import crud
from . import voice_auth

# --- INITIALIZATION ---
app = FastAPI(title="FinEcho API")
BASE_DIR = Path(__file__).resolve().parent
TEMP_DIR = BASE_DIR / "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

# --- MIDDLEWARE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Transcribed-Text", "X-Session-State", "X-Requires-Verification"]
)

# --- MODEL LOADING ---
print("Loading AI Models...")
asr_model = whisper.load_model("small.en")
tts_model = TTS(model_name="tts_models/en/ljspeech/vits", progress_bar=False)
print("Models loaded.")

# --- DATABASE DEPENDENCY ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API ENDPOINTS ---

@app.post("/enroll")
async def enroll_voice(audio_file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Enrolls a user's voice by creating and storing an embedding."""
    temp_audio_path = TEMP_DIR / audio_file.filename
    with open(temp_audio_path, "wb") as buffer:
        buffer.write(await audio_file.read())
    
    embedding = voice_auth.create_embedding(temp_audio_path)
    success = crud.save_voice_embedding(db, embedding)
    os.remove(temp_audio_path)

    if success:
        return JSONResponse(content={"status": "success", "message": "Voice enrolled successfully."})
    return JSONResponse(content={"status": "error", "message": "Failed to enroll voice."}, status_code=500)


@app.post("/converse")
async def converse_audio(
    session_state_str: str = Form(...),
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    session_state = json.loads(session_state_str)
    temp_audio_path = TEMP_DIR / audio_file.filename
    with open(temp_audio_path, "wb") as buffer:
        buffer.write(await audio_file.read())
        
    transcription_result = asr_model.transcribe(str(temp_audio_path), fp16=False)
    transcribed_text = transcription_result["text"].strip()
    
    response_text, updated_session_state, requires_verification = get_dialogue_response(session_state, transcribed_text, db)
    
    tts_output_path = TEMP_DIR / "response.wav"
    tts_model.tts_to_file(text=response_text, file_path=str(tts_output_path))
    os.remove(temp_audio_path)
    
    headers = {
        "X-Transcribed-Text": transcribed_text,
        "X-Session-State": json.dumps(updated_session_state),
        "X-Requires-Verification": "true" if requires_verification else "false"
    }
    
    return FileResponse(path=tts_output_path, headers=headers)


@app.post("/verify_and_execute")
async def verify_and_execute(
    session_state_str: str = Form(...),
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Verifies user's voice and executes the transaction if successful."""
    session_state = json.loads(session_state_str)
    
    temp_audio_path = TEMP_DIR / audio_file.filename
    with open(temp_audio_path, "wb") as buffer:
        buffer.write(await audio_file.read())
        
    # 1. Verify the voice
    new_embedding = voice_auth.create_embedding(temp_audio_path)
    stored_embedding_str = crud.get_user_voice_embedding(db)
    is_verified = voice_auth.verify_voice(new_embedding, stored_embedding_str)

    os.remove(temp_audio_path)
    
    # 2. Execute the transaction if verified
    if is_verified:
        slots = session_state.get("filled_slots", {})
        result = crud.execute_transfer(db, slots["amount"], slots["recipient"])
        response_text = result["message"]
    else:
        response_text = "Voice verification failed. Please try the transaction again."
        
    # 3. Generate TTS for the final result
    tts_output_path = TEMP_DIR / "response.wav"
    tts_model.tts_to_file(text=response_text, file_path=str(tts_output_path))
    
    headers = {
        "X-Transcribed-Text": "--- Verification Result ---",
        "X-Session-State": json.dumps({}) # Reset session state
    }
    
    return FileResponse(path=tts_output_path, headers=headers)
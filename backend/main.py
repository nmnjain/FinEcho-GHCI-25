import whisper
from TTS.api import TTS
# --- ADD `Form` TO THIS IMPORT ---
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import json

from nlu import get_dialogue_response

# --- INITIALIZATION ---
os.makedirs("temp", exist_ok=True)
app = FastAPI(title="FinEcho API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Transcribed-Text", "X-Session-State"]
)

print("Loading AI Models...")
asr_model = whisper.load_model("base.en")
tts_model = TTS(model_name="tts_models/en/ljspeech/vits", progress_bar=False)
print("Models loaded.")

sessions = {"user123": {}}

# --- THIS IS THE LINE TO CHANGE ---
@app.post("/converse")
async def converse_audio(session_state_str: str = Form(...), audio_file: UploadFile = File(...)):
    # The rest of the function remains the same
    session_state = json.loads(session_state_str)
    
    print(f"\nReceived audio file. Current session state: {session_state}")
    
    temp_audio_path = os.path.join("temp", audio_file.filename)
    with open(temp_audio_path, "wb") as buffer:
        buffer.write(await audio_file.read())
        
    print("Transcribing audio...")
    transcription_result = asr_model.transcribe(temp_audio_path, fp16=False)
    transcribed_text = transcription_result["text"].strip()
    print(f"Transcribed Text: {transcribed_text}")
    
    response_text, updated_session_state = get_dialogue_response(session_state, transcribed_text)
    print(f"Updated session state: {updated_session_state}")
    print(f"Response Text: {response_text}")
    
    print("Generating TTS response...")
    tts_output_path = os.path.join("temp", "response.wav")
    tts_model.tts_to_file(text=response_text, file_path=tts_output_path)
    print("TTS response generated.")
    
    os.remove(temp_audio_path)
    
    headers = {
        "X-Transcribed-Text": transcribed_text,
        "X-Session-State": json.dumps(updated_session_state)
    }
    
    return FileResponse(
        path=tts_output_path, 
        media_type="audio/wav", 
        filename="response.wav",
        headers=headers
    )
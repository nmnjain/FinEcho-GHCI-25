import whisper
import torchaudio
from TTS.api import TTS
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os

# --- INITIALIZATION ---

# Create a directory to store temporary files
os.makedirs("temp", exist_ok=True)

# Initialize FastAPI app
app = FastAPI(title="FinEcho API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load AI Models
# Using a smaller, faster model is ideal for a hackathon prototype.
print("Loading Whisper ASR model...")
asr_model = whisper.load_model("base.en") # Use "base.en" for English-only
print("ASR Model loaded.")

print("Loading Coqui TTS model...")
# This will download the model on the first run
tts_model = TTS(model_name="tts_models/en/ljspeech/vits", progress_bar=True)
print("TTS Model loaded.")


# --- API ENDPOINTS ---

@app.get("/")
def read_root():
    return {"status": "success", "message": "Welcome to the FinEcho Backend!"}

@app.post("/transcribe")
async def transcribe_audio(audio_file: UploadFile = File(...)):
    """
    This endpoint receives audio, transcribes it, and returns a TTS audio response.
    """
    print("Received audio file.")
    
    # 1. Save the uploaded audio file temporarily
    temp_audio_path = os.path.join("temp", audio_file.filename)
    with open(temp_audio_path, "wb") as buffer:
        buffer.write(await audio_file.read())
        
    # 2. Transcribe the audio using Whisper
    print("Transcribing audio...")
    transcription_result = asr_model.transcribe(temp_audio_path, fp16=False)
    transcribed_text = transcription_result["text"]
    print(f"Transcribed Text: {transcribed_text}")
    
    # --- For Phase 1, we use a fixed response ---
    response_text = "Hello, welcome to FinEcho. How can I assist you today?"
    
    # 3. Generate speech from the fixed response text using TTS
    print("Generating TTS response...")
    tts_output_path = os.path.join("temp", "response.wav")
    tts_model.tts_to_file(text=response_text, file_path=tts_output_path)
    print("TTS response generated.")
    
    # 4. Clean up the temporary input file
    os.remove(temp_audio_path)
    
    # 5. Return the generated audio file
    return FileResponse(path=tts_output_path, media_type="audio/wav", filename="response.wav")
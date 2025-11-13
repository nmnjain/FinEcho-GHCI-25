
from resemblyzer import VoiceEncoder, preprocess_wav
from pathlib import Path
import numpy as np
import json 

# Initialize the VoiceEncoder. This loads the model into memory.
encoder = VoiceEncoder()

VERIFICATION_THRESHOLD = 0.70 # Similarity score must be >= 80%

def create_embedding(wav_file_path: Path):
    """Creates a voice embedding from a WAV file."""
    wav = preprocess_wav(wav_file_path)
    embedding = encoder.embed_utterance(wav)
    return embedding

def verify_voice(new_embedding, stored_embedding_str: str):
    """
    Verifies a new voice embedding against a stored one.
    Returns True if the voices are similar, False otherwise.
    """
    if not stored_embedding_str:
        return False # No voice enrolled

    # Convert the stored JSON string back to a numpy array
    stored_embedding = np.array(json.loads(stored_embedding_str))
    
    # Calculate the similarity score
    similarity = np.inner(new_embedding, stored_embedding)
    
    print(f"Voice similarity score: {similarity:.2f}")
    
    return similarity >= VERIFICATION_THRESHOLD
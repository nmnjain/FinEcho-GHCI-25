import React, { useState } from 'react';
import axios from 'axios';
import { useReactMediaRecorder } from 'react-media-recorder';
import './App.css';

function App() {
  const [status, setStatus] = useState('idle');
  const [transcribedText, setTranscribedText] = useState('');
  const [audioPlayer, setAudioPlayer] = useState(null);

  // Hook for handling media recording
  const {
    startRecording,
    stopRecording,
    mediaBlobUrl,
  } = useReactMediaRecorder({ 
      audio: true, 
      onStop: handleStop,
      // Add this onError handler for debugging
      onError: (err) => console.error("react-media-recorder error:", err),
  });

  async function handleStop(blobUrl, blob) {
    console.log("Recording stopped. Blob available at:", blobUrl);
    setStatus('transcribing');
    setTranscribedText('...'); 

    const formData = new FormData();
    formData.append('audio_file', blob, 'recording.wav');

    try {
      console.log("Sending audio to backend...");
      const response = await axios.post('http://localhost:8000/transcribe', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        responseType: 'blob',
      });
      
      console.log("Received response from backend.");
      setTranscribedText("(User transcription will appear here in the next phase)");

      const audioUrl = URL.createObjectURL(response.data);
      const audio = new Audio(audioUrl);
      setAudioPlayer(audio);
      
      setStatus('playing');
      audio.play();
      
      audio.onended = () => {
        setStatus('idle');
      };

    } catch (error) {
      console.error('Error transcribing audio:', error);
      setStatus('idle');
    }
  }

  // A new function to wrap the start recording logic
  const handleStartRecording = () => {
    console.log("Start Recording button clicked.");
    try {
      setStatus('recording');
      startRecording();
      console.log("Recording process initiated.");
    } catch (err) {
      console.error("Error initiating recording:", err);
      setStatus('idle');
    }
  };

  return (
    <div className="container">
      <h1>FinEcho Voice Assistant</h1>
      <div className="status-box">
        <p>Status: <span>{status}</span></p>
      </div>
      <div className="button-container">
        <button
          onClick={handleStartRecording} // Use the new handler
          disabled={status === 'recording'}
          className="btn-start"
        >
          Start Recording
        </button>
        <button
          onClick={stopRecording}
          disabled={status !== 'recording'}
          className="btn-stop"
        >
          Stop Recording
        </button>
      </div>
      <div className="transcription-box">
        <h2>You Said:</h2>
        <p>{transcribedText || "..."}</p>
      </div>
    </div>
  );
}

export default App;
import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useReactMediaRecorder } from 'react-media-recorder';
import './App.css';

// --- A simple component for the enrollment section ---
function Enrollment({ onEnrollmentSuccess }) {
  const [status, setStatus] = useState('idle'); // idle, recording, processing

  const handleEnrollStop = async (blobUrl, blob) => {
    setStatus('processing');
    const formData = new FormData();
    formData.append('audio_file', blob, 'enrollment.wav');
    try {
      await axios.post('http://localhost:8000/enroll', formData);
      alert('Enrollment successful!');
      onEnrollmentSuccess();
    } catch (error) {
      alert('Enrollment failed. Please try again.');
      console.error(error);
    } finally {
      setStatus('idle');
    }
  };

  const { startRecording, stopRecording } = useReactMediaRecorder({ audio: true, onStop: handleEnrollStop });

  const handleRecordClick = () => {
    if (status === 'idle') {
      setStatus('recording');
      startRecording();
    } else if (status === 'recording') {
      stopRecording();
    }
  };

  return (
    <div className="enrollment-container">
      <h2>Voice Enrollment</h2>
      <p>Please record yourself saying: <strong>"My voice is my password for secure transactions."</strong></p>
      <button onClick={handleRecordClick} className={`record-button ${status}`}>
        {status === 'idle' && 'Start Enrollment Recording'}
        {status === 'recording' && 'Stop Recording'}
        {status ==='processing' && 'Processing...'}
      </button>
    </div>
  );
}


// --- Main App Component ---
function App() {
  const [status, setStatus] = useState('idle'); // idle, recording, processing, awaiting_verification
  const [messages, setMessages] = useState([]);
  const [sessionState, setSessionState] = useState({});
  const [showEnrollment, setShowEnrollment] = useState(true);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleNewMessage = (text, sender) => {
    setMessages(prev => [...prev, { text, sender }]);
  };

  const handleStopCallback = async (blobUrl, blob) => {
    setStatus('processing');
    
    let endpoint = 'http://localhost:8000/converse';
    // If we are in the verification step, call the verification endpoint instead
    if (status === 'awaiting_verification') {
      endpoint = 'http://localhost:8000/verify_and_execute';
    }

    const formData = new FormData();
    formData.append('session_state_str', JSON.stringify(sessionState));
    formData.append('audio_file', blob, 'recording.wav');

    try {
      const response = await axios.post(endpoint, formData, {
        responseType: 'blob',
      });

      const userText = response.headers['x-transcribed-text'];
      const updatedSession = JSON.parse(response.headers['x-session-state']);
      const requiresVerification = response.headers['x-requires-verification'] === 'true';

      handleNewMessage(userText, 'user');
      setSessionState(updatedSession);

      const audioUrl = URL.createObjectURL(response.data);
      const audio = new Audio(audioUrl);
      audio.play();

      handleNewMessage("...(Assistant's spoken response)", 'assistant');

      // Transition to the verification state if required
      if (requiresVerification) {
        setStatus('awaiting_verification');
      } else {
        setStatus('idle');
      }

    } catch (error) {
      console.error('Error in conversation:', error);
      handleNewMessage("Sorry, I encountered an error.", 'assistant');
      setStatus('idle');
    }
  };

  const { startRecording, stopRecording } = useReactMediaRecorder({
    audio: true,
    onStop: handleStopCallback,
  });

  const handleRecordClick = () => {
    if (status === 'idle' || status === 'awaiting_verification') {
      setStatus('recording');
      startRecording();
    } else if (status === 'recording') {
      stopRecording();
    }
  };
  
  const startNewConversation = () => {
    setMessages([]);
    setSessionState({});
    setStatus('idle');
  }

  if (showEnrollment) {
    return <Enrollment onEnrollmentSuccess={() => setShowEnrollment(false)} />;
  }

  return (
    <div className="chat-container">
      <div className="header">
        <h1>FinEcho Assistant</h1>
        <button onClick={startNewConversation} className="clear-button">New Chat</button>
      </div>
      <div className="message-list">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender}`}>
            {msg.text}
          </div>
        ))}
        {status === 'awaiting_verification' && (
          <div className="message assistant verification-prompt">
            Please speak the verification phrase now.
          </div>
        )}
        <div ref={chatEndRef} />
      </div>
      <div className="footer">
        <button onClick={handleRecordClick} className={`record-button ${status}`}>
          {status === 'idle' && 'Start Recording'}
          {status === 'recording' && 'Stop Recording'}
          {status === 'processing' && 'Processing...'}
          {status === 'awaiting_verification' && 'Record Verification Phrase'}
        </button>
      </div>
    </div>
  );
}

export default App;
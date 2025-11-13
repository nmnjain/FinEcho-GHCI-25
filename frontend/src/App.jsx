import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useReactMediaRecorder } from 'react-media-recorder';
import './App.css';

function App() {
  const [status, setStatus] = useState('idle'); // idle, recording, processing
  const [messages, setMessages] = useState([]); // Array to hold the conversation
  const [sessionState, setSessionState] = useState({}); // To hold conversation state
  const chatEndRef = useRef(null); // To auto-scroll chat

  // Auto-scroll to the latest message
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleNewMessage = (text, sender) => {
    setMessages(prev => [...prev, { text, sender }]);
  };

  async function handleStopCallback(blobUrl, blob) {
    setStatus('processing');
    const formData = new FormData();
    // Append session state as a string, because it's not a file
    formData.append('session_state_str', JSON.stringify(sessionState));
    formData.append('audio_file', blob, 'recording.wav');

    try {
      const response = await axios.post('http://localhost:8000/converse', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        responseType: 'blob',
      });

      const userText = response.headers['x-transcribed-text'];
      const updatedSession = JSON.parse(response.headers['x-session-state']);

      handleNewMessage(userText, 'user');
      setSessionState(updatedSession);

      const audioUrl = URL.createObjectURL(response.data);
      const audio = new Audio(audioUrl);
      audio.play();

      // We need the assistant's text response for the chat history
      // For now, we'll have to wait until Phase 6 (LLM) for the actual text.
      // Let's use a placeholder.
      // A better approach would be for the backend to return a JSON with both text and audio path.
      handleNewMessage("...(Assistant's spoken response)", 'assistant');

    } catch (error) {
      console.error('Error in conversation:', error);
      handleNewMessage("Sorry, I encountered an error.", 'assistant');
    } finally {
      setStatus('idle');
    }
  }

  const { startRecording, stopRecording } = useReactMediaRecorder({
    audio: true,
    onStop: handleStopCallback,
    onError: () => handleNewMessage("Recording failed. Please check microphone permissions.", 'assistant'),
  });

  const handleRecordClick = () => {
    if (status === 'idle') {
      // Only clear messages and state if it's the start of a brand new conversation
      if (messages.length === 0) {
        setSessionState({});
      }
      setStatus('recording');
      startRecording();
    } else if (status === 'recording') {
      stopRecording();
    }
  };

  const clearChat = () => {
    setMessages([]);
    setSessionState({});
}

  return (
    <div className="chat-container">
      <div className="header">
        <h1>FinEcho Assistant</h1>
      </div>
      <div className="message-list">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender}`}>
            {msg.text}
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>
      <div className="footer">
        <button onClick={handleRecordClick} className={`record-button ${status}`}>
          {status === 'idle' && 'Record'}
          {status === 'recording' && 'Stop'}
          {status === 'processing' && 'Processing...'}
        </button>
        <button onClick={clearChat} className="clear-button">Clear</button>
      </div>
    </div>
  );
}

export default App;
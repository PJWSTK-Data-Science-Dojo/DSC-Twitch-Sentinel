import { useEffect, useRef } from 'react';
import logo from './logo.svg';
import './App.css';
import { io } from 'socket.io-client';

function App() {
  const socketRef = useRef(null);
  useEffect(() => {
    // Initialize socket connection once when the component mounts
    window.Twitch.ext.onAuthorized((auth) => {
      // Create the WebSocket connection if it doesn't exist
      if (socketRef.current) {
        return;
      }
      socketRef.current = io(process.env.REACT_APP_BACKEND_URL, {
          transports: ['websocket'],
          rejectUnauthorized: false,
      });

      socketRef.current.on('connected', () => {
          console.log('Connected to server');
          socketRef.current.emit('stream_context', auth);
      });

      socketRef.current.on('disconnect', () => {
          console.log('Disconnected from server');
      });

      socketRef.current.on('message', (message) => {
          console.log('Received message:', message);
      });

      socketRef.current.on('data', (data) => {
        console.log('Received message:', data);
      });
    });
    
    return () => {
        socketRef.current.disconnect();
        socketRef.current = null;
    };
  }, []);
  
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>
    </div>
  );
}

export default App;

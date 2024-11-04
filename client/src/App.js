import { useEffect, useState, useRef } from 'react';
import './App.css';
import io from 'socket.io-client';

function App() {

  const [chatEntertainment, setChatEntertainment] = useState(1.0);
  const [isConnected, setIsConnected] = useState(false);
  const socket = useRef();

  useEffect(() => {

    socket.current = io(`http://${process.env.REACT_APP_BACKEND_URL}`, {
      transports: ['websocket'],
      path: '/sockets'
    });

    socket.current.on("connnection", () => {
      console.log("connected to server");
    });
    socket.current.on('connect', () => {
      setIsConnected(true);
    });

    socket.current.on('disconnect', () => {
      setIsConnected(socket.current.connected);
    });

    socket.current.on('data', (data) => {
      console.log('Received data:', data);
      let value = data.positive/(data.negative + data.positive);
      setChatEntertainment(value);
    });

    socket.current.on('disconnect', () => {
      socket.current.disconnect();
    });
    

    window.Twitch.ext.onAuthorized((auth) => {
      console.log('Auth:', auth);
      socket.current.emit('stream_context', auth);
    });

    return () => {
      socket.current.disconnect();
    };

  }, []);


  const [color, setColor] = useState('lightblue');

  function calcColor(value) {
    let r, g, b;
  
    if (value <= 0.5) {
      // Interpolate from blue (#0000FF) to yellow (#FFFF00)
      const ratio = value / 0.5;
      r = Math.round(255 * ratio);
      g = Math.round(255 * ratio);
      b = 255 - Math.round(255 * ratio);
    } else {
      // Interpolate from yellow (#FFFF00) to red (#FF0000)
      const ratio = (value - 0.5) / 0.5;
      r = 255;
      g = 255 - Math.round(255 * ratio);
      b = 0;
    }
    // r = Math.round(255 * value);
    // g = 22;
    // b = 22;
    return `rgb(${r}, ${g}, ${b})`;
  }

  useEffect(() => {
    console.log('Chat entertainment:', chatEntertainment);
    setColor(calcColor(chatEntertainment));
  }, [chatEntertainment]);

  return (
    <div className="App">
      <div className='main-body'>
      </div>
      <div className='chart-bar' style={{
        backgroundColor: color,
        height: `${chatEntertainment * 100}%`,
      }}></div>
    </div>
  );
}

export default App;

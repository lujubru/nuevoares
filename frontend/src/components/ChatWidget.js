import React, { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client';
import axios from 'axios';
import './ChatWidget.css';

const ChatWidget = ({ user }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [username, setUsername] = useState('');
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const messagesEndRef = useRef(null);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    // Conectar a Socket.IO
    const newSocket = io(backendUrl);
    setSocket(newSocket);

    newSocket.on('connect', () => {
      setIsConnected(true);
      console.log('Conectado al chat');
    });

    newSocket.on('disconnect', () => {
      setIsConnected(false);
      console.log('Desconectado del chat');
    });

    newSocket.on('new_message', (message) => {
      setMessages(prev => [...prev, message]);
    });

    newSocket.on('connected', (data) => {
      console.log(data.message);
    });

    return () => {
      newSocket.close();
    };
  }, [backendUrl]);

  useEffect(() => {
    // Cargar mensajes existentes cuando se abre el chat
    if (isOpen && messages.length === 0) {
      loadMessages();
    }
  }, [isOpen]);

  useEffect(() => {
    // Scroll automático al final
    scrollToBottom();
  }, [messages]);

  const loadMessages = async () => {
    try {
      const response = await axios.get(`${backendUrl}/api/chat/messages`);
      if (response.data.success) {
        setMessages(response.data.data);
      }
    } catch (error) {
      console.error('Error cargando mensajes:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!newMessage.trim()) return;

    if (user && user.is_admin) {
      // Admin enviando mensaje a través de la API
      try {
        const token = localStorage.getItem('token');
        await axios.post(
          `${backendUrl}/api/chat/send`,
          { message: newMessage },
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );
        setNewMessage('');
      } catch (error) {
        console.error('Error enviando mensaje:', error);
      }
    } else {
      // Usuario regular enviando mensaje a través de Socket.IO
      if (!username.trim()) {
        alert('Por favor ingresa tu nombre');
        return;
      }

      if (socket && isConnected) {
        socket.emit('user_message', {
          username: username,
          message: newMessage
        });
        setNewMessage('');
      }
    }
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  return (
    <>
      {/* Botón flotante del chat */}
      <div className={`chat-float ${isOpen ? 'open' : ''}`} onClick={toggleChat}>
        <div className="chat-icon">
          {isOpen ? '×' : '💬'}
        </div>
        {!isOpen && (
          <div className="chat-notification">
            <span>Chat de Soporte</span>
            {isConnected && <div className="online-indicator"></div>}
            }
          </div>
        )}
      </div>

      {/* Widget del chat */}
      {isOpen && (
        <div className="chat-widget">
          <div className="chat-header">
            <h3>Chat de Soporte Ares Club</h3>
            <div className="chat-status">
              <span className={`status-indicator ${isConnected ? 'online' : 'offline'}`}></span>
              {isConnected ? 'En línea' : 'Desconectado'}
            </div>
            <button className="chat-close" onClick={toggleChat}>×</button>
          </div>

          <div className="chat-messages">
            {messages.length === 0 ? (
              <div className="welcome-message">
                <p>¡Bienvenido al chat de soporte de Ares Club!</p>
                <p>Nuestro equipo está aquí para ayudarte.</p>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`message ${message.is_admin ? 'admin' : 'user'}`}
                >
                  <div className="message-header">
                    <span className="username">
                      {message.is_admin ? '👑 ' : '👤 '}
                      {message.username}
                    </span>
                    <span className="timestamp">
                      {new Date(message.created_at).toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="message-content">
                    {message.message}
                  </div>
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>

          <form className="chat-input-form" onSubmit={handleSendMessage}>
            {!user && (
              <input
                type="text"
                placeholder="Tu nombre..."
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="username-input"
                required
              />
            )}
            <div className="message-input-container">
              <input
                type="text"
                placeholder="Escribe tu mensaje..."
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                className="message-input"
                disabled={!isConnected}
                required
              />
              <button 
                type="submit" 
                className="send-button"
                disabled={!isConnected || !newMessage.trim()}
              >
                📤
              </button>
            </div>
          </form>
        </div>
      )}
    </>
  );
};

export default ChatWidget;
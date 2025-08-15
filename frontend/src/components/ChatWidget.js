import React, { useState, useEffect, useRef, useCallback } from 'react';
import io from 'socket.io-client';
import axios from 'axios';
import './ChatWidget.css';

const ChatWidget = ({ user }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [chatRooms, setChatRooms] = useState([]);
  const [activeRoom, setActiveRoom] = useState(null);
  const [newMessage, setNewMessage] = useState('');
  const [username, setUsername] = useState('');
  const [roomId, setRoomId] = useState(null);
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const messagesEndRef = useRef(null);

  const backendUrl = (process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001').replace(/\/$/, '');

  const loadMessages = useCallback(async () => {
    if (!activeRoom) return;
    try {
      const response = await axios.get(`${backendUrl}/api/chat/messages/${activeRoom}`);
      if (response.data.success) {
        setMessages(response.data.data);
      }
    } catch (error) {
      console.error('Error cargando mensajes:', error);
    }
  }, [backendUrl, activeRoom]);

  const loadChatRooms = useCallback(async () => {
    if (!user || !user.is_admin) return;
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${backendUrl}/api/chat/rooms`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data.success) {
        setChatRooms(response.data.data);
        console.log('Chat rooms cargadas:', response.data.data.length);
      }
    } catch (error) {
      console.error('Error cargando salas de chat:', error);
    }
  }, [backendUrl, user]);

  // Conexión al socket (solo una vez)
  useEffect(() => {
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
      console.log('Nuevo mensaje recibido:', message);
      // Solo mostrar si es la sala activa o si no hay sala activa seleccionada
      if (!activeRoom || message.room_id === activeRoom) {
        setMessages(prev => [...prev, message]);
      }
    });

    newSocket.on('room_joined', (data) => {
      setRoomId(data.room_id);
      console.log('Unido a sala:', data.room_id);
    });

    newSocket.on('new_user_message', (notification) => {
      console.log('Nueva notificación de usuario:', notification);
      if (user && user.is_admin) {
        loadChatRooms();
      }
    });

    newSocket.on('admin_joined', (data) => {
      console.log(`Admin unido a sala: ${data.room_id}`);
    });

    return () => {
      newSocket.close();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [backendUrl]); // solo se ejecuta al iniciar

  // Unirse a la sala de admins si aplica
  useEffect(() => {
    if (socket && isConnected && user && user.is_admin) {
      socket.emit('join_admins', {});
      loadChatRooms();
      console.log('Admin conectado - cargando salas');
    }
  }, [socket, isConnected, user, loadChatRooms]);

  // Para usuarios regulares: unirse automáticamente
  useEffect(() => {
    if (socket && isConnected && username && !user) {
      socket.emit('join_room', { username });
      console.log('Usuario regular conectándose con username:', username);
    }
  }, [socket, isConnected, username, user]);

  // Cargar mensajes al abrir chat y seleccionar sala
  useEffect(() => {
    if (isOpen && activeRoom) {
      loadMessages();
    }
  }, [isOpen, activeRoom, loadMessages]);

  // Scroll automático al final
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    if (user && user.is_admin) {
      if (!activeRoom) {
        alert('Selecciona una conversación primero');
        return;
      }
      try {
        const token = localStorage.getItem('token');
        await axios.post(
          `${backendUrl}/api/chat/send`,
          { message: newMessage, room_id: activeRoom },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        setNewMessage('');
      } catch (error) {
        console.error('Error enviando mensaje:', error);
      }
    } else {
      if (!username.trim()) {
        alert('Por favor ingresa tu nombre');
        return;
      }
      if (socket && isConnected) {
        console.log('Enviando mensaje del usuario:', { username, message: newMessage, room_id: roomId });
        socket.emit('user_message', {
          username,
          message: newMessage,
          room_id: roomId
        });
        setNewMessage('');
      }
    }
  };

  const selectRoom = (room) => {
    setActiveRoom(room.room_id);
    setMessages([]);
    if (socket && user && user.is_admin) {
      socket.emit('admin_join_room', { room_id: room.room_id });
      console.log('Admin seleccionó sala:', room.room_id);
    }
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
    if (!isOpen && user && user.is_admin) {
      // Recargar salas cuando el admin abre el chat
      loadChatRooms();
    }
  };

  return (
    <>
      {/* Botón flotante */}
      <div className={`chat-float ${isOpen ? 'open' : ''}`} onClick={toggleChat}>
        <div className="chat-icon">{isOpen ? '×' : '💬'}</div>
        {!isOpen && (
          <div className="chat-notification">
            <span>Chat de Soporte</span>
            {isConnected && <div className="online-indicator"></div>}
          </div>
        )}
      </div>

      {/* Widget */}
      {isOpen && (
        <div className="chat-widget">
          <div className="chat-header">
            <h3>
              {user && user.is_admin
                ? (activeRoom ? `Chat: ${chatRooms.find(r => r.room_id === activeRoom)?.username || 'Usuario'}` : 'Panel de Chat Admin')
                : 'Chat de Soporte Ares Club'}
            </h3>
            <div className="chat-status">
              <span className={`status-indicator ${isConnected ? 'online' : 'offline'}`}></span>
              {isConnected ? 'En línea' : 'Desconectado'}
            </div>
            <button className="chat-close" onClick={toggleChat}>×</button>
          </div>

          {user && user.is_admin ? (
            <div className="admin-chat-container">
              {!activeRoom ? (
                <div className="chat-rooms-list">
                  <h4>Conversaciones Activas ({chatRooms.length})</h4>
                  {chatRooms.length === 0 ? (
                    <div className="no-rooms">
                      <p>No hay conversaciones activas</p>
                      <p style={{fontSize: '0.8rem', color: '#888', marginTop: '1rem'}}>
                        Las conversaciones aparecerán aquí cuando los usuarios escriban mensajes
                      </p>
                    </div>
                  ) : (
                    chatRooms.map((room) => (
                      <div key={room.room_id} className="room-item" onClick={() => selectRoom(room)}>
                        <div className="room-header">
                          <span className="room-username">👤 {room.username}</span>
                          {room.unread_count > 0 && (
                            <span className="unread-badge">{room.unread_count}</span>
                          )}
                        </div>
                        <div className="room-last-message">{room.last_message}</div>
                        <div className="room-time">
                          {new Date(room.last_message_time).toLocaleString()}
                        </div>
                      </div>
                    ))
                  )}
                  <button 
                    onClick={loadChatRooms}
                    style={{
                      background: 'rgba(204, 0, 0, 0.2)',
                      border: '1px solid rgba(204, 0, 0, 0.5)',
                      color: 'white',
                      padding: '0.5rem 1rem',
                      borderRadius: '5px',
                      cursor: 'pointer',
                      marginTop: '1rem',
                      width: '100%'
                    }}
                  >
                    🔄 Actualizar conversaciones
                  </button>
                </div>
              ) : (
                <div className="chat-conversation">
                  <div className="conversation-header">
                    <button className="back-button" onClick={() => setActiveRoom(null)}>← Volver</button>
                  </div>
                  <div className="chat-messages">
                    {messages.length === 0 ? (
                      <div className="welcome-message">
                        <p>Conversación con {chatRooms.find(r => r.room_id === activeRoom)?.username}</p>
                        <p style={{fontSize: '0.8rem', color: '#888'}}>Los mensajes aparecerán aquí</p>
                      </div>
                    ) : (
                      messages.map((message) => (
                        <div key={message.id} className={`message ${message.is_admin ? 'admin' : 'user'}`}>
                          <div className="message-header">
                            <span className="username">
                              {message.is_admin ? '👑 ' : '👤 '}
                              {message.username}
                            </span>
                            <span className="timestamp">
                              {new Date(message.created_at).toLocaleTimeString()}
                            </span>
                          </div>
                          <div className="message-content">{message.message}</div>
                        </div>
                      ))
                    )}
                    <div ref={messagesEndRef} />
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="chat-messages">
              {messages.length === 0 ? (
                <div className="welcome-message">
                  <p>¡Bienvenido al chat de soporte de Ares Club!</p>
                  <p>Nuestro equipo está aquí para ayudarte.</p>
                  <p style={{fontSize: '0.8rem', color: '#888', marginTop: '1rem'}}>
                    Conexión: {isConnected ? '🟢 Conectado' : '🔴 Desconectado'}
                  </p>
                </div>
              ) : (
                messages.map((message) => (
                  <div key={message.id} className={`message ${message.is_admin ? 'admin' : 'user'}`}>
                    <div className="message-header">
                      <span className="username">
                        {message.is_admin ? '👑 ' : '👤 '}
                        {message.username}
                      </span>
                      <span className="timestamp">
                        {new Date(message.created_at).toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="message-content">{message.message}</div>
                  </div>
                ))
              )}
              <div ref={messagesEndRef} />
            </div>
          )}

          {(!user || (user.is_admin && activeRoom)) && (
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
                <button type="submit" className="send-button" disabled={!isConnected || !newMessage.trim()}>
                  📤
                </button>
              </div>
            </form>
          )}
        </div>
      )}
    </>
  );
};

export default ChatWidget;

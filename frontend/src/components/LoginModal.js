import React, { useState } from 'react';
import axios from 'axios';
import './LoginModal.css';

const LoginModal = ({ isOpen, onClose, onLogin }) => {
  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${backendUrl}/api/auth/login`, credentials);
      
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        onLogin(response.data.user);
        onClose();
        setCredentials({ username: '', password: '' });
      }
    } catch (error) {
      setError(error.response?.data?.detail || 'Error al iniciar sesión');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setCredentials({
      ...credentials,
      [e.target.name]: e.target.value
    });
  };

  if (!isOpen) return null;

  return (
    <div className="login-modal-overlay">
      <div className="login-modal">
        <div className="login-modal-header">
          <h2>Iniciar Sesión - Admin</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <form onSubmit={handleSubmit} className="login-form">
          {error && <div className="error-message">{error}</div>}
          }
          
          <div className="form-group">
            <label htmlFor="username">Usuario:</label>
            <input
              type="text"
              id="username"
              name="username"
              value={credentials.username}
              onChange={handleChange}
              required
              placeholder="Ingresa tu usuario"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="password">Contraseña:</label>
            <input
              type="password"
              id="password"
              name="password"
              value={credentials.password}
              onChange={handleChange}
              required
              placeholder="Ingresa tu contraseña"
            />
          </div>
          
          <button 
            type="submit" 
            className="login-button"
            disabled={loading}
          >
            {loading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
          </button>
        </form>
        
        <div className="login-info">
          <p><strong>Usuario por defecto:</strong> admin</p>
          <p><strong>Contraseña:</strong> admin123</p>
        </div>
      </div>
    </div>
  );
};

export default LoginModal;
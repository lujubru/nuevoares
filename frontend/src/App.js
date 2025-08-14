import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

// Hook para Meta Pixel events
const useMetaPixel = () => {
  const trackEvent = (eventName, parameters = {}) => {
    if (window.fbq) {
      window.fbq('track', eventName, parameters);
      console.log(`Meta Pixel Event: ${eventName}`, parameters);
    }
  };

  return { trackEvent };
};

function App() {
  const [games, setGames] = useState([]);
  const [promotions, setPromotions] = useState([]);
  const [paymentMethods, setPaymentMethods] = useState([]);
  const [faq, setFaq] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentSlide, setCurrentSlide] = useState(0);
  
  const { trackEvent } = useMetaPixel();
  
  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
  
  // Imágenes del carousel
  const carouselImages = [
    '/static/images/fondo1.png',
    '/static/images/fondo2.png',
    '/static/images/fondo3.png',
    '/static/images/fondo4.png'
  ];

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [gamesRes, promotionsRes, paymentRes, faqRes] = await Promise.all([
          axios.get(`${backendUrl}/api/games`),
          axios.get(`${backendUrl}/api/promotions`),
          axios.get(`${backendUrl}/api/payment-methods`),
          axios.get(`${backendUrl}/api/faq`)
        ]);
        
        setGames(gamesRes.data.data || []);
        setPromotions(promotionsRes.data.data || []);
        setPaymentMethods(paymentRes.data.data || []);
        setFaq(faqRes.data.data || []);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [backendUrl]);

  // Carousel automático
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % carouselImages.length);
    }, 5000);
    
    return () => clearInterval(interval);
  }, [carouselImages.length]);

  const handleWhatsAppClick = (action = 'Contact') => {
    trackEvent(action);
    window.open('https://wa.me/5491178419956?text=Hola!%20Buenas!!%20vengo%20por%20mi%20usuario%20de%20la%20suerte%20🍀', '_blank');
  };

  const handleGameClick = (gameName) => {
    trackEvent('Lead', { game: gameName });
    handleWhatsAppClick('Lead');
  };

  const handleBonusClick = (bonusName) => {
    trackEvent('Lead', { bonus: bonusName });
    handleWhatsAppClick('Lead');
  };

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner"></div>
        <h2>Cargando Ares Club...</h2>
      </div>
    );
  }

  return (
    <div className="App">
      {/* Header */}
      <header className="header">
        <nav className="nav container">
          <div className="logo">
            <img src="/static/images/ares.png" alt="Ares Club Logo" />
          </div>
          <ul className="nav-links">
            <li><a href="#inicio">Inicio</a></li>
            <li><a href="#juegos">Juegos</a></li>
            <li><a href="#bonos">Bonos</a></li>
            <li><a href="#contacto" onClick={() => handleWhatsAppClick()}>Contacto</a></li>
          </ul>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="hero" id="inicio">
        <div className="carousel-container">
          {carouselImages.map((image, index) => (
            <div
              key={index}
              className={`carousel-slide ${index === currentSlide ? 'active' : ''}`}
              style={{ backgroundImage: `url(${image})` }}
            />
          ))}
        </div>
        <div className="container hero-content">
          <h1>Bienvenido a Ares Club</h1>
          <p>La experiencia de casino más emocionante te espera</p>
          <button 
            className="cta-button"
            onClick={() => handleWhatsAppClick('Lead')}
          >
            ¡Crea tu Usuario Ahora!
          </button>
        </div>
      </section>

      {/* WhatsApp Flotante */}
      <div className="whatsapp-float" onClick={() => handleWhatsAppClick()}>
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="currentColor" viewBox="0 0 16 16">
          <path d="M13.601 2.326A7.85 7.85 0 0 0 7.994 0C3.627 0 .068 3.558.064 7.926c0 1.399.366 2.76 1.057 3.965L0 16l4.204-1.102a7.9 7.9 0 0 0 3.79.965h.004c4.368 0 7.926-3.558 7.93-7.93A7.9 7.9 0 0 0 13.6 2.326zM7.994 14.521a6.6 6.6 0 0 1-3.356-.92l-.24-.144-2.494.654.666-2.433-.156-.251a6.56 6.56 0 0 1-1.007-3.505c0-3.626 2.957-6.584 6.591-6.584a6.56 6.56 0 0 1 4.66 1.931 6.56 6.56 0 0 1 1.928 4.66c-.004 3.639-2.961 6.592-6.592 6.592m3.615-4.934c-.197-.099-1.17-.578-1.353-.646-.182-.065-.315-.099-.445.099-.133.197-.513.646-.627.775-.114.133-.232.148-.43.05-.197-.1-.836-.308-1.592-.985-.59-.525-.985-1.175-1.103-1.372-.114-.198-.011-.304.088-.403.087-.088.197-.232.296-.346.1-.114.133-.198.198-.33.065-.134.034-.248-.015-.347-.05-.099-.445-1.076-.612-1.47-.16-.389-.323-.335-.445-.34-.114-.007-.247-.007-.38-.007a.73.73 0 0 0-.529.247c-.182.198-.691.677-.691 1.654s.71 1.916.81 2.049c.098.133 1.394 2.132 3.383 2.992.47.205.84.326 1.129.418.475.152.904.129 1.246.08.38-.058 1.171-.48 1.338-.943.164-.464.164-.86.114-.943-.049-.084-.182-.133-.38-.232"/>
        </svg>
      </div>

      {/* Bienvenida */}
      <section className="section">
        <div className="container">
          <h2 className="section-title">Bienvenido a la emoción de Ares Club</h2>
          <div className="text-content">
            <p><span className="highlight">Ares Club</span> es una plataforma de juegos en línea que ofrece una experiencia de casino emocionante y atractiva. Como un sitio de confianza, Ares Club proporciona una amplia variedad de juegos tragamonedas, todo impulsado por proveedores de software líderes en la industria.</p>
            
            <p>Ya seas un jugador ocasional o un apostador experimentado, <span className="highlight">Ares Club</span> tiene algo para todos con su diversa gama de opciones de juego. El sitio, conocido por su navegación fluida y su interfaz amigable, tiene como objetivo ofrecer a los jugadores una experiencia de juego excepcional y segura.</p>
            
            <p>La plataforma ofrece una experiencia de juego emocionante y diversa, adaptándose a las preferencias de todos los jugadores. Con una amplia variedad de juegos y bonos atractivos, <span className="highlight">Ares Club</span> se está convirtiendo rápidamente en una opción popular para los entusiastas del juego en línea.</p>
          </div>
        </div>
      </section>

      {/* Seguridad */}
      <section className="section">
        <div className="container">
          <h2 className="section-title">Seguridad y Confianza</h2>
          <div className="text-content">
            <p>En <span className="highlight">Ares Club</span>, la seguridad es una de las principales prioridades para garantizar una experiencia segura y agradable para todos los jugadores. El sitio opera bajo una licencia válida emitida por las autoridades de Curazao, Antillas Neerlandesas, ofreciendo un entorno seguro y regulado para el juego.</p>
            
            <p>Toda la información personal y financiera compartida con <span className="highlight">Ares Club</span> está protegida mediante las últimas tecnologías de cifrado, asegurando que tus datos estén siempre a salvo. La plataforma cumple con estrictos estándares de la industria para ofrecer una experiencia de juego justa.</p>
            
            <p>El equipo de <span className="highlight">Ares Club</span> asegura que todas las transacciones sean seguras y utiliza medidas de seguridad avanzadas para proteger la privacidad y los fondos de los jugadores.</p>
          </div>
        </div>
      </section>

      {/* Juegos Destacados */}
      <section className="section" id="juegos">
        <div className="container">
          <h2 className="section-title">Juegos Destacados</h2>
          <div className="games-grid">
            {games.map((game) => (
              <div key={game.id} className="game-card">
                <div className="game-image">
                  <img src={game.image} alt={`Captura del juego ${game.name}`} />
                </div>
                <h3>{game.name} - {game.provider}</h3>
                <button 
                  className="cta-button"
                  onClick={() => handleGameClick(game.name)}
                >
                  Jugar Ahora
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Bonos y Promociones */}
      <section className="section" id="bonos">
        <div className="container">
          <h2 className="section-title">Bonos y Promociones</h2>
          <div className="text-content">
            <p>En <span className="highlight">nuestra plataforma</span>, los jugadores pueden disfrutar de emocionantes bonos y promociones que mejoran su experiencia de juego. Ya seas un jugador nuevo o experimentado, la plataforma asegura que siempre haya una oferta que se ajuste a tu estilo.</p>
          </div>
          <div className="features">
            {promotions.map((promo) => (
              <div key={promo.id} className="feature">
                <h3>{promo.title}</h3>
                <p>{promo.description}</p>
                <button 
                  className="cta-button"
                  onClick={() => handleBonusClick(promo.title)}
                >
                  {promo.type === 'welcome_bonus' ? 'Reclamar' : 'Ver Eventos'}
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Métodos de Pago */}
      <section className="section">
        <div className="container">
          <h2 className="section-title">Métodos de Pago</h2>
          <div className="text-content">
            <p>En <span className="highlight">Ares</span>, los jugadores cuentan con una variedad de opciones de pago convenientes para garantizar un proceso de transacciones seguro y ágil.</p>
          </div>
          <div className="payment-methods">
            {paymentMethods.map((method, index) => (
              <div key={index} className="payment-method">
                {method.name}
              </div>
            ))}
          </div>
          <div className="text-content">
            <p>Los ewallets están ganando cada vez más popularidad para transacciones en línea, y la plataforma se asegura de que tengas acceso a estos métodos modernos de pago. Disfrutarás de pagos rápidos, seguros y convenientes sin retrasos.</p>
          </div>
        </div>
      </section>

      {/* Experiencia Móvil */}
      <section className="section">
        <div className="container">
          <h2 className="section-title">Experiencia Móvil</h2>
          <div className="text-content">
            <p>Para los jugadores que buscan una forma dinámica y conveniente de disfrutar de los juegos en línea, <span className="highlight">Ares</span> ofrece una experiencia de apuestas móviles sin interrupciones en múltiples dispositivos.</p>
            
            <p>Ya sea en casa o mientras estás en movimiento, puedes disfrutar de todas las características y juegos disponibles en la versión de escritorio, optimizados para jugar desde el móvil. La plataforma está diseñada para funcionar de manera eficiente en varios sistemas operativos.</p>
            
            <p>No importa el dispositivo, <span className="highlight">Ares</span> garantiza una interfaz rica y fácil de usar. Esta flexibilidad asegura que los jugadores puedan acceder al Ares Club desde prácticamente cualquier lugar, en cualquier momento.</p>
          </div>
        </div>
      </section>

      {/* Soporte al Cliente */}
      <section className="section" id="contacto">
        <div className="container">
          <h2 className="section-title">Soporte al Cliente</h2>
          <div className="text-content">
            <p>En <span className="highlight">Ares Club</span>, damos prioridad a ofrecer una asistencia fluida para todos los jugadores, asegurando que su experiencia sea agradable y sin inconvenientes. Nuestro equipo de soporte está disponible para ayudarte con cualquier pregunta o problema que puedas encontrar.</p>
            
            <p>Para contactarnos, puedes usar nuestra función de <span className="highlight">chat en vivo</span> de la plataforma, disponible las 24 horas del día, los 7 días de la semana, para asistencia inmediata. También puedes ponerte en contacto con nosotros por correo electrónico o explorar nuestra extensa sección de preguntas frecuentes.</p>
          </div>
          <div style={{textAlign: 'center', marginTop: '2rem'}}>
            <button 
              className="cta-button"
              onClick={() => handleWhatsAppClick()}
            >
              Contactar Soporte
            </button>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="section">
        <div className="container">
          <h2 className="section-title">Preguntas Frecuentes</h2>
          <div className="features">
            {faq.map((item, index) => (
              <div key={index} className="feature">
                <h3>{item.question}</h3>
                <p>{item.answer}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Conclusión */}
      <section className="section">
        <div className="container">
          <h2 className="section-title">Conclusión</h2>
          <div className="text-content">
            <p>En conclusión, <span className="highlight">Ares Club</span> ofrece una experiencia de juego en línea de alta calidad con una amplia variedad de juegos, bonificaciones y opciones de pago seguras. Los jugadores que buscan una plataforma confiable y divertida encontrarán en Ares Club una excelente opción.</p>
            
            <p>El sitio ofrece diversas características diseñadas para mejorar tu experiencia de juego, ya seas nuevo en los casinos en línea o un jugador experimentado. En <span className="highlight">Ares Club</span>, encontrarás una interfaz fácil de usar, lo que facilita la navegación por las diferentes secciones.</p>
            
            <p>El compromiso del sitio de ofrecer juegos de alta calidad de proveedores reconocidos asegura que todos los jugadores puedan disfrutar de una experiencia emocionante, tambien de como jugar. Además, <span className="highlight">Ares Club</span> ofrece una amplia gama de promociones, lo que añade emoción adicional a tu juego.</p>
          </div>
          <div style={{textAlign: 'center', marginTop: '3rem'}}>
            <button 
              className="cta-button"
              onClick={() => handleWhatsAppClick('Lead')}
            >
              ¡Únite Ahora a Ares Club!
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-links">
            <a href="/terminos.html">Términos y Condiciones</a>
            <a href="/privacidad.html">Política de Privacidad</a>
            <a href="/juego-responsable.html">Juego Responsable</a>
            <a href="#contacto" onClick={() => handleWhatsAppClick()}>Contacto</a>
            <a href="/ayuda.html">Ayuda</a>
          </div>
          <div className="contact-box">
            <p>Contactanos por correo o WhatsApp:</p>
            <p><strong>Correo:</strong> aresclub.net@gmail.com</p>
            <p><strong>WhatsApp:</strong> <a href="https://wa.me/5491178419956" target="_blank" rel="noopener noreferrer">+54 9 11 7841 9956</a></p>
          </div>
          
          <p>&copy; Ares Club™. Todos los derechos reservados.</p>
          <p>Sitio web oficial para Argentina. Juega responsablemente. +18</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import desc, text, func
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import Optional
import jwt
from datetime import timedelta
import socketio

from database import get_db, create_tables, check_db_connection, Contact, GameInteraction, PromoInteraction, User, ChatMessage, authenticate_user

# Cargar variables de entorno
load_dotenv()

app = FastAPI(title="Ares Club Casino API", version="1.0.0")

# Configuración JWT
SECRET_KEY = os.getenv("SECRET_KEY", "ares-club-secret-key-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuración Socket.IO
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=True
)

# Crear la aplicación ASGI con Socket.IO
socket_app = socketio.ASGIApp(sio, app)

# Security
security = HTTPBearer()

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Crear tablas al iniciar
@app.on_event("startup")
async def startup_event():
    print("🚀 Iniciando Ares Club Casino API...")
    if check_db_connection():
        print("✅ Conexión a PostgreSQL exitosa")
        create_tables()
        print("✅ Tablas creadas/verificadas")
    else:
        print("❌ Error conectando a PostgreSQL")

# Juegos disponibles
GAMES = [
    {
        "id": 1,
        "name": "Volcano Rising",
        "provider": "RubyPlay",
        "image": "https://images.pexels.com/photos/2258536/pexels-photo-2258536.jpeg?auto=compress&cs=tinysrgb&w=400",
        "category": "slots",
        "description": "Una aventura volcánica llena de premios ardientes"
    },
    {
        "id": 2,
        "name": "Sweet Bonanza 1000",
        "provider": "Pragmatic Play",
        "image": "https://images.pexels.com/photos/1191710/pexels-photo-1191710.jpeg?auto=compress&cs=tinysrgb&w=400",
        "category": "slots",
        "description": "Dulces premios te esperan en esta deliciosa tragamonedas"
    },
    {
        "id": 3,
        "name": "Reactoonz",
        "provider": "Play n' Go",
        "image": "https://images.pexels.com/photos/163064/play-stone-network-networked-interactive-163064.jpeg?auto=compress&cs=tinysrgb&w=400",
        "category": "slots",
        "description": "Alienígenas divertidos con grandes multiplicadores"
    },
    {
        "id": 4,
        "name": "Book of Dead",
        "provider": "Play n' Go",
        "image": "https://images.pexels.com/photos/256541/pexels-photo-256541.jpeg?auto=compress&cs=tinysrgb&w=400",
        "category": "slots",
        "description": "Explora el antiguo Egipto en busca de tesoros"
    },
    {
        "id": 5,
        "name": "Zeus Rush Fever Deluxe",
        "provider": "RubyPlay",
        "image": "https://images.pexels.com/photos/2258536/pexels-photo-2258536.jpeg?auto=compress&cs=tinysrgb&w=400",
        "category": "slots",
        "description": "El poder de Zeus en tus manos para grandes premios"
    },
    {
        "id": 6,
        "name": "Wolf Gold",
        "provider": "Pragmatic Play",
        "image": "https://images.pexels.com/photos/1118873/pexels-photo-1118873.jpeg?auto=compress&cs=tinysrgb&w=400",
        "category": "slots",
        "description": "Caza junto a los lobos por el oro más preciado"
    }
]

# Promociones y bonos
PROMOTIONS = [
    {
        "id": 1,
        "title": "Bono de Bienvenida",
        "description": "Los nuevos jugadores son recibidos con un bono del 20% más en tu primer carga!",
        "type": "welcome_bonus",
        "percentage": 20,
        "active": True
    },
    {
        "id": 2,
        "title": "Eventos Especiales",
        "description": "Participa en eventos especiales donde puedes ganar recompensas y premios exclusivos.",
        "type": "special_events",
        "active": True
    }
]

# Métodos de pago
PAYMENT_METHODS = [
    {"name": "Visa", "type": "card", "icon": "💳", "image": "https://images.pexels.com/photos/164501/pexels-photo-164501.jpeg?auto=compress&cs=tinysrgb&w=200"},
    {"name": "Mastercard", "type": "card", "icon": "💳", "image": "https://images.pexels.com/photos/164501/pexels-photo-164501.jpeg?auto=compress&cs=tinysrgb&w=200"},
    {"name": "Transferencia Bancaria", "type": "bank", "icon": "🏦", "image": "https://images.pexels.com/photos/259027/pexels-photo-259027.jpeg?auto=compress&cs=tinysrgb&w=200"},
    {"name": "E-Wallets", "type": "ewallet", "icon": "📱", "image": "https://images.pexels.com/photos/4386321/pexels-photo-4386321.jpeg?auto=compress&cs=tinysrgb&w=200"}
]

# Funciones de autenticación
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(db: Session = Depends(get_db), username: str = Depends(verify_token)):
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.get("/")
async def root():
    return {
        "message": "Bienvenido a Ares Club Casino API",
        "version": "2.0.0",
        "database": "PostgreSQL",
        "status": "active"
    }

@app.get("/api/health")
async def health_check(db: Session = Depends(get_db)):
    """Verificar estado de la API y base de datos"""
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")

@app.get("/api/games")
async def get_games():
    """Obtener lista de juegos disponibles"""
    return {
        "success": True,
        "data": GAMES,
        "total": len(GAMES)
    }

@app.get("/api/games/{game_id}")
async def get_game(game_id: int, db: Session = Depends(get_db)):
    """Obtener detalles de un juego específico"""
    game = next((g for g in GAMES if g["id"] == game_id), None)
    if not game:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    
    # Registrar interacción
    try:
        interaction = GameInteraction(
            game_name=game["name"],
            interaction_type="view"
        )
        db.add(interaction)
        db.commit()
    except Exception as e:
        print(f"Error registrando interacción: {e}")
    
    return {
        "success": True,
        "data": game
    }

@app.post("/api/games/{game_id}/interact")
async def interact_with_game(
    game_id: int, 
    request: Request,
    db: Session = Depends(get_db)
):
    """Registrar interacción con un juego (Meta Pixel tracking)"""
    game = next((g for g in GAMES if g["id"] == game_id), None)
    if not game:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    
    try:
        # Registrar interacción en la base de datos
        interaction = GameInteraction(
            game_name=game["name"],
            interaction_type="click",
            user_agent=request.headers.get("user-agent"),
            ip_address=request.client.host
        )
        db.add(interaction)
        db.commit()
        
        return {
            "success": True,
            "message": "Interacción registrada",
            "game": game["name"],
            "whatsapp_url": "https://wa.me/5491178419956?text=Hola!%20Buenas!!%20vengo%20por%20mi%20usuario%20de%20la%20suerte%20🍀"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error registrando interacción: {str(e)}")

@app.get("/api/promotions")
async def get_promotions():
    """Obtener lista de promociones disponibles"""
    active_promotions = [p for p in PROMOTIONS if p.get("active", True)]
    return {
        "success": True,
        "data": active_promotions,
        "total": len(active_promotions)
    }

@app.post("/api/promotions/{promo_id}/interact")
async def interact_with_promotion(
    promo_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Registrar interacción con una promoción"""
    promo = next((p for p in PROMOTIONS if p["id"] == promo_id), None)
    if not promo:
        raise HTTPException(status_code=404, detail="Promoción no encontrada")
    
    try:
        interaction = PromoInteraction(
            promo_name=promo["title"],
            interaction_type="click",
            user_agent=request.headers.get("user-agent"),
            ip_address=request.client.host
        )
        db.add(interaction)
        db.commit()
        
        return {
            "success": True,
            "message": "Interacción con promoción registrada",
            "promo": promo["title"],
            "whatsapp_url": "https://wa.me/5491178419956?text=Hola!%20Buenas!!%20vengo%20por%20mi%20usuario%20de%20la%20suerte%20🍀"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error registrando interacción: {str(e)}")

@app.get("/api/payment-methods")
async def get_payment_methods():
    """Obtener métodos de pago disponibles"""
    return {
        "success": True,
        "data": PAYMENT_METHODS,
        "total": len(PAYMENT_METHODS)
    }

@app.post("/api/contact")
async def contact_form(
    contact_data: dict,
    request: Request,
    db: Session = Depends(get_db)
):
    """Endpoint para formularios de contacto (Meta Pixel tracking)"""
    try:
        # Registrar contacto en la base de datos
        contact = Contact(
            name=contact_data.get("name"),
            phone=contact_data.get("phone"),
            email=contact_data.get("email"),
            message=contact_data.get("message", "Contacto desde landing page"),
            source=contact_data.get("source", "whatsapp")
        )
        db.add(contact)
        db.commit()
        
        return {
            "success": True,
            "message": "Solicitud de contacto registrada exitosamente",
            "whatsapp_url": "https://wa.me/5491178419956?text=Hola!%20Buenas!!%20vengo%20por%20mi%20usuario%20de%20la%20suerte%20🍀"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error registrando contacto: {str(e)}")

@app.get("/api/faq")
async def get_faq():
    """Obtener preguntas frecuentes"""
    faq_data = [
        {
            "id": 1,
            "question": "¿Es Ares Club seguro?",
            "answer": "Sí, Ares Club es seguro para todos los jugadores. El sitio utiliza tecnología de cifrado avanzada para proteger tu información personal y financiera.",
            "category": "security"
        },
        {
            "id": 2,
            "question": "¿Cuanto tiempo demora hacer mi usuario?",
            "answer": "Los usuarios se crean al instante que lo solicitas.",
            "category": "account"
        },
        {
            "id": 3,
            "question": "¿Cuánto tardan los retiros?",
            "answer": "Los retiros son en el momento que lo solicitas.",
            "category": "payments"
        },
        {
            "id": 4,
            "question": "¿Hay política de reembolsos?",
            "answer": "Sí, la plataforma tiene una política de reembolsos. Puedes contactar al soporte al cliente para recibir asistencia.",
            "category": "policies"
        },
        {
            "id": 5,
            "question": "¿Hay códigos promocionales?",
            "answer": "Los jugadores nuevos y existentes pueden aprovechar los bonos y promociones regulares disponibles en el sitio.",
            "category": "promotions"
        },
        {
            "id": 6,
            "question": "¿Cuanto demoran las recargas?",
            "answer": "Las recargas son en el momento apenas impacte el deposito que solicitas.",
            "category": "payments"
        }
    ]
    return {
        "success": True,
        "data": faq_data,
        "total": len(faq_data)
    }

@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Obtener estadísticas básicas (para admin)"""
    try:
        total_contacts = db.query(Contact).count()
        total_game_interactions = db.query(GameInteraction).count()
        total_promo_interactions = db.query(PromoInteraction).count()
        
        # Top juegos más clickeados
        top_games = db.query(GameInteraction.game_name, func.count(GameInteraction.id).label('clicks'))\
                     .group_by(GameInteraction.game_name)\
                     .order_by(desc('clicks'))\
                     .limit(5).all()
        
        return {
            "success": True,
            "data": {
                "total_contacts": total_contacts,
                "total_game_interactions": total_game_interactions,
                "total_promo_interactions": total_promo_interactions,
                "top_games": [{"name": game[0], "clicks": game[1]} for game in top_games]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")

# Endpoints de autenticación
@app.post("/api/auth/login")
async def login(login_data: dict, db: Session = Depends(get_db)):
    """Login de usuario"""
    username = login_data.get("username")
    password = login_data.get("password")
    
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password required")
    
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_admin
        }
    }

@app.get("/api/auth/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Obtener información del usuario actual"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_admin": current_user.is_admin
    }

# Endpoints de chat
@app.get("/api/chat/messages")
async def get_chat_messages(db: Session = Depends(get_db)):
    """Obtener mensajes del chat"""
    messages = db.query(ChatMessage).order_by(desc(ChatMessage.created_at)).limit(50).all()
    return {
        "success": True,
        "data": [
            {
                "id": msg.id,
                "username": msg.username,
                "message": msg.message,
                "is_admin": msg.is_admin,
                "created_at": msg.created_at.isoformat()
            }
            for msg in reversed(messages)
        ]
    }

@app.post("/api/chat/send")
async def send_chat_message(
    message_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Enviar mensaje al chat (solo admins)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can send messages")
    
    message_text = message_data.get("message")
    if not message_text:
        raise HTTPException(status_code=400, detail="Message is required")
    
    chat_message = ChatMessage(
        user_id=current_user.id,
        username=current_user.username,
        message=message_text,
        is_admin=True
    )
    
    db.add(chat_message)
    db.commit()
    
    # Emitir mensaje a todos los clientes conectados
    await sio.emit('new_message', {
        'id': chat_message.id,
        'username': chat_message.username,
        'message': chat_message.message,
        'is_admin': True,
        'created_at': chat_message.created_at.isoformat()
    })
    
    return {"success": True, "message": "Message sent"}

# Socket.IO events
@sio.event
async def connect(sid, environ):
    print(f"Cliente conectado: {sid}")
    await sio.emit('connected', {'message': 'Conectado al chat de Ares Club'}, room=sid)

@sio.event
async def disconnect(sid):
    print(f"Cliente desconectado: {sid}")

@sio.event
async def user_message(sid, data):
    """Manejar mensajes de usuarios"""
    username = data.get('username', 'Usuario Anónimo')
    message = data.get('message', '')
    
    if not message.strip():
        return
    
    # Guardar mensaje en la base de datos
    db = SessionLocal()
    try:
        chat_message = ChatMessage(
            username=username,
            message=message,
            is_admin=False
        )
        db.add(chat_message)
        db.commit()
        
        # Emitir mensaje a todos los clientes
        await sio.emit('new_message', {
            'id': chat_message.id,
            'username': username,
            'message': message,
            'is_admin': False,
            'created_at': chat_message.created_at.isoformat()
        })
        
    except Exception as e:
        print(f"Error guardando mensaje: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(socket_app, host="0.0.0.0", port=8001)
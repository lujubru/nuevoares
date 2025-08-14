from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = FastAPI(title="Ares Club Casino API", version="1.0.0")

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Juegos disponibles
GAMES = [
    {
        "id": 1,
        "name": "Volcano Rising",
        "provider": "RubyPlay",
        "image": "/static/images/volcano.jpg",
        "category": "slots"
    },
    {
        "id": 2,
        "name": "Sweet Bonanza 1000",
        "provider": "Pragmatic Play",
        "image": "/static/images/bonanza.jpg",
        "category": "slots"
    },
    {
        "id": 3,
        "name": "Reactoonz",
        "provider": "Play n' Go",
        "image": "/static/images/reac.jpg",
        "category": "slots"
    },
    {
        "id": 4,
        "name": "Book of Dead",
        "provider": "Play n' Go",
        "image": "/static/images/book.jpg",
        "category": "slots"
    },
    {
        "id": 5,
        "name": "Zeus Rush Fever Deluxe",
        "provider": "RubyPlay",
        "image": "/static/images/zeus.jpg",
        "category": "slots"
    },
    {
        "id": 6,
        "name": "Wolf Gold",
        "provider": "Pragmatic Play",
        "image": "/static/images/wolf.jpg",
        "category": "slots"
    }
]

# Promociones y bonos
PROMOTIONS = [
    {
        "id": 1,
        "title": "Bono de Bienvenida",
        "description": "Los nuevos jugadores son recibidos con un bono del 20% mas en tu primer carga!",
        "type": "welcome_bonus"
    },
    {
        "id": 2,
        "title": "Eventos Especiales",
        "description": "Participa en eventos especiales donde puedes ganar recompensas y premios exclusivos.",
        "type": "special_events"
    }
]

# Métodos de pago
PAYMENT_METHODS = [
    {"name": "Visa", "type": "card"},
    {"name": "Mastercard", "type": "card"},
    {"name": "Transferencia Bancaria", "type": "bank"},
    {"name": "E-Wallets", "type": "ewallet"}
]

@app.get("/")
async def root():
    return {"message": "Bienvenido a Ares Club Casino API"}

@app.get("/api/games")
async def get_games():
    """Obtener lista de juegos disponibles"""
    return {
        "success": True,
        "data": GAMES,
        "total": len(GAMES)
    }

@app.get("/api/games/{game_id}")
async def get_game(game_id: int):
    """Obtener detalles de un juego específico"""
    game = next((g for g in GAMES if g["id"] == game_id), None)
    if not game:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    return {
        "success": True,
        "data": game
    }

@app.get("/api/promotions")
async def get_promotions():
    """Obtener lista de promociones disponibles"""
    return {
        "success": True,
        "data": PROMOTIONS,
        "total": len(PROMOTIONS)
    }

@app.get("/api/payment-methods")
async def get_payment_methods():
    """Obtener métodos de pago disponibles"""
    return {
        "success": True,
        "data": PAYMENT_METHODS,
        "total": len(PAYMENT_METHODS)
    }

@app.post("/api/contact")
async def contact_form(contact_data: dict):
    """Endpoint para formularios de contacto (Meta Pixel tracking)"""
    # Aquí podrías procesar la información de contacto
    # Por ahora solo registramos que se hizo contacto
    return {
        "success": True,
        "message": "Solicitud de contacto registrada exitosamente",
        "whatsapp_url": "https://wa.me/5491178419956?text=Hola!%20Buenas!!%20vengo%20por%20mi%20usuario%20de%20la%20suerte%20🍀"
    }

@app.get("/api/faq")
async def get_faq():
    """Obtener preguntas frecuentes"""
    faq_data = [
        {
            "question": "¿Es Ares Club seguro?",
            "answer": "Sí, Ares Club es seguro para todos los jugadores. El sitio utiliza tecnología de cifrado avanzada para proteger tu información personal y financiera."
        },
        {
            "question": "¿Cuanto tiempo demora hacer mi usuario?",
            "answer": "Los usuarios se crean al instante que lo solicitas."
        },
        {
            "question": "¿Cuánto tardan los retiros?",
            "answer": "Los retiros son en el momento que lo solicitas."
        },
        {
            "question": "¿Hay política de reembolsos?",
            "answer": "Sí, la plataforma tiene una política de reembolsos. Puedes contactar al soporte al cliente para recibir asistencia."
        },
        {
            "question": "¿Hay códigos promocionales?",
            "answer": "Los jugadores nuevos y existentes pueden aprovechar los bonos y promociones regulares disponibles en el sitio."
        },
        {
            "question": "¿Cuanto demoran las recargas?",
            "answer": "Las recargas son en el momento apenas impacte el deposito que solicitas."
        }
    ]
    return {
        "success": True,
        "data": faq_data,
        "total": len(faq_data)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
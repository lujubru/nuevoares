from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Crear el engine de SQLAlchemy
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

# Configuración para hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Modelos de base de datos
class Contact(Base):
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(120), nullable=True)
    message = Column(Text, nullable=True)
    source = Column(String(50), default="whatsapp")  # whatsapp, form, etc
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class GameInteraction(Base):
    __tablename__ = "game_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    game_name = Column(String(100), nullable=False)
    interaction_type = Column(String(50), default="click")  # click, view, etc
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PromoInteraction(Base):
    __tablename__ = "promo_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    promo_name = Column(String(100), nullable=False)
    interaction_type = Column(String(50), default="click")
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)  # None para usuarios anónimos
    username = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Función para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Función para crear las tablas
def create_tables():
    Base.metadata.create_all(bind=engine)
    
    # Crear usuario admin por defecto
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            hashed_password = pwd_context.hash("admin123")
            admin_user = User(
                username="admin",
                email="admin@aresclub.com",
                hashed_password=hashed_password,
                is_admin=True
            )
            db.add(admin_user)
            db.commit()
            print("✅ Usuario admin creado")
    except Exception as e:
        print(f"Error creando admin: {e}")
    finally:
        db.close()

# Función para verificar conexión
def check_db_connection():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return False

# Funciones de autenticación
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
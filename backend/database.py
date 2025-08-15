from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Crear el engine de SQLAlchemy
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

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
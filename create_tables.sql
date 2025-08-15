-- Script SQL para crear las tablas de Ares Club Casino en PostgreSQL
-- Ejecutar este script en pgAdmin4 conectado a tu base de datos de Railway

-- Crear tabla de contactos
CREATE TABLE IF NOT EXISTS contacts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(120),
    message TEXT,
    source VARCHAR(50) DEFAULT 'whatsapp',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Crear índice en created_at para consultas más rápidas
CREATE INDEX IF NOT EXISTS idx_contacts_created_at ON contacts(created_at);
CREATE INDEX IF NOT EXISTS idx_contacts_source ON contacts(source);

-- Crear tabla de interacciones con juegos
CREATE TABLE IF NOT EXISTS game_interactions (
    id SERIAL PRIMARY KEY,
    game_name VARCHAR(100) NOT NULL,
    interaction_type VARCHAR(50) DEFAULT 'click',
    user_agent TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Crear índices para optimizar consultas de estadísticas
CREATE INDEX IF NOT EXISTS idx_game_interactions_game_name ON game_interactions(game_name);
CREATE INDEX IF NOT EXISTS idx_game_interactions_created_at ON game_interactions(created_at);
CREATE INDEX IF NOT EXISTS idx_game_interactions_type ON game_interactions(interaction_type);

-- Crear tabla de interacciones con promociones
CREATE TABLE IF NOT EXISTS promo_interactions (
    id SERIAL PRIMARY KEY,
    promo_name VARCHAR(100) NOT NULL,
    interaction_type VARCHAR(50) DEFAULT 'click',
    user_agent TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Crear índices para optimizar consultas de estadísticas
CREATE INDEX IF NOT EXISTS idx_promo_interactions_promo_name ON promo_interactions(promo_name);
CREATE INDEX IF NOT EXISTS idx_promo_interactions_created_at ON promo_interactions(created_at);
CREATE INDEX IF NOT EXISTS idx_promo_interactions_type ON promo_interactions(interaction_type);

-- Insertar algunos datos de ejemplo (opcional)
-- Descomenta las siguientes líneas si quieres datos de prueba

/*
INSERT INTO contacts (name, phone, email, message, source) VALUES 
('Usuario Prueba', '+549111234567', 'test@example.com', 'Consulta desde landing page', 'whatsapp');

INSERT INTO game_interactions (game_name, interaction_type) VALUES 
('Volcano Rising', 'click'),
('Sweet Bonanza 1000', 'view'),
('Reactoonz', 'click');

INSERT INTO promo_interactions (promo_name, interaction_type) VALUES 
('Bono de Bienvenida', 'click'),
('Eventos Especiales', 'view');
*/

-- Verificar que las tablas se crearon correctamente
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('contacts', 'game_interactions', 'promo_interactions');
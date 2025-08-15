# 📊 INSTRUCCIONES PARA CREAR TABLAS EN PGADMIN4

## ✅ ESTADO ACTUAL
**¡LAS TABLAS YA ESTÁN CREADAS AUTOMÁTICAMENTE!** 🎉

Al ejecutar la aplicación, las tablas se crearon automáticamente en tu base de datos PostgreSQL de Railway. Puedes verificarlo ejecutando esta consulta en pgAdmin4:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('contacts', 'game_interactions', 'promo_interactions');
```

## 🗂️ TABLAS CREADAS

### 1. **contacts** - Formularios de Contacto
```sql
CREATE TABLE contacts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    phone VARCHAR(20), 
    email VARCHAR(120),
    message TEXT,
    source VARCHAR(50) DEFAULT 'whatsapp',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Función:** Almacena todos los contactos que llegan desde:
- Formularios web
- Clics en WhatsApp
- Otras fuentes de leads

### 2. **game_interactions** - Tracking de Juegos
```sql
CREATE TABLE game_interactions (
    id SERIAL PRIMARY KEY,
    game_name VARCHAR(100) NOT NULL,
    interaction_type VARCHAR(50) DEFAULT 'click',
    user_agent TEXT,
    ip_address VARCHAR(45), 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Función:** Rastrea cada interacción con los juegos:
- Clics en "Jugar Ahora"
- Visualizaciones de juegos
- Meta Pixel events

### 3. **promo_interactions** - Tracking de Promociones
```sql
CREATE TABLE promo_interactions (
    id SERIAL PRIMARY KEY,
    promo_name VARCHAR(100) NOT NULL,
    interaction_type VARCHAR(50) DEFAULT 'click',
    user_agent TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Función:** Rastrea interacciones con promociones:
- Clics en bonos
- Eventos especiales
- Campañas promocionales

## 📈 CONSULTAS ÚTILES PARA PGADMIN4

### Ver todos los contactos recientes:
```sql
SELECT * FROM contacts ORDER BY created_at DESC LIMIT 10;
```

### Top 5 juegos más clickeados:
```sql
SELECT game_name, COUNT(*) as clicks 
FROM game_interactions 
GROUP BY game_name 
ORDER BY clicks DESC 
LIMIT 5;
```

### Estadísticas del día:
```sql
SELECT 
    (SELECT COUNT(*) FROM contacts WHERE DATE(created_at) = CURRENT_DATE) as contactos_hoy,
    (SELECT COUNT(*) FROM game_interactions WHERE DATE(created_at) = CURRENT_DATE) as clics_juegos_hoy,
    (SELECT COUNT(*) FROM promo_interactions WHERE DATE(created_at) = CURRENT_DATE) as clics_promos_hoy;
```

### Interacciones por hora (último día):
```sql
SELECT 
    EXTRACT(HOUR FROM created_at) as hora,
    COUNT(*) as interacciones
FROM game_interactions 
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY EXTRACT(HOUR FROM created_at)
ORDER BY hora;
```

## 🔧 MANTENIMIENTO

### Limpiar datos antiguos (opcional):
```sql
-- Eliminar interacciones más antiguas de 6 meses
DELETE FROM game_interactions WHERE created_at < NOW() - INTERVAL '6 months';
DELETE FROM promo_interactions WHERE created_at < NOW() - INTERVAL '6 months';
```

### Crear índices adicionales para mejor performance:
```sql
CREATE INDEX idx_contacts_email ON contacts(email);
CREATE INDEX idx_game_interactions_ip ON game_interactions(ip_address);
CREATE INDEX idx_promo_interactions_ip ON promo_interactions(ip_address);
```

## 🎯 RESUMEN

**✅ Estado:** Tablas creadas y funcionando  
**✅ Conexión:** PostgreSQL Railway OK  
**✅ API:** Endpoints funcionando  
**✅ Tracking:** Sistema de métricas activo  

**🚀 Próximo paso:** Desplegar en Railway y Vercel siguiendo `README_DEPLOY.md`
# Guía de Despliegue - Ares Club Casino

## 🚀 Pasos para Desplegar

### 1. Base de Datos (PostgreSQL en Railway) ✅ COMPLETADO

Las tablas ya están creadas automáticamente en tu base de datos de Railway. Si necesitas recrearlas manualmente, usa el archivo `create_tables.sql` en pgAdmin4.

**Tablas creadas:**
- `contacts` - Para formularios de contacto
- `game_interactions` - Para tracking de clics en juegos  
- `promo_interactions` - Para tracking de clics en promociones

### 2. Desplegar Backend en Railway 🚂

1. **Crear nuevo proyecto en Railway:**
   - Ve a [railway.app](https://railway.app)
   - Crea un nuevo proyecto
   - Conecta tu repositorio de GitHub

2. **Configurar variables de entorno:**
   ```
   DATABASE_URL=postgresql://postgres:MRywQLUhiSrUvCrTbHZCOGonlTtEmgoQ@nozomi.proxy.rlwy.net:41589/railway
   PORT=8001
   ```

3. **Railway detectará automáticamente:**
   - `railway.toml` (configuración)
   - `Procfile` (comando de inicio)
   - `requirements.txt` (dependencias)

4. **Una vez desplegado, Railway te dará una URL como:**
   `https://tu-proyecto.railway.app`

### 3. Desplegar Frontend en Vercel 🌐

1. **Actualizar URL del backend:**
   Antes de desplegar, actualiza `/app/frontend/.env`:
   ```
   REACT_APP_BACKEND_URL=https://tu-proyecto.railway.app
   ```

2. **Desplegar en Vercel:**
   - Ve a [vercel.com](https://vercel.com)
   - Conecta tu repositorio de GitHub
   - Vercel detectará automáticamente `vercel.json`
   - Las variables de entorno se configurarán automáticamente

3. **Vercel te dará una URL como:**
   `https://tu-proyecto.vercel.app`

## 🔧 Configuración Avanzada

### Meta Pixel (Facebook Ads)
El código ya está preparado para Meta Pixel. Solo necesitas:
1. Reemplazar el Pixel ID en el HTML
2. Configurar eventos personalizados según necesites

### Monitoreo
- Endpoint de health check: `/api/health`
- Estadísticas básicas: `/api/stats`

### Base de Datos
- **Conexión:** Ya configurada con Railway PostgreSQL
- **Migraciones:** Automáticas al iniciar la aplicación
- **Backup:** Usa las herramientas de Railway para backups

## 📁 Estructura de Archivos Creados

```
/app/
├── railway.toml          # Configuración Railway
├── vercel.json          # Configuración Vercel  
├── create_tables.sql    # Script SQL para tablas
├── backend/
│   ├── Procfile        # Comando para Railway
│   └── .env            # Variables de entorno (PostgreSQL)
└── README_DEPLOY.md    # Esta guía
```

## 🛠️ Comandos Útiles

**Verificar conexión DB local:**
```bash
cd backend && python -c "from database import check_db_connection; print('✅ OK' if check_db_connection() else '❌ Error')"
```

**Crear tablas manualmente:**
```bash
cd backend && python -c "from database import create_tables; create_tables()"
```

**Probar API local:**
```bash
curl http://localhost:8001/api/health
```

## 🎯 URLs Finales

Una vez desplegado tendrás:
- **Frontend:** `https://tu-proyecto.vercel.app`
- **Backend API:** `https://tu-proyecto.railway.app/api`
- **Base de Datos:** Ya configurada en Railway

## 📞 Funcionalidades

### Landing Page Features:
- ✅ Carousel de imágenes automático
- ✅ Sección de juegos con tracking
- ✅ Promociones y bonos
- ✅ FAQ personalizado
- ✅ WhatsApp flotante
- ✅ Meta Pixel integration
- ✅ Formulario de contacto
- ✅ Responsive design

### Backend Features:
- ✅ API RESTful con FastAPI
- ✅ Base de datos PostgreSQL
- ✅ Tracking de interacciones
- ✅ Estadísticas básicas
- ✅ Health checks
- ✅ CORS configurado

¡Tu aplicación está lista para producción! 🎉
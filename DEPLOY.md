# 🚀 Guía de Deployment - Backend en Render

## ✅ Archivos Necesarios para Deployment

Los siguientes archivos ya están configurados y listos:

- ✅ `requirements.txt` - Dependencias sin conflictos
- ✅ `setup.py` - Instalación del paquete deepagents
- ✅ `start.sh` - Script de inicio para Render
- ✅ `runtime.txt` - Versión de Python (3.11.10)
- ✅ `agent.py` - Servidor FastAPI principal

## 🔧 Configuración en Render

### 1. Configuración del Servicio

- **Build Command**: `pip install -r requirements.txt && pip install -e .`
- **Start Command**: `python agent.py`
- **Environment**: `Python 3`
- **Region**: Elige la más cercana
- **Instance Type**: Starter (gratis) o Pro según necesidades

### 2. Variables de Entorno Requeridas

```bash
# OBLIGATORIO - API Key de Anthropic
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# OPCIONAL - LangSmith para debugging (recomendado desactivar en producción)
LANGCHAIN_TRACING_V2=false

# OPCIONAL - Si quieres usar LangSmith
# LANGCHAIN_API_KEY=tu_langsmith_api_key_aqui
# LANGCHAIN_TRACING_V2=true

# Puerto automático de Render (no cambiar)
PORT=10000
```

### 3. Pasos de Deployment

1. **Conecta tu repositorio a Render**
   - Ve a [render.com](https://render.com)
   - Conecta tu cuenta de GitHub
   - Selecciona el repositorio `LoisAgent`

2. **Configura el servicio**
   - Tipo: `Web Service`
   - Root Directory: `Backend`
   - Build Command: `pip install -r requirements.txt && pip install -e .`
   - Start Command: `python agent.py`

3. **Agrega las variables de entorno**
   - Ve a Environment en el dashboard de Render
   - Agrega `ANTHROPIC_API_KEY` con tu API key real

4. **Deploy**
   - Haz clic en "Create Web Service"
   - Espera a que termine el deployment (5-10 minutos)

## 🌐 URLs de Producción

Una vez deployado, tendrás:

- **API Base**: `https://tu-servicio-render.onrender.com`
- **Health Check**: `https://tu-servicio-render.onrender.com/health`
- **Documentación**: `https://tu-servicio-render.onrender.com/docs`
- **Chat Endpoint**: `https://tu-servicio-render.onrender.com/chat`
- **Streaming**: `https://tu-servicio-render.onrender.com/chat/stream`

## 🔍 Verificación del Deployment

```bash
# Test health endpoint
curl https://tu-servicio-render.onrender.com/health

# Test chat endpoint
curl -X POST "https://tu-servicio-render.onrender.com/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "test deployment", "thread_id": "test"}'
```

## ⚠️ Notas Importantes

1. **Render tarda ~2-3 minutos en arrancar** el servicio después de inactividad
2. **El plan gratuito** tiene limitaciones de tiempo de actividad
3. **Los archivos locales** (como los .md creados por write_file) se perderán en cada restart
4. **La base de datos SQLite** se resetea en cada deployment (considera usar PostgreSQL para producción)

## 🔄 Actualizaciones

Para actualizar el deployment:
1. Haz push a tu rama `main` en GitHub
2. Render automáticamente detectará los cambios
3. Se ejecutará un nuevo deployment

## 🐛 Troubleshooting

**Error: "Module not found"**
- Verifica que `setup.py` esté en el directorio Backend
- Asegúrate que el Build Command incluya `pip install -e .`

**Error: "Port already in use"**
- Render maneja automáticamente el puerto, no cambies la variable PORT

**Error: "API Key invalid"**
- Verifica que `ANTHROPIC_API_KEY` esté configurada correctamente
- Genera una nueva API key en [console.anthropic.com](https://console.anthropic.com)

## ✅ Frontend Configuration

Una vez que tengas la URL del backend, actualiza el frontend:

```bash
# En Frontend/.env.local
NEXT_PUBLIC_DEPLOYMENT_URL=https://tu-servicio-render.onrender.com
NEXT_PUBLIC_AGENT_ID=deepagent
```
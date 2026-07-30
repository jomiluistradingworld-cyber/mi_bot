# 🤖 Mi Bot IA Local

Bot de Telegram conversacional potenciado por LLMs locales (`llama.cpp`) con sistema de personalidades, memoria persistente y dashboard de análisis.

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.11+-blue)

## ✨ Características

- 🎭 **6 Personalidades Constructivas**: Desde un coach motivacional hasta un filósofo reflexivo.
- 🧠 **Memoria Persistente**: Recuerdo de conversaciones y puntos clave por usuario y personalidad.
- 📉 **Análisis de Sentimientos**: Clasificación de mensajes en positivo, negativo o neutral usando TextBlob.
- 📊 **Dashboard Web Moderno**: Vista de estadísticas globales y detalle de usuario con HTMX y TailwindCSS.
- 🚀 **100% Local**: Privacidad total, sin costos de API y sin censura externa.
- 📦 **Docker Ready**: Despliegue rápido mediante `docker-compose`.

## 🏗️ Arquitectura

```text
[Telegram User] <---> [pyTelegramBotAPI] <---> [FastAPI App] <---> [SQLite DB]
                                                   ^
                                                   |
                                           [llama-server (Local LLM)]
```

## 🛠️ Requisitos

- **Hardware**: CPU moderna (8GB+ RAM recomendados) o GPU NVIDIA.
- **Software**: Docker y Docker Compose (opcional), o Python 3.11+.

## 🚀 Instalación Paso a Paso

### 1. Clonar el Repositorio
```bash
git clone https://github.com/jomiluistradingworld-cyber/mi_bot.git
cd mi_bot
```

### 2. Configuración de Variables de Entorno
```bash
cp .env.example .env
nano .env # Editar el TELEGRAM_BOT_TOKEN
```

### 3. Instalación de Dependencias
```bash
chmod +x setup.sh
./setup.sh
```

### 4. Descarga del Modelo
Descarga un modelo GGUF (ej. `dolphin-2.7b-q4_k_m.gguf`) y colócalo en la carpeta `/models`.

### 5. Ejecución
```bash
# Opción A: Script local
./run_all.sh

# Opción B: Docker
docker-compose up -d
```

## 🎮 Uso del Bot

### Comandos Principales:
- `/start` - Inicia el bot y muestra el menú de personalidades.
- `/help` - Muestra la lista de comandos.
- `/reset` - Borra el historial de la personalidad activa.
- `/exportar` - Envía un archivo JSON con tu historial.
- `/insights` - Genera un análisis de patrones usando la IA.

### Personalidades Disponibles:
| Comando | Nombre | Descripción |
| :--- | :--- | :--- |
| `/amigo` | Amigo Casual | Charlas sinceras y consejos modernos. |
| `/motivador` | Coach Motivacional | Energía, acción y positivismo. |
| `/sabio` | Filósofo Reflexivo | Reflexiones profundas y citas clásicas. |
| `/humorista` | Comediante | Sarcasmo amable y observaciones ingeniosas. |
| `/mentor` | Mentor Profesional | Desarrollo de carrera y liderazgo. |
| `/apoyo` | Consejero Empático | Escucha activa y acompañamiento emocional. |

## 📈 Dashboard Web
Accede a `http://localhost:8000` para visualizar:
- Estadísticas globales de usuarios y mensajes.
- Tabla de usuarios con búsqueda en tiempo real (HTMX).
- Detalle de conversación y análisis de sentimiento por usuario.
- Generación de insights automatizados.

## 📂 Estructura del Proyecto
- `src/mi_bot/core`: Configuración, prompts de personalidades y cliente LLM.
- `src/mi_bot/db`: Modelos SQLAlchemy y repositorios CRUD.
- `src/mi_bot/services`: Lógica de memoria, sentimientos y exportación.
- `src/mi_bot/bot`: Controladores del bot de Telegram.
- `src/mi_bot/api`: Endpoints de FastAPI y lógica del dashboard.
- `src/mi_bot/web`: Templates Jinja2 y assets estáticos.

## 📄 Licencia
Este proyecto está bajo la licencia MIT.

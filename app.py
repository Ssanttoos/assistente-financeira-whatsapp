"""
Assistente Financeira para WhatsApp
Entry point da aplicação FastAPI
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from database.firebase import init_firebase
from routes.webhook import router as webhook_router
from routes.health import router as health_router

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    logger.info("🚀 Iniciando Assistente Financeira...")
    init_firebase()
    logger.info("✅ Firebase conectado com sucesso!")
    yield
    logger.info("🔴 Encerrando aplicação...")


app = FastAPI(
    title="Assistente Financeira WhatsApp",
    description="API para assistente financeira via WhatsApp usando Evolution API e Firebase",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(webhook_router, prefix="/webhook", tags=["Webhook"])
app.include_router(health_router, prefix="/health", tags=["Health"])


@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Assistente Financeira WhatsApp",
        "version": "1.0.0"
    }

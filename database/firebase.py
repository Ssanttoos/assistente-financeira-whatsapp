"""
Módulo de conexão com Firebase Firestore
Inicialização e funções auxiliares de acesso ao banco
"""

import logging
from typing import Optional

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import Client

from config.settings import settings

logger = logging.getLogger(__name__)

_db: Optional[Client] = None


def init_firebase() -> None:
    """Inicializa o Firebase Admin SDK"""
    global _db
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(settings.firebase_credentials_path)
            firebase_admin.initialize_app(cred, {
                "projectId": settings.firebase_project_id
            })
        _db = firestore.client()
        logger.info("Firebase Firestore inicializado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao inicializar Firebase: {e}")
        raise


def get_db() -> Client:
    """Retorna instância do Firestore client"""
    global _db
    if _db is None:
        raise RuntimeError("Firebase não foi inicializado. Chame init_firebase() primeiro.")
    return _db


def get_usuario_ref(telefone: str):
    """Retorna referência do documento do usuário"""
    return get_db().collection("usuarios").document(telefone)


def get_transacoes_ref(telefone: str):
    """Retorna referência da subcoleção de transações do usuário"""
    return get_usuario_ref(telefone).collection("transacoes")

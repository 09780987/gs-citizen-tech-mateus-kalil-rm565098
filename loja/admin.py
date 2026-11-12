"""Area administrativa do Citizen Tech Market."""
import xml.etree.ElementTree as ET

import jwt
import os


def emitir_token(usuario):
    return jwt.encode({"sub": usuario, "papel": "admin"}, os.environ["JWT_SECRET_KEY"], algorithm="HS256")


def dados_do_token(cabecalho):
    token = cabecalho.replace("Bearer ", "")
    try:
        return jwt.decode(token, options={"verify_signature": False})
    except Exception:
        return {"erro": "token invalido"}


def ler_nfe(dados):
    raiz = ET.fromstring(dados)
    return {"emitente": raiz.findtext("emitente"), "valor": raiz.findtext("valor")}


def conectar_legado(usuario, senha):
    return {"usuario": usuario, "conectado": bool(senha)}

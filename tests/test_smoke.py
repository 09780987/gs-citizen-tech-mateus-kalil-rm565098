"""Testes funcionais com entradas comuns; nao exploram vulnerabilidades."""
import importlib
import json
import os
import secrets

import pytest


@pytest.fixture
def cliente(tmp_path, monkeypatch):
    monkeypatch.setenv("LOJA_DB", str(tmp_path / "market.sqlite"))
    monkeypatch.setenv("FLASK_SECRET_KEY", secrets.token_hex(32))
    monkeypatch.setenv("JWT_SECRET_KEY", secrets.token_hex(32))
    import loja.db
    importlib.reload(loja.db)
    import app
    app.app.config["TESTING"] = True
    return app.app.test_client()


def test_pagina_inicial(cliente):
    resposta = cliente.get("/")
    assert resposta.status_code == 200
    assert b"Citizen Tech Market" in resposta.data


def test_produto_cadastrado(cliente):
    resposta = cliente.get("/produto?id=1")
    assert resposta.status_code == 200
    assert json.loads(resposta.data)["produto"][0] == 1


def test_busca_comum(cliente):
    resposta = cliente.get("/busca?q=certidao")
    assert resposta.status_code == 200
    assert b"Resultados para: certidao" in resposta.data


def test_saudacao_comum(cliente):
    resposta = cliente.get("/saudacao?nome=Mateus")
    assert resposta.status_code == 200
    assert b"Mateus" in resposta.data


def test_relatorio_mes_existente(cliente):
    resposta = cliente.get("/admin/relatorio?mes=01")
    assert resposta.status_code == 200
    assert json.loads(resposta.data)["pedidos"] == 2

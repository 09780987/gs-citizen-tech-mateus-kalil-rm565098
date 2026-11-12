import os
"""Configuracoes do Citizen Tech Market."""
DEBUG = True
REGIAO = "sa-east-1"
BUCKET = "ct-market-notas-fiscais"

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")

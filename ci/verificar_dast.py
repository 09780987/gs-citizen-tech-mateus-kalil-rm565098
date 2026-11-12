"""Gate de evidencia DAST: nao executa ataques e nao aceita baseline como ativo."""
import json
import os
import sys
from pathlib import Path

relatorio = Path(sys.argv[1])
contexto = Path(sys.argv[2])
if not relatorio.is_file() or not contexto.is_file():
    sys.exit("REPROVADO: faltam o relatorio ZAP e os metadados da varredura ativa.")
d = json.loads(relatorio.read_text(encoding="utf-8-sig"))
m = json.loads(contexto.read_text(encoding="utf-8-sig"))
if not isinstance(d.get("site"), list) or not d.get("@version"):
    sys.exit("REPROVADO: o arquivo nao e um relatorio JSON tradicional do ZAP.")
if m.get("modo") != "ativo" or m.get("varredura_concluida") is not True:
    sys.exit("REPROVADO: evidencia apenas passiva ou varredura ativa incompleta.")
if os.environ.get("GITHUB_SHA") and m.get("commit_sha") != os.environ["GITHUB_SHA"]:
    sys.exit("REPROVADO: a evidencia nao corresponde ao commit desta execucao.")
if any(int(a.get("riskcode", 0)) >= 3 for site in d["site"] for a in site.get("alerts", [])):
    sys.exit("REPROVADO: o ZAP registrou achado de risco alto.")
print("APROVADO: evidencia ativa concluida e sem achados altos.")

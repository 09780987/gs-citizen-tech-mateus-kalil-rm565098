import json
import sys
from pathlib import Path

total = 0
for nome in sys.argv[1:]:
    d = json.loads(Path(nome).read_text(encoding="utf-8"))
    if not isinstance(d.get("Results"), list):
        sys.exit("REPROVADO: relatorio Trivy incompleto ou invalido.")
    for resultado in d["Results"]:
        for chave in ("Vulnerabilities", "Misconfigurations"):
            total += sum(v.get("Severity") in ("HIGH", "CRITICAL") for v in resultado.get(chave, []))
if total:
    sys.exit(f"REPROVADO: {total} achados altos/criticos.")
print("APROVADO: Trivy sem riscos altos ou criticos.")

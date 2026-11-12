import json
import sys
from pathlib import Path

d = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
if d.get("errors"):
    sys.exit("REPROVADO: analise SAST incompleta ou com erro.")
achados = [r for r in d.get("results", []) if
           r.get("extra", {}).get("severity") == "ERROR" or
           r.get("extra", {}).get("metadata", {}).get("impact") in ("HIGH", "CRITICAL")]
if achados:
    sys.exit(f"REPROVADO: {len(achados)} achados SAST bloqueantes.")
print("APROVADO: SAST sem achados bloqueantes.")

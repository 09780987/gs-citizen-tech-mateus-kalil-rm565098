"""Vincula o arquivo da imagem ao commit e ao ImageID analisado pelo Trivy."""
import hashlib
import json
import os
import re
from pathlib import Path

sha = os.environ["GITHUB_SHA"]
if not re.fullmatch(r"[0-9a-f]{40}", sha):
    raise SystemExit("Commit invalido")
arquivo = Path("reports/imagem.tar")
trivy = json.loads(Path("reports/trivy-image.json").read_text())
image_id = trivy["Metadata"]["ImageID"]
if not re.fullmatch(r"sha256:[0-9a-f]{64}", image_id):
    raise SystemExit("ImageID invalido")
digest = hashlib.sha256()
with arquivo.open("rb") as stream:
    for bloco in iter(lambda: stream.read(2 * 1024 * 1024), b""):
        digest.update(bloco)
manifesto = {
    "rm": "565098", "commit": sha,
    "repository": "09780987/gs-citizen-tech-mateus-kalil-rm565098",
    "image_id": image_id,
    "image_tag": "localhost/ctmarket-release:565098-" + sha,
    "archive_sha256": digest.hexdigest(),
}
Path("reports/deploy-manifest.json").write_text(json.dumps(manifesto, indent=2) + "\n")

"""Rollout rootless na VM 565098, com verificacao de integridade e rollback."""
import argparse
import hashlib
import json
import os
import re
import subprocess
import time
import urllib.request
from pathlib import Path

SERVICO = "ctmarket-producao-rm565098.service"


def executar(*argumentos, timeout=120):
    return subprocess.check_output(argumentos, text=True, stderr=subprocess.STDOUT, timeout=timeout).strip()


def ambiente():
    if os.geteuid() == 0:
        raise RuntimeError("O deploy deve usar o usuario sem privilegios da VM")
    os.environ["XDG_RUNTIME_DIR"] = "/run/user/" + str(os.getuid())
    os.environ["DBUS_SESSION_BUS_ADDRESS"] = "unix:path=" + os.environ["XDG_RUNTIME_DIR"] + "/bus"
    if executar("podman", "info", "--format", "{{.Host.Security.Rootless}}") != "true":
        raise RuntimeError("Podman rootless nao esta disponivel")
    executar("systemctl", "--user", "is-active", "default.target")
    segredo = Path.home() / ".config/ctmarket-rm565098/producao.env"
    if not segredo.is_file() or segredo.stat().st_mode & 0o077:
        raise RuntimeError("Arquivo de ambiente ausente ou com permissoes excessivas")
    return segredo


def saudavel():
    for _ in range(45):
        try:
            with urllib.request.urlopen("http://127.0.0.1:9530/", timeout=2) as resposta:
                if resposta.status == 200 and b"Citizen Tech Market" in resposta.read(1024 * 1024):
                    return True
        except OSError:
            pass
        time.sleep(1)
    return False


def publicar(arquivo, caminho_manifesto, commit):
    segredo = ambiente()
    manifesto = json.loads(caminho_manifesto.read_text())
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise RuntimeError("Commit esperado invalido")
    if manifesto.get("commit") != commit or manifesto.get("rm") != "565098":
        raise RuntimeError("Artefato nao corresponde ao commit/RM desta execucao")
    if manifesto.get("repository") != "09780987/gs-citizen-tech-mateus-kalil-rm565098":
        raise RuntimeError("Repositorio do artefato incorreto")
    tag = "localhost/ctmarket-release:565098-" + commit
    if manifesto.get("image_tag") != tag:
        raise RuntimeError("Tag de release incorreta")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", manifesto.get("image_id", "")):
        raise RuntimeError("ImageID do manifesto invalido")
    digest = hashlib.sha256()
    with arquivo.open("rb") as stream:
        for bloco in iter(lambda: stream.read(2 * 1024 * 1024), b""):
            digest.update(bloco)
    if digest.hexdigest() != manifesto.get("archive_sha256"):
        raise RuntimeError("Arquivo de imagem divergente do manifesto")
    executar("podman", "load", "--input", str(arquivo), timeout=300)
    image_id = executar("podman", "image", "inspect", tag, "--format", "{{.Id}}")
    if image_id.removeprefix("sha256:") != manifesto["image_id"].removeprefix("sha256:"):
        raise RuntimeError("Imagem carregada difere da imagem analisada pelo Trivy")
    quadlet = Path.home() / ".config/containers/systemd/ctmarket-producao-rm565098.container"
    quadlet.parent.mkdir(parents=True, exist_ok=True)
    anterior = quadlet.read_bytes() if quadlet.exists() else None
    conteudo = f"""[Unit]
Description=Citizen Tech Market - Mateus Kalil RM 565098
After=network-online.target

[Container]
Image={manifesto['image_id']}
Pull=never
ContainerName=ctmarket-producao-rm565098
PublishPort=127.0.0.1:9530:8530
EnvironmentFile={segredo}
Environment=PORTA=8530
Environment=LOJA_DB=/dados/market.sqlite
Environment=PYTHONDONTWRITEBYTECODE=1
Volume=ctmarket-dados-rm565098:/dados:U
User=10001:10001
ReadOnly=true
NoNewPrivileges=true
DropCapability=ALL
Tmpfs=/tmp:rw,nosuid,nodev,size=64m
PidsLimit=128

[Service]
Restart=on-failure
RestartSec=2
TimeoutStartSec=120
MemoryMax=768M

[Install]
WantedBy=default.target
"""
    temporario = quadlet.with_suffix(".tmp")
    temporario.write_text(conteudo)
    temporario.replace(quadlet)
    try:
        executar("systemctl", "--user", "daemon-reload")
        executar("systemctl", "--user", "restart", SERVICO, timeout=150)
        if not saudavel():
            raise RuntimeError("Health check de producao nao retornou a aplicacao esperada")
    except Exception:
        if anterior is not None:
            quadlet.write_bytes(anterior)
            executar("systemctl", "--user", "daemon-reload")
            executar("systemctl", "--user", "restart", SERVICO, timeout=150)
        else:
            subprocess.run(["systemctl", "--user", "stop", SERVICO], check=False)
            quadlet.unlink(missing_ok=True)
            executar("systemctl", "--user", "daemon-reload")
        raise
    return {"rm": "565098", "commit": commit, "image_id": manifesto["image_id"],
            "status": "deploy_concluido", "runtime": "podman-rootless", "http": 200, "porta": 9530}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-environment", action="store_true")
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--commit")
    args = parser.parse_args()
    if args.check_environment:
        ambiente()
        print("Runtime rootless e configuracao de producao disponiveis")
    else:
        if not all((args.archive, args.manifest, args.commit)):
            parser.error("Informe --archive, --manifest e --commit")
        try:
            resultado = publicar(args.archive, args.manifest, args.commit)
        except Exception as exc:
            Path("reports").mkdir(exist_ok=True)
            Path("reports/deploy.json").write_text(json.dumps({"rm": "565098", "status": "falha", "erro": str(exc)}, indent=2) + "\n")
            raise
        Path("reports/deploy.json").write_text(json.dumps(resultado, indent=2) + "\n")
        print(json.dumps(resultado))

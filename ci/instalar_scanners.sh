#!/usr/bin/env bash
set -euo pipefail
mkdir -p /tmp/gs-scanners /opt/scanners
cd /tmp/gs-scanners
curl --retry 3 -fsSL -o trivy.tar.gz https://github.com/aquasecurity/trivy/releases/download/v0.76.2/trivy_0.76.2_Linux-64bit.tar.gz
curl --retry 3 -fsSL -o trivy-checksums.txt https://github.com/aquasecurity/trivy/releases/download/v0.76.2/trivy_0.76.2_checksums.txt
mv trivy.tar.gz trivy_0.76.2_Linux-64bit.tar.gz
sha256sum --check --ignore-missing trivy-checksums.txt
tar -xzf trivy_0.76.2_Linux-64bit.tar.gz -C /opt/scanners trivy
curl --retry 3 -fsSL -o gitleaks_8.30.1_linux_x64.tar.gz https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz
curl --retry 3 -fsSL -o gitleaks-checksums.txt https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_checksums.txt
sha256sum --check --ignore-missing gitleaks-checksums.txt
tar -xzf gitleaks_8.30.1_linux_x64.tar.gz -C /opt/scanners gitleaks
/opt/scanners/trivy --version
/opt/scanners/gitleaks version

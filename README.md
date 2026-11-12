# Citizen Tech Market - Mateus Kalil, RM 565098

Repositorio novo para a questao 06. A copia de analise em `/opt/gs/app` e preservada.
As credenciais plantadas, a chave privada e o historico original nao integram este repositorio.
Configuracao sensivel e recebida por variaveis de ambiente.

O workflow `.github/workflows/devsecops-rm565098.yml` possui oito jobs:
build, SAST, segredos, SCA, testes, imagem, DAST e deploy.
O deploy depende dos sete anteriores e so e elegivel em push para `main`.
As actions estao fixadas por SHA; os relatorios de cada job sao publicados mesmo quando o gate reprova.
O token tem leitura de conteudo por padrao; somente a validacao de artefato DAST recebe leitura de Actions.
O deploy tambem utiliza somente leitura de conteudo.

## Gates

- SAST: bloqueia erros de analise, achados ERROR e achados com impacto HIGH/CRITICAL.
- Segredos: Gitleaks examina todo o historico; qualquer segredo reprova. O relatorio de CI e redigido.
- SCA: Trivy examina ambos os requirements.txt e bloqueia HIGH/CRITICAL.
- Testes: pytest gera JUnit XML; falha funcional reprova o job.
- Imagem: Dockerfile e pacotes da imagem sao analisados; HIGH/CRITICAL reprova.
- DAST: exige evidencia ativa concluida e associada ao mesmo commit; risco alto reprova.

O projeto de laboratorio ainda possui vulnerabilidades e dependencias antigas. Assim, a reprovacao dos
gates de seguranca e esperada; nao ha continue-on-error nem supressao de codigos de falha no workflow.

## Integracoes pendentes

O job DAST valida uma evidencia importada e NAO executa uma varredura ativa. Essa parte da questao 06.b
permanece incompleta. O baseline passivo produzido localmente nao atende ao requisito de DAST ativo.
Um produtor externo de evidencia, quando disponivel, deve publicar um artefato
`dast-ativo-<commit_sha>` no mesmo repositorio, com `dast.json` tradicional do ZAP e
`dast-contexto.json` contendo `modo`, `varredura_concluida` e `commit_sha` verdadeiros.
A variavel de repositorio `DAST_REPORT_RUN_ID` identifica a execucao produtora.
O gate bloqueia a ausencia dessa integracao.

O remoto origin aponta para `https://github.com/09780987/gs-citizen-tech-mateus-kalil-rm565098.git`.
O ambiente GitHub `producao` foi configurado com aprovacao obrigatoria de `09780987`,
sem bypass administrativo e com regra de branch limitada a `main`.

## Deploy na VM Debian 13

O executor `mateus-kalil-rm565098-deploy` esta registrado na VM de hostname `565098`,
com o label `deploy-rm565098`, e executa como `ctmarket-deploy`, sem sudo e sem acesso ao Docker do root.
O runtime de producao e Podman rootless. Contribuicoes externas exigem aprovacao para executar workflows.

Depois que os sete jobs anteriores passam e a aprovacao de `producao` e concedida, o deploy baixa
o artefato de imagem do mesmo commit. Confere SHA-256 do arquivo, RM, repositorio, commit e ImageID
analisado pelo Trivy. A imagem de release usa uma tag propria, preservando `ctmarket:565098`, que e
o alvo original da prova.

O rollout utiliza um servico systemd do usuario e escuta em `127.0.0.1:9530` dentro da VM;
o alvo de analise permanece em `127.0.0.1:8530`. Os dados SQLite ficam em um volume persistente.
Chaves de sessao ficam somente no arquivo privado `~/.config/ctmarket-rm565098/producao.env`,
fora do repositorio. O servico utiliza usuario de container sem privilegios, raiz somente leitura,
sem capacidades adicionais e sem novos privilegios.

O deploy exige HTTP 200 e a identificacao da aplicacao; se falhar, restaura a configuracao/imagem
anterior e reprova o job. O rollback nao desfaz migracoes de banco. O resultado e publicado como
`deploy.json`. Enquanto houver achados bloqueantes ou faltar DAST ativo, o job de deploy permanece
impedido; o executor estar pronto nao significa que uma release insegura foi implantada.

## Validacao local realizada

Actionlint 1.7.12: workflow valido.
Pytest 7.4.4 no Python 3.7 da imagem: cinco testes funcionais aprovados.
Gitleaks 8.30.1: arvore e historico do novo repositorio conferidos separadamente.
Podman rootless e ambiente de producao: verificados diretamente na VM.

Fontes oficiais das ferramentas:

- https://github.com/semgrep/semgrep
- https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1
- https://github.com/aquasecurity/trivy/releases/tag/v0.76.2
- https://github.com/rhysd/actionlint/releases/tag/v1.7.12
- https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/add-runners
- https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html

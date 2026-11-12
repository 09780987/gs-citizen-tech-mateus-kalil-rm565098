# Citizen Tech Market - Mateus Kalil, RM 565098

Repositorio novo para a questao 06. A copia de analise em `/opt/gs/app` e preservada.
As credenciais plantadas, a chave privada e o historico original nao integram este repositorio.
Configuracao sensivel e recebida por variaveis de ambiente.

O workflow `.github/workflows/devsecops-rm565098.yml` possui oito jobs:
build, SAST, segredos, SCA, testes, imagem, DAST e deploy.
O deploy depende dos sete anteriores e so e elegivel em push para `main`.
As actions estao fixadas por SHA; os relatorios de cada job sao publicados mesmo quando o gate reprova.
O token tem leitura de conteudo por padrao; somente a validacao de artefato DAST recebe leitura de Actions,
e somente o deploy recebe escrita no registro de pacotes.

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
O segredo de ambiente `DEPLOY_WEBHOOK_URL` deve apontar para um endpoint HTTPS de rollout que receba
um JSON com `image`, `commit` e `rm`. Nenhum valor desse segredo e armazenado no codigo.
Sem essas configuracoes o deploy nao e considerado operacional.

## Validacao local realizada

Actionlint 1.7.12: workflow valido.
Pytest 7.4.4 no Python 3.7 da imagem: cinco testes funcionais aprovados.
Gitleaks 8.30.1: arvore e historico do novo repositorio conferidos separadamente.

Fontes oficiais das ferramentas:

- https://github.com/semgrep/semgrep
- https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1
- https://github.com/aquasecurity/trivy/releases/tag/v0.76.2
- https://github.com/rhysd/actionlint/releases/tag/v1.7.12

---
name: coleta-processual-tjmg
description: Coleta processos do TJMG a partir de números CNJ, direto no eproc e no PJe pelo Chrome, com capa, 20 últimos andamentos, cópia integral e Excel de aba única, em até 3 abas em paralelo. Use sempre que o usuário pedir para consultar, levantar, baixar ou atualizar dados, andamentos, autos ou cópia integral de processos do TJMG ou de uma lista de CNJs com segmento 8.13, mesmo sem citar eproc, PJe ou esta skill. NÃO use para peticionar, tomar ciência, analisar o mérito, outros tribunais ou consulta por DataJud e agregadores.
---

# Coleta processual no TJMG

Entrega, para cada processo: capa, 20 últimos andamentos e cópia integral, lidos do sistema do tribunal no momento da consulta. A saída é um Excel de aba única e uma pasta por processo.

Rotina validada em 2026-11-01 e 2026-11-02 na comarca 0105. Trate seletores e tempos como ponto de partida, porque os sistemas mudam: é por isso que todo lote começa com um teste.

## Regras fixas

Elas protegem a pessoa de efeitos jurídicos e de uso indevido da conta.

- **Credenciais:** login, senha e MFA são digitados pela pessoa, na tela. Não peça no chat, não digite e não grave senhas, códigos, cookies ou tokens. Se a pessoa enviar um código no chat, não o use e oriente a digitar na tela.
- **Somente leitura:** só consulte e baixe. Não peticione, não assine, não tome ciência, não abra prazo e não altere nada.
- **Intimações:** abrir autos com um perfil que representa a parte pode registrar ciência. Faça o cruzamento da etapa 3 antes de abrir qualquer processo.
- **Sem contorno:** CAPTCHA, MFA, sigilo e restrição de acesso são limites. Registre o status e siga, ou peça a ação da pessoa.
- **Só o tribunal:** não use DataJud, Escavador, Jusbrasil, agregadores ou buscadores, nem para complementar.
- **Sem invenção:** campo sem fonte fica vazio, com motivo. A conferência final só recebe hora se o andamento foi relido naquele momento.
- **Dados pessoais:** não salve autos ou planilhas no vault Segundo Cérebro. Não grave CPF no Excel.
- **Registro em nome de terceiros:** os acessos ficam em nome do titular do login, e gerações no eproc enviam e-mail ao endereço cadastrado. Avise antes de começar, principalmente em perfil sem procuração.

## Pré-requisitos

- Extensão Claude in Chrome conectada. Se não estiver, pare e peça para conectar; não troque de navegador sem combinar. O navegador integrado do app não gera o arquivo do PJe.
- Pasta de saída fora do vault. Padrão: `~/Projetos Claude/Coleta processos/<nome do lote>/`.
- `pdfinfo`, `pdftotext`, `pdfunite` e Python com `openpyxl`.

Scripts em `scripts/`, trechos de página em `assets/js/`. Leia `references/eproc.md` antes de operar o eproc, `references/pje.md` antes do PJe e `references/excel-e-status.md` antes de fechar o Excel.

## Fluxo

### 1. Preparar

```bash
python3 scripts/validar_cnj.py <arquivo-ou-lista> --saida <lote>/lista.json
```

Aceita `.txt`, `.csv` e `.xlsx` (com `--coluna`). O script normaliza, valida o dígito, separa duplicados e números fora do TJMG. Informe os excluídos à pessoa.

Antes de operar, combine estes pontos, salvo se a pessoa já os definiu:

- Qual perfil será usado em cada sistema. Com procuração, o eproc libera o download direto. Sem procuração, exige Acesso à Íntegra, com declaração de interesse e MFA por processo.
- Teste com até 5 processos, cobrindo eproc e PJe. Só siga para o lote inteiro depois da aprovação, a menos que a pessoa dispense o teste.

### 2. Autenticar

Abra a tela de login, peça para a pessoa entrar e confirme o perfil logado antes de continuar. Se a sessão expirar, pause e retome do processo em que parou.

### 3. Cruzar intimações

Antes de abrir processos, leia as pendências de cada sistema com o perfil logado:

- **eproc:** listas de citações e intimações pendentes, comum e urgente (`assets/js/cruzar_pendencias_eproc.js`).
- **PJe:** grupo "Apenas pendentes de ciência" do painel de expedientes. Abra o grupo até ver a jurisdição e os processos.

Não clique em nada nessas listas, em especial "Abrir Prazo". Processo com pendência não é aberto: registre `risco_de_intimacao` e avise a pessoa. Se a pendência não puder ser lida, não abra os autos daquele sistema.

Lista vazia não prova que não há prazo: no eproc, uma intimação já aberta sai da lista e continua correndo. Por isso, as etapas 4 e 7 leem o status dos eventos.

### 4. Coletar capa e andamentos

Consulte o **eproc primeiro**, mesmo em números que começam com 5, porque um processo migrado deixa o PJe defasado.

| Resultado no eproc | O que fazer |
|---|---|
| Processo encontrado | Usar os dados do eproc |
| "Processo não encontrado" | Consultar no PJe |
| Segredo de justiça, sem eventos | Registrar `segredo_de_justica` |

Os coletores guardam os dados na memória da aba. Assim, centenas de andamentos não passam pela conversa.

Ao terminar o trabalho de uma aba, exporte uma única vez com `assets/js/exportar_coleta.js`, usando um nome diferente por aba e sistema, como `coleta_pje_aba2`. O Chrome pode bloquear um segundo download automático na mesma aba, sem aviso nos comandos. Confira se o arquivo chegou em `Downloads`. Se não chegar, leia `sessionStorage.coleta` com `javascript_tool` e grave o conteúdo em `<lote>/coletas/`. Não feche a aba antes de confirmar, porque a memória dela se perde.

### 5. Baixar a cópia integral

Siga `references/eproc.md` ou `references/pje.md`. Salve com `assets/js/salvar_pdf_aba.js`, na aba onde o PDF abriu. Em erro 500 do PJe, siga para o próximo e tente de novo uma vez no final.

### 6. Paralelismo

Use até 3 abas por sistema, um sistema por vez. Mais de 3 abas, e eproc e PJe simultâneos, ainda não foram testados.

- Abra as abas de trabalho no início e reutilize cada uma. No eproc, voltar ao painel custa minutos.
- Dê a cada aba processos diferentes e confira o número no título antes de ler ou baixar.
- Mantenha cada bloco de comandos abaixo de 1 minuto. Blocos longos perderam a conexão; para esperas maiores, use vários blocos.
- Se uma leitura da página não responder, não reenvie o comando. Ele pode ser executado quando a página liberar. Consulte as abas com `tabs_context_mcp` e espere.
- Não feche a primeira aba do grupo antes do fim, porque o grupo pode se desfazer e deixar as outras fora de controle.
- Volte para uma aba se houver falhas seguidas, sessão derrubada ou dados trocados.
- O MFA do Acesso à Íntegra é sempre um processo por vez, porque depende da pessoa.

### 7. Conferir

```bash
python3 scripts/conferir_pdfs.py --lote <lote> [--downloads ~/Downloads]
```

O script move os PDFs para `<lote>/<CNJ>/`, une partes, confere abertura, senha, número do processo, páginas e documentos dos últimos andamentos, e atualiza `<lote>/controle.json`. Ele também lista, nas linhas `PRAZO`, os prazos do eproc abertos ou aguardando abertura encontrados no PDF. Avise a pessoa logo, com a parte e a data final.

Depois do download, releia o último andamento de cada processo e grave a hora real em `conferencia_final`. Se ele mudou, colete de novo. Se a lista do PJe mostrar um movimento ausente dos autos, registre a divergência em `motivo` e avise a pessoa. A consulta vale por 1 hora, salvo outro prazo combinado: passou disso, consulte de novo.

### 8. Entregar

```bash
python3 scripts/gerar_excel.py --lote <lote> --saida <lote>/<nome>.xlsx
```

Feche as abas que você abriu e relate em linguagem simples:

- Total recebido, válido e duplicado.
- Concluídos por etapa: capa, andamentos e cópia integral.
- Falhas por tipo e tratamento dado.
- O que exige ação manual, incluindo intimações, prazos abertos e divergências.
- Efeitos do acesso: perfil usado, registros e e-mails.
- Lembrete de que as sessões seguem abertas no Chrome.

## Limites conhecidos

- A verificação de mídias no PJe olha só os 20 últimos andamentos. Mídia mais antiga pode ficar fora do PDF.
- O 2º grau não é consultado. Registre a remessa em `motivo`.
- O painel do eproc pode ficar lento por vários minutos em perfil com muitos processos.
- Um PDF sem erro não prova que cada peça foi lida. A conferência é automática e por amostra de identificadores.

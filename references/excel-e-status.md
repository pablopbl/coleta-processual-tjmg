# Excel, status e arquivos de trabalho

## Estrutura do lote

```
<lote>/
├── lista.json          # números válidos, duplicados e excluídos
├── controle.json       # situação por processo, editada durante a coleta
├── coletas/            # exportações das abas (coleta_eproc*.json, coleta_pje*.json)
├── <CNJ>/              # PDF, partes e mídias
└── <nome>.xlsx
```

## controle.json

Um objeto por CNJ. Os campos são opcionais e substituem o que o script deduz da coleta.

```json
{
  "5000000-00.2026.8.13.0105": {
    "status_capa": "sucesso",
    "status_andamentos": "sucesso",
    "status_copia": "risco_de_intimacao",
    "motivo": "Intimação pendente no perfil logado.",
    "perfil": "Nome do titular (OAB)",
    "esperado": 303,
    "conferencia_final": "02/11/2026 21:16:06",
    "pdf": "5000000-00.2026.8.13.0105_copia_integral.pdf",
    "paginas": 303
  }
}
```

`conferencia_final` só recebe a hora em que o andamento foi relido de fato.

O coletor do eproc já traz o perfil. No PJe, informe `perfil` no `controle.json`, com o nome exibido no topo da página.

## Colunas

Aba única `Processos`, uma linha por processo, nesta ordem:

1. **Capa:** Número CNJ, Tribunal, Sistema, Grau, Órgão julgador, Juiz, Classe, Assuntos, Data de distribuição, Valor da causa, Situação, Partes, Advogados, Segredo de justiça.
2. **Andamentos:** `Data andamento 1`, `Andamento 1`, até o 20. O 1 é o mais recente. Com menos de 20, as colunas ficam vazias.
3. **Controle:** Quantidade de andamentos, Status capa, Status andamentos, Status cópia integral, Motivo da falha, Perfil de acesso, URL de origem, Data e hora da consulta inicial, Data e hora da conferência final, Nome do PDF, Páginas do PDF.

Datas no horário de Brasília. A URL de origem é o endereço do sistema, sem tokens. Em campos com vários valores, use " ; ".

`Juiz` traz o nome exibido pelo sistema. O eproc mostra o nome na capa. A consulta do PJe mostra só o cargo, então a coluna fica vazia e `Motivo da falha` explica. Não preencha com nome deduzido de peças dos autos.

## Status

| Status | Quando usar |
|---|---|
| `sucesso` | Etapa concluída e conferida |
| `parcial` | Parte obtida; explique o que falta |
| `numero_invalido` | Falha no dígito verificador |
| `nao_encontrado` | Ausente no eproc e no PJe |
| `segredo_de_justica` | Sigilo impede o acesso neste perfil |
| `sem_acesso` | O perfil não libera a etapa, ou ela ficou pendente |
| `risco_de_intimacao` | Pendência de ciência; processo não aberto |
| `sessao_expirada` | Sessão caiu e não foi retomada |
| `captcha` | CAPTCHA impediu a etapa |
| `erro_sistema` | Falha do tribunal depois da nova tentativa |
| `desatualizado` | Não foi possível confirmar a posição atual |

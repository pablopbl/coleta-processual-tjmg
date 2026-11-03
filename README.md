# coleta-processual-tjmg

Skill para Claude que coleta processos do TJMG a partir de números CNJ, direto no eproc e no PJe, pelo Chrome. Para cada processo, entrega capa, 20 últimos andamentos e cópia integral, com um Excel de aba única e uma pasta por processo.

## O que ela faz

1. Valida os números CNJ e separa duplicados, inválidos e processos de outros tribunais.
2. Aguarda o login, feito pela própria pessoa, e confere o perfil.
3. Cruza a lista com as intimações pendentes antes de abrir qualquer processo.
4. Coleta capa e andamentos no eproc e, se o processo não estiver lá, no PJe.
5. Baixa as cópias integrais, com até 3 abas por sistema.
6. Confere os PDFs, relê o último andamento e gera o Excel.

## Instalação

Copie esta pasta para o diretório de skills do Claude Code, com o nome `coleta-processual-tjmg`:

```bash
git clone https://github.com/pablopbl/coleta-processual-tjmg ~/.claude/skills/coleta-processual-tjmg
```

## Requisitos

- Claude Code com a extensão [Claude in Chrome](https://chromewebstore.google.com/detail/fcoeoabgfenejglbffodgkkbkcdhcgfn) conectada.
- Conta com acesso regular ao eproc e ao PJe do TJMG.
- `pdfinfo`, `pdftotext` e `pdfunite` (poppler).
- Python 3 com `openpyxl`.

## Uso

Peça algo como:

> Baixe os dados e a cópia integral destes processos do TJMG: 0000000-00.0000.8.13.0000.

A skill começa com um teste de até 5 processos e só segue para o lote com aprovação.

## Uso responsável

- **Credenciais:** login, senha e MFA são sempre digitados pela pessoa, na tela. A skill não pede nem guarda esses dados.
- **Somente leitura:** ela só consulta e baixa. Não peticiona, não assina e não toma ciência.
- **Intimações:** abrir autos com um perfil que representa a parte pode registrar ciência. Por isso, a skill cruza as pendências antes e não abre os processos com pendência. No eproc, uma intimação já aberta sai da lista de pendências, então a skill também lê o status dos eventos e dos PDFs. A verificação não substitui o controle de prazos do escritório.
- **Registro de acesso:** os acessos ficam em nome do titular do login, que precisa ter autorizado o uso. Algumas gerações enviam e-mail ao endereço cadastrado.
- **Regras do tribunal:** confira as regras de acesso automatizado do tribunal antes de usar em volume.
- **Dados pessoais:** os autos têm dados de terceiros. Trate as saídas de acordo com a LGPD e não as publique.
- **Sem contorno:** CAPTCHA, MFA, sigilo e restrições de acesso são limites, não obstáculos a superar.

## Limites conhecidos

- Testada no TJMG, comarca 0105, em novembro de 2026. Os sistemas mudam, então seletores e tempos podem precisar de ajuste.
- Não consulta o 2º grau e não foi testada em outros tribunais.
- O paralelismo foi testado com até 3 abas e um sistema por vez.
- A conferência dos PDFs é automática e não substitui a leitura das peças. Revise o resultado antes de usá-lo em uma decisão.

## Licença

[MIT](LICENSE)

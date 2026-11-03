# PJe do TJMG, pelo Chrome

Pesquisa: `https://pje.tjmg.jus.br/pje/Processo/ConsultaProcesso/listView.seam`

Login e senha valem para quem está cadastrado nos autos. Um aviso do próprio PJe informa que terceiros só acessam a íntegra com certificado digital.

## Pendências de intimação

1. Abra `https://pje.tjmg.jus.br/pje/Painel/painel_usuario/advogado.seam`.
2. Clique em `#tabExpedientes_lbl`. A lista pode levar cerca de 1 minuto.
3. Abra o grupo "Apenas pendentes de ciência" até ver a jurisdição.
4. Se a jurisdição coincidir com a do lote, abra o agrupador para ver o número. Não abra o documento.

Se o painel não carregar, não abra autos do PJe nesse lote.

## Abrir os autos

Rode `assets/js/abrir_autos_pje.js` na página de pesquisa, trocando `__CNJ__` pelo formato `NNNNNNN-DD.AAAA` e `__ORIGEM__` pelos 4 dígitos finais. Ele preenche a pesquisa e entra nos autos. Roda solto, então aguarde cerca de 15 segundos e confira o número no título da aba.

O endereço dos autos vale só para a sessão. Sempre passe pela pesquisa.

## Coletar

Nos autos, rode `assets/js/coletor_pje.js`. Ele lê "Mais detalhes", os polos e até 20 movimentos da linha do tempo, omitindo CPFs. "Mais detalhes" traz o cargo judicial, não o nome do juiz.

Compare com a coluna "Última moviment." da pesquisa. Em um caso, a lista mostrou um movimento que não aparecia nos autos. Registre essa divergência, sem deduzir a data ou o conteúdo.

## Cópia integral

1. Rode `assets/js/pedir_autos_pje.js`. Ele abre o formulário "Download autos do processo" e clica em Download, com as opções padrão.
2. O PDF abre em uma aba nova, em `s3-pjedocumentos.tjmg.jus.br`. Costuma levar menos de 1 minuto; processos maiores podem levar mais.
3. Salve nessa aba com `assets/js/salvar_pdf_aba.js` e feche-a.
4. Se aparecer "Falha ao gerar PDF ... HttpStatus: 500", anote o protocolo, siga para o próximo e tente de novo uma vez no final. Em 4 dos 4 casos observados, a nova tentativa funcionou. Se falhar outra vez, registre `erro_sistema` com o protocolo.

A busca por `window.__u` no script só captura o endereço que o próprio PJe tentaria abrir. Não altere esse endereço nem o grave em arquivos.

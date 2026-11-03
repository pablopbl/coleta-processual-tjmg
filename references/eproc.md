# eproc do TJMG, pelo Chrome

Endereço: `https://eproc1g.tjmg.jus.br/eproc/`

## Entrada

1. Abra o endereço em uma aba nova e peça o login à pessoa.
2. Depois do login, o Painel do Advogado carrega. Em perfil com muitos processos, ele pode bloquear a automação por vários minutos.
3. Se `javascript_tool` não responder, não reenvie comandos. Espere e consulte o título da aba com `tabs_context_mcp`.
4. Confira o perfil em `#nav-profile`.
5. A partir daí, pesquise dentro dos processos, sem voltar ao painel.

## Pendências de intimação

No painel, localize com `find` os links de "Processos pendentes de citação/intimação" e da linha "Urgentes", e navegue até eles. Na lista, rode `assets/js/cruzar_pendencias_eproc.js`, trocando `__LISTA__` pelos CNJs do lote. Não use os botões da página. A lista pagina a cada 300 processos, então confira todas as páginas se houver mais.

Essa lista só mostra o que aguarda abertura. Uma intimação já aberta sai dela e o prazo continua correndo, então lista vazia não significa ausência de prazo. As próximas etapas leem o status dos eventos: veja `prazosAbertos` no coletor e `PRAZO` no conferidor.

## Pesquisar processo

Rode `assets/js/pesquisar_eproc.js`, trocando `__CNJ20__` pelos 20 dígitos. Aguarde cerca de 7 segundos. Evite clicar por coordenada na barra superior, porque o link do portal jus.br fica ao lado do campo.

"Processo não encontrado" no texto da página significa ir ao PJe. Esse retorno é normal; repita um número conhecido se muitos vierem em sequência, para descartar bloqueio.

## Coletar

Na página do processo, rode `assets/js/coletor_eproc.js`. Ele abre "Informações Adicionais", aguarda, lê capa, juiz, partes, assuntos e até 20 eventos, omite CPFs e guarda na memória da aba. Se `total` vier 0 com "Segredo de Justiça" na página, registre `segredo_de_justica`.

Se `prazosAbertos` ou `prazosAguardando` vierem acima de zero, leia nos eventos de quem é o prazo e a data final, e avise a pessoa logo. Não espere o relatório final, porque o prazo pode estar perto de vencer.

## Cópia integral

**Se existir o botão "Download Completo" na página:** o perfil tem acesso. Siga para a geração.

**Se só existir "Acesso íntegra do processo":** é vista sem procuração.

1. Clique, leia a tela e pare.
2. A pessoa decide se declara interesse e digita o MFA.
3. Depois da confirmação, confira se o botão "Download Completo" apareceu.

**Geração:**

1. Clique em "Download Completo". Se a tela informar arquivo ainda válido, por até 72 horas, ele aparece direto.
2. Se aparecer `#btnGerar`, clique nele com as opções padrão. Leia antes o e-mail exibido, porque ele recebe o aviso.
3. A página de status recarrega sozinha. Em geral leva de 20 segundos a pouco mais de 1 minuto.
4. Leia o status e anote o total de páginas em `esperado` no `controle.json`, além das contagens de falhas e de "Arquivos de áudio/vídeo não convertidos".
5. Localize "BAIXAR ARQUIVO" com `find` e clique com `computer`, pelo `ref`. Um clique por script não abre a aba. Com o clique real, o PDF abre em aba própria e a aba de trabalho fica na mesma página, com a pesquisa disponível.
6. Salve na aba do PDF com `assets/js/salvar_pdf_aba.js` e feche-a.
7. Arquivos acima de 50 MB vêm em partes (`BAIXAR ARQUIVO PARTE n`). Salve todas: o conferidor une.

## Mídias

Se o status indicar áudio ou vídeo fora do PDF:

1. Procure com `find` os links de documento "do tipo" mp4, mpeg, mp3, ogg ou wav. Não confie só no nome: uma mídia pode se chamar `DOCCOMPROV2`, e o mesmo arquivo pode aparecer em mais de um evento e ser contado duas vezes.
2. Clique em cada link pelo `ref` e confira se o arquivo chegou em `Downloads`.
3. Mova para `<lote>/<CNJ>/evento_<n>_<documento>.<ext>`.
4. Se o número de mídias encontradas for menor que o informado pelo eproc, registre `parcial` e o motivo.

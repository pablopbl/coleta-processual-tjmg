// Pesquisa um processo no eproc, na mesma aba. Troque __CNJ20__ pelos 20 dígitos.
(() => {
  const e = document.getElementById('txtNumProcessoPesquisaRapida');
  if (!e) return { erro: 'campo de pesquisa ausente', titulo: document.title.slice(0, 60) };
  e.value = '__CNJ20__';
  e.form.querySelector('button[type=submit]').click();
  return 'pesquisando';
})()

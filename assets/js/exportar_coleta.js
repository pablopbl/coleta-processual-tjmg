// Exporta para Downloads o que os coletores guardaram nesta aba. Troque __NOME__ por coleta_eproc_aba1, por exemplo.
(() => {
  const d = sessionStorage.getItem('coleta') || '{}';
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([d], { type: 'application/json' }));
  a.download = '__NOME__.json';
  document.body.appendChild(a);
  a.click();
  a.remove();
  return { processos: Object.keys(JSON.parse(d)).length, tamanho: d.length };
})()

// Na lista de pendentes do eproc, cruza com os CNJs do lote. Só leitura: não clique nos botões da página.
(() => {
  const lote = __LISTA__; // array de CNJs no formato completo
  const t = document.body.innerText;
  const nums = [...new Set(t.match(/\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}/g) || [])];
  return { titulo: document.title.slice(0, 70), registros: (t.match(/\((\d+) registros?\)/) || [])[1], lidos: nums.length, pendentesDoLote: nums.filter(n => lote.includes(n)) };
})()

// Na aba onde o PDF abriu, salva em Downloads com nome padronizado.
const u = decodeURIComponent(location.pathname + location.search);
const pje = u.match(/(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})-\d+-\d+-processo\.pdf/);
const eproc = u.match(/MG-(\d{20})-.*PARTE_(\d+)/);
let nome = null;
if (pje) nome = pje[1] + '_copia_integral.pdf';
if (eproc) { const s = eproc[1]; nome = `${s.slice(0, 7)}-${s.slice(7, 9)}.${s.slice(9, 13)}.${s[13]}.${s.slice(14, 16)}.${s.slice(16)}_parte_${eproc[2]}.pdf`; }
if (!nome) { ({ erro: 'não é o PDF esperado', titulo: document.title.slice(0, 60) }); } else {
  const r = await fetch(location.href);
  const b = await r.blob();
  const a = document.createElement('a');
  a.href = URL.createObjectURL(b);
  a.download = nome;
  document.documentElement.appendChild(a);
  a.click();
  a.remove();
  await new Promise(x => setTimeout(x, 2500));
  ({ nome, status: r.status, tamanho: b.size, tipo: b.type });
}

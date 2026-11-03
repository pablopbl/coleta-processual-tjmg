// Lê a página do processo no eproc e guarda na memória da aba. Não abre documentos.
document.getElementById('legInfAdicional')?.click();
await new Promise(r => setTimeout(r, 2500));
(() => {
  const c = s => (s || '').replace(/\s+/g, ' ').trim();
  const mask = s => s.replace(/\d{3}\.\d{3}\.\d{3}-\d{2}/g, 'CPF');
  const num = (document.title.match(/\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}/) || [])[0];
  const corpo = c(document.body.innerText);
  if (!num) return { ok: false, naoEncontrado: /Processo não encontrado/.test(corpo), titulo: document.title.slice(0, 70) };
  const inf = c(document.getElementById('fldInformacoesAdicionais_content')?.textContent);
  const t = document.getElementById('tblPartesERepresentantes');
  const cells = t ? [...t.querySelectorAll('td')].map(x => mask(c(x.textContent).replace(/\.item-barra[^}]*\}/, '')).trim()) : [];
  const ev = [...document.querySelectorAll('tr[id^=trEvento]')].map(r => [c(r.cells[0].textContent).split(' ')[0], c(r.cells[1].textContent), mask(c(r.cells[2].textContent))]);
  const midia = [...document.querySelectorAll('tr[id^=trEvento] a.infraLinkDocumento')].filter(a => /udio|v[ií]deo|m[ií]dia/i.test((a.title || '') + ' ' + a.textContent)).map(a => c(a.textContent) + ' ' + (a.title || '').split('\n').pop());
  const r = {
    hora: new Date().toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' }),
    capa: c(document.getElementById('fldCapa')?.innerText),
    ass: [...document.querySelectorAll('#conteudoAssuntos2 tr')].slice(1).map(x => c(x.cells[1]?.textContent)),
    valor: (inf.match(/Valor da Causa: ?(R\$ ?[\d.,]+)/) || [])[1],
    sigilo: (inf.match(/Nível de Sigilo do Processo: ?(.*?\))/) || [])[1] || (corpo.match(/Segredo de Justiça \(Nível \d\)/) || [])[0],
    heads: t ? [...t.querySelectorAll('th')].map(x => c(x.textContent)) : [],
    cells,
    total: ev.length,
    docs: document.querySelectorAll('a.infraLinkDocumento').length,
    downloadCompleto: [...document.querySelectorAll('button')].some(b => /Download Completo/.test(b.textContent)),
    acessoIntegra: [...document.querySelectorAll('a')].some(a => /Acesso íntegra/.test(a.textContent)),
    perfil: c(document.getElementById('nav-profile')?.textContent).split(' MG')[0].slice(0, 60),
    midia,
    ev: ev.slice(0, 20)
  };
  const d = JSON.parse(sessionStorage.getItem('coleta') || '{}');
  d[num] = r;
  sessionStorage.setItem('coleta', JSON.stringify(d));
  return { ok: true, num, total: ev.length, ultimo: ev[0] && ev[0][1], docs: r.docs, download: r.downloadCompleto, integra: r.acessoIntegra, sigilo: r.sigilo, midia: midia.length, prazosAbertos: ev.filter(e => /Status:ABERTO/.test(e[2])).length, guardados: Object.keys(d).length };
})()

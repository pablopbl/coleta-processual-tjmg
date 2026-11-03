// Lê os autos no PJe e guarda na memória da aba. Não abre expedientes.
(() => {
  const c = s => (s || '').replace(/\s+/g, ' ').trim();
  const num = (document.title.match(/\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}/) || [])[0];
  if (!num) return { ok: false, titulo: document.title.slice(0, 60) };
  const mask = s => s.replace(/\d{3}\.\d{3}\.\d{3}-\d{2}/g, 'CPF');
  const det = c(document.querySelector('#maisDetalhes')?.textContent);
  const g = (a, b) => { const m = det.match(new RegExp(a + ' (.*?) ' + b)); return m ? m[1] : null; };
  const a = document.querySelector('#poloAtivo'), p = document.querySelector('#poloPassivo');
  const box = document.querySelector('#divTimeLine\\:eventosTimeLineElement') || [...document.querySelectorAll('div')].find(d => d.id && /timeline|eventosTimeLine|divTimeLine/i.test(d.id));
  const raw = (box || document.body).innerText.split('\n').map(c).filter(Boolean);
  const mes = { jan: '01', fev: '02', mar: '03', abr: '04', mai: '05', jun: '06', jul: '07', ago: '08', set: '09', out: '10', nov: '11', dez: '12' };
  let d = null, buf = [];
  const ev = [];
  for (const l of raw) {
    const m = l.match(/^(\d{2}) (jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez) (\d{4})$/);
    if (m) { d = m[1] + '/' + mes[m[2]] + '/' + m[3]; buf = []; continue; }
    if (/^\d{2}:\d{2}$/.test(l)) { if (d && buf.length) ev.push([d + ' ' + l, mask(buf.join(' '))]); buf = []; continue; }
    if (d && !/^ÍCONE/i.test(l)) buf.push(l);
  }
  const r = {
    hora: new Date().toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' }),
    classe: g('Classe judicial', 'Assunto'), assunto: g('Assunto', 'Jurisdição'), autuacao: g('Autuação', 'Última distribuição'),
    valor: g('Valor da causa', 'Segredo de justiça'), segredo: g('Segredo de justiça\\?', 'Justiça gratuita'), orgao: g('Órgão julgador', 'Cargo judicial'),
    ativo: a ? mask(c(a.textContent)) : null, passivo: p ? mask(c(p.textContent)) : null,
    ultimaLista: sessionStorage.getItem('ultimaMov'), total: ev.length, ev: ev.slice(0, 20)
  };
  const dd = JSON.parse(sessionStorage.getItem('coleta') || '{}');
  dd[num] = r;
  sessionStorage.setItem('coleta', JSON.stringify(dd));
  return { ok: true, num, total: ev.length, ultimo: ev[0], ultimaLista: r.ultimaLista, orgao: (r.orgao || '').slice(0, 40), guardados: Object.keys(dd).length };
})()

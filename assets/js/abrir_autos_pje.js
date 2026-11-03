// Na pesquisa do PJe, localiza o processo e entra nos autos. Troque __CNJ__ por NNNNNNN-DD.AAAA.
window.__u = [];
window.open = function (u) { window.__u.push(String(u)); return null; };
(async () => {
  const sl = ms => new Promise(r => setTimeout(r, ms));
  const n = '__CNJ__';
  const m = n.match(/(\d{7})-(\d{2})\.(\d{4})/);
  const set = (i, v) => { const e = document.getElementById(i); e.value = v; e.dispatchEvent(new Event('change', { bubbles: true })); };
  set('fPP:numeroProcesso:numeroSequencial', m[1]);
  set('fPP:numeroProcesso:numeroDigitoVerificador', m[2]);
  set('fPP:numeroProcesso:Ano', m[3]);
  set('fPP:numeroProcesso:NumeroOrgaoJustica', '__ORIGEM__');
  document.getElementById('fPP:searchProcessos').click();
  await sl(7000);
  const r = [...document.querySelectorAll('#fPP\\:processosTable tbody tr')].find(x => x.textContent.includes(n));
  if (!r) { window.__erro = 'sem linha'; return; }
  sessionStorage.setItem('ultimaMov', r.cells[r.cells.length - 1].innerText.trim());
  [...r.querySelectorAll('a')].find(x => /\d{7}-\d{2}/.test(x.textContent)).click();
  await sl(4000);
  if (window.__u[0]) location.href = window.__u[0];
})();
'iniciado'

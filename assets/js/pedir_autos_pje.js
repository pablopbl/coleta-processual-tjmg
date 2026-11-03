// Nos autos do PJe, pede a cópia integral com as opções padrão. O PDF abre em outra aba.
(async () => {
  const sl = ms => new Promise(r => setTimeout(r, ms));
  [...document.querySelectorAll('a')].find(x => x.title === 'Download autos do processo').click();
  await sl(1200);
  [...document.querySelectorAll('input[type=button],input[type=submit]')].find(x => x.value === 'Download' && x.offsetParent).click();
})();
document.title.slice(0, 26)

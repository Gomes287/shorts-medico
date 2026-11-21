/* shorts-medico — runtime pequeno. Tudo depende só do tempo da timeline (o render pede quadros fora de ordem). */
(function () {
  const SM = {};
  const fmt = (v, casas) => new Intl.NumberFormat('pt-BR', { minimumFractionDigits: casas, maximumFractionDigits: casas }).format(v);
  const contadores = [];   // {el, de, ate, t0, dur, casas, prefixo, sufixo}
  SM.contador = (sel, o) => { const el = document.querySelector(sel); if (el) contadores.push({ el, ...o }); };
  const ease = (x) => 1 - Math.pow(1 - x, 3);
  SM.tick = (t) => {
    for (const c of contadores) {
      const p = Math.max(0, Math.min(1, (t - c.t0) / c.dur));
      c.el.textContent = (c.prefixo || '') + fmt(c.de + (c.ate - c.de) * ease(p), c.casas || 0) + (c.sufixo || '');
    }
  };
  SM.ligar = (tl) => { tl.eventCallback('onUpdate', () => SM.tick(tl.time())); SM.tick(0); };
  window.SM = SM;
})();

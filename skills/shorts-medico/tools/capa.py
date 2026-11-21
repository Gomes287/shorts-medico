"""Capa (miniatura) do Short — vai no campo Miniatura do YouTube Studio e na capa do Reels. Mesmo layout em toda a série.
uso:
  capa.py <projeto> <nome> --t 3.4          usa o quadro do médico no tempo t (escolha em work/capa_candidatos.jpg)
  capa.py --previa <saida.png> [--titulo "LINHA 1|LINHA 2"]   prévia das cores do perfil com uma silhueta (configuração)
"""
import sys, json, shutil, argparse, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import *
from build import css, titulo_html, PLANOS

ap = argparse.ArgumentParser(); ap.add_argument('projeto', nargs='?'); ap.add_argument('nome', nargs='?')
ap.add_argument('--t', type=float, default=None); ap.add_argument('--previa'); ap.add_argument('--titulo')
a = ap.parse_args(); p = carregar_perfil(obrigatorio=not a.previa)

if a.previa:
    work = Path.home() / '.cache/shorts-medico/previa'; rot = {'titulo_capa': (a.titulo or 'O ERRO QUE EU MAIS|VEJO NO CONSULTÓRIO').split('|')}
    pessoa = ('<svg class="abs" style="left:240px;top:640px" width="600" height="1280" viewBox="0 0 600 1280">'
              '<circle cx="300" cy="230" r="200" fill="rgba(255,255,255,.85)"/><path d="M20 1280 V760 Q20 470 300 470 Q580 470 580 760 V1280 Z" fill="rgba(255,255,255,.85)"/></svg>')
else:
    P = Path(a.projeto).resolve(); work = P / 'work/capa'; rot = roteiro(P)
    r = json.load(open(P / 'work/rosto.json'))
    t = a.t if a.t is not None else 0.5
    work.mkdir(parents=True, exist_ok=True)
    run(['ffmpeg', '-v', 'error', '-y', '-c:v', 'libvpx-vp9', '-ss', str(t), '-i', str(P / 'assets/video/medico.webm'), '-frames:v', '1', str(work / 'medico.png')])
    fh, tx, ty = PLANOS['capa']; s = fh * H / r['h']; x = tx - r['cx'] * s; y = ty * H - r['cy'] * s
    pessoa = f'<img class="abs" src="medico.png" style="left:0;top:0;width:{W}px;height:{H}px;transform-origin:0 0;transform:translate({x:.1f}px,{y:.1f}px) scale({s:.4f});filter:drop-shadow(0 30px 40px rgba(0,0,0,.35));-webkit-mask-image:linear-gradient(to bottom,#000 70%,transparent 97%);mask-image:linear-gradient(to bottom,#000 70%,transparent 97%)">'
work.mkdir(parents=True, exist_ok=True); (work / 'assets/fonts').mkdir(parents=True, exist_ok=True)
for f in (SK / 'kit/fonts').glob('*.woff2'): shutil.copy(f, work / 'assets/fonts/')
(work / 'assets/vendor').mkdir(exist_ok=True); shutil.copy(gsap(), work / 'assets/vendor/gsap.min.js')
arroba = f'<div class="idpill" style="visibility:visible;top:1660px;transform:translateX(-50%)">{p.get("arroba") or linha_id(p)}</div>' if (p.get('arroba') or p.get('nome')) else ''
doc = f"""<!doctype html><html lang="pt-BR"><head><meta charset="UTF-8"><script src="assets/vendor/gsap.min.js"></script><style>{css(p)}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="1" data-width="{W}" data-height="{H}">
<div class="mundo m-primaria" style="visibility:visible"><div class="grade"></div><div class="luz"></div><div class="vinheta"></div></div>
{pessoa}{titulo_html(rot, fonte=p.get('fonte_titulo', 'Anton'))}{arroba}</div>
<script>const tl=gsap.timeline({{paused:true}});tl.set("#root",{{opacity:1}},0);window.__timelines={{main:tl}};</script></body></html>"""
(work / 'index.html').write_text(doc, encoding='utf-8')
(work / 'package.json').write_text('{"name":"capa","private":true,"type":"module"}')
snap = work / 'snap'
run(['npx', '--yes', HF, 'snapshot', str(work), '--no-end', '--at', '0.5', '-o', str(snap)], capture_output=True)
png = next(iter(sorted(snap.glob('*.png'))), None) or sys.exit('o snapshot não gerou imagem')
dest = Path(a.previa) if a.previa else P / 'entrega' / f'{a.nome}_capa.png'
dest.parent.mkdir(parents=True, exist_ok=True); shutil.copy(png, dest); print('capa:', dest)

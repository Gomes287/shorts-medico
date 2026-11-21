"""Cria a pasta de um Short novo.  uso: novo_projeto.py <pasta>
Estrutura: assets/ (vendor, kit, fontes, sons, video, audio, img) · work/ · renders/ · entrega/
"""
import sys, shutil, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import *

P = Path(sys.argv[1]).expanduser().resolve()
for d in ('assets/vendor', 'assets/kit', 'assets/fonts', 'assets/sfx', 'assets/video', 'assets/audio', 'assets/img', 'work', 'renders', 'entrega'):
    (P / d).mkdir(parents=True, exist_ok=True)
shutil.copy(gsap(), P / 'assets/vendor/gsap.min.js')
shutil.copy(SK / 'motor/shorts.js', P / 'assets/kit/')
for f in (SK / 'kit/fonts').glob('*.woff2'): shutil.copy(f, P / 'assets/fonts/')
for f in (SK / 'kit/sfx').iterdir(): shutil.copy(f, P / 'assets/sfx/')
(P / 'package.json').write_text(json.dumps({'name': P.name.lower().replace(' ', '-'), 'private': True, 'type': 'module'}, indent=1))
(P / 'hyperframes.json').write_text(json.dumps({'paths': {'assets': 'assets'}, 'media': {'autoProxy': True}}, indent=1))
ex = SK / 'exemplo/roteiro.json'
if not (P / 'work/roteiro.json').exists() and ex.exists():
    shutil.copy(ex, P / 'work/roteiro.json')
print('projeto criado:', P)

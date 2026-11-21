"""Perfil do médico (uma vez por pessoa): identificação CFM, cores e fonte.
uso:
  perfil.py mostrar                       mostra o perfil
  perfil.py definir '<json parcial>'      junta no perfil, ex.: '{"nome":"Ana Souza","crm":"123456","uf":"SP"}'
  perfil.py paleta <imagem>               tira as cores principais de um logo/print e sugere primaria/acento
  perfil.py checar                        diz o que falta para gerar um vídeo
Arquivo: ~/.config/shorts-medico/perfil.json (só no computador da pessoa).
"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import *


def paleta(img):
    import numpy as np
    from PIL import Image
    a = np.asarray(Image.open(img).convert('RGB').resize((160, 160))).reshape(-1, 3).astype(float)
    rng = np.random.default_rng(3); c = a[rng.choice(len(a), 6, replace=False)]
    for _ in range(25):
        d = ((a[:, None, :] - c[None]) ** 2).sum(-1); lab = d.argmin(1)
        c = np.array([a[lab == k].mean(0) if (lab == k).any() else c[k] for k in range(len(c))])
    cont = np.bincount(lab, minlength=len(c))
    hexs = []
    for k in cont.argsort()[::-1]:
        r, g, b = c[k]; mx, mn = max(r, g, b), min(r, g, b)
        sat = (mx - mn) / (mx + 1e-6); lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        hexs.append(dict(hex='#%02X%02X%02X' % (int(r), int(g), int(b)), parte=round(cont[k] / len(a) * 100), sat=round(sat, 2), lum=round(lum, 2)))
    viv = sorted([h for h in hexs if h['sat'] > 0.25 and 0.15 < h['lum'] < 0.85], key=lambda h: -h['parte'])
    print('cores encontradas (da mais presente para a menos):')
    for h in hexs:
        print(f"  {h['hex']}  {h['parte']:>3}%  saturação {h['sat']}  luminosidade {h['lum']}")
    if viv:
        print('sugestão: primaria', viv[0]['hex'], '· acento', (viv[1]['hex'] if len(viv) > 1 else '(escolha um contraste)'))


cmd = sys.argv[1] if len(sys.argv) > 1 else 'mostrar'
if cmd == 'mostrar':
    p = carregar_perfil(obrigatorio=False)
    print(json.dumps(p, indent=1, ensure_ascii=False))
    print('\nidentificação nos vídeos:', linha_id(p) if p.get('nome') else '(falta nome/CRM)')
elif cmd == 'definir':
    p = carregar_perfil(obrigatorio=False); novo = json.loads(sys.argv[2])
    for k, v in novo.items():
        if isinstance(v, dict) and isinstance(p.get(k), dict): p[k].update(v)
        else: p[k] = v
    salvar_perfil(p); print('perfil salvo em', PERFIL); print('identificação:', linha_id(p))
elif cmd == 'paleta':
    paleta(sys.argv[2])
elif cmd == 'checar':
    p = carregar_perfil(); f = faltando_perfil(p)
    print('identificação:', linha_id(p))
    print('falta:', ', '.join(f) if f else 'nada. Pronto para gerar.')
    sys.exit(1 if f else 0)
else:
    print(__doc__)

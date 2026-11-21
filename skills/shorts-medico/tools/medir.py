"""Mede o Short contra as metas de retenção (guia "Do 1.800 aos 392 mil" + regras da skill) e diz o que trocar.
uso: medir.py <projeto> <video.mp4>
"""
import sys, json, subprocess
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import *

P = Path(sys.argv[1]); V = Path(sys.argv[2])
ev = json.load(open(P / 'work/eventos.json')); words = json.load(open(P / 'work/words.json', encoding='utf-8'))
D = duracao(V)
# movimento quadro a quadro (10 fps, 108x192)
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(V), '-vf', 'fps=10,scale=216:384', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], capture_output=True, check=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, 384, 216).astype(np.int16)
dif = np.abs(np.diff(fr, axis=0)).mean((1, 2))
parado = dif < 0.35
maior, cur = 0, 0
for p in parado:
    cur = cur + 1 if p else 0; maior = max(maior, cur)
# som: buracos e nível entre falas
SR = 16000
au = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', str(V), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32)
jan = int(0.05 * SR); n = len(au) // jan
db = 20 * np.log10(np.sqrt((au[:n * jan].reshape(n, jan) ** 2).mean(1)) + 1e-9)
fala = np.zeros(n, bool)
for w in words: fala[int(w['start'] / 0.05):int(w['end'] / 0.05) + 1] = True
fala = fala[:n]
sil, cur = 0, 0
for d in db[:int((words[-1]['end']) / 0.05)]:
    cur = cur + 1 if d < -45 else 0; sil = max(sil, cur)
entre = float(np.median(db[fala]) - np.median(db[~fala])) if (~fala).any() else 0.0
novid = len(ev['eventos']) / D * 10
metas = [
    ('coisas novas a cada 10 s', f'{novid:.1f}', novid >= 13, '≥ 13', 'mais cenas curtas, punch-in (^palavra), barras/ícones um a um'),
    ('quadros parados', f'{parado.mean() * 100:.0f}%', parado.mean() <= 0.30, '≤ 30%', 'deriva de câmera, troca de enquadramento, elementos entrando'),
    ('maior trecho parado', f'{maior / 10:.1f} s', maior / 10 <= 1.6, '≤ 1,6 s', 'achar o trecho na folha e colocar uma entrada nele'),
    ('rosto em close', f'{ev["close_s"] / D * 100:.0f}%', 0.25 <= ev['close_s'] / D <= 0.55, '25–55%', 'mais ou menos cenas "rosto" em close'),
    ('cabeça no quadro 0', f'{ev["cabeca_quadro0"] * 100:.0f}% da altura', 0.37 <= ev['cabeca_quadro0'] <= 0.47, '37–47%', 'plano "capa" em build.py'),
    ('maior silêncio na fala', f'{sil * 0.05:.2f} s', sil * 0.05 <= 0.3, '≤ 0,3 s', 'mixar.py (trilha mais alta entre falas)'),
    ('som entre falas abaixo da voz', f'{entre:.1f} dB', 3 <= entre <= 9, '3–9 dB', 'mixar.py --entre'),
    ('duração', f'{D:.1f} s', 40 <= D <= 60, '45–57 s ideal', 'cortar frase que não acrescenta / abrir mais uma curiosidade'),
]
print(f'MEDIDAS de {V.name}')
ok = True
for nome, val, passou, alvo, dica in metas:
    ok &= passou
    print(f'  {"OK " if passou else "!! "} {nome:<32} {val:<16} meta {alvo}' + ('' if passou else f'  → {dica}'))
print('PASSOU em tudo.' if ok else 'Ajuste os itens marcados com !! e renderize de novo.')
json.dump({m[0]: m[1] for m in metas}, open(P / 'work/medidas.json', 'w'), indent=1, ensure_ascii=False)

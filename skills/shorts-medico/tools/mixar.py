"""Som do Short: voz (do vídeo) + trilha por baixo SEM buraco de silêncio + efeitos suaves nas trocas.
uso: mixar.py <projeto> [--entre -6] [--sob -14]
- Trilha: assets/audio/musica.mp3|wav se a pessoa tiver uma com direito de uso; senão gera por código (trilha.py).
- Entre as falas a trilha fica ~4 dB abaixo do nível da voz (metas medidas: 3,5–5,8 dB); sob a fala, ~14 dB abaixo.
- Efeitos: work/som.json (o build.py escreve), pico de cada efeito 1 quadro depois da imagem.
Grava assets/audio/mix.wav (48 kHz estéreo). A masterização final (-14 LUFS) é no render.py.
"""
import sys, json, argparse, subprocess
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import *

ap = argparse.ArgumentParser(); ap.add_argument('projeto'); ap.add_argument('--entre', type=float, default=-4); ap.add_argument('--sob', type=float, default=-14)
a = ap.parse_args(); P = Path(a.projeto); SR = 48000
cfg = json.load(open(P / 'work/som.json')); D = cfg['duracao']; N = int(D * SR)
words = json.load(open(P / 'work/words.json', encoding='utf-8'))


def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    return np.vstack([x, np.zeros((max(0, N - len(x)), 2), np.float32)])[:N]


rms = lambda x: float(np.sqrt(np.mean(x ** 2)) + 1e-9)
voz = load(P / 'assets/audio/vo.wav')
fala = np.zeros(N, bool)
for w in words: fala[int(max(0, w['start'] - 0.05) * SR):int(min(D, w['end'] + 0.08) * SR)] = True
nivel_voz = rms(voz[fala]) if fala.any() else rms(voz)

musica = next((f for f in (P / 'assets/audio/musica.mp3', P / 'assets/audio/musica.wav') if f.exists()), None)
if not musica:
    run([sys.executable, str(SK / 'tools/trilha.py'), str(P), str(D), '--titulo', str(round(max(1.0, words[-1]['end'] - 2.0), 2))], capture_output=True)
    musica = P / 'assets/audio/trilha.wav'
trilha = load(musica)
trilha *= nivel_voz / rms(trilha[~fala] if (~fala).any() else trilha) * 10 ** (a.entre / 20)
# ducking suave sob a fala (ataque 60 ms, soltura 150 ms)
alvo = np.where(fala, 10 ** ((a.sob - a.entre) / 20), 1.0).astype(np.float32)
env = np.empty_like(alvo); g = 1.0; at, rl = 1 - np.exp(-1 / (0.06 * SR)), 1 - np.exp(-1 / (0.15 * SR))
for i in range(N):
    g += (alvo[i] - g) * (at if alvo[i] < g else rl); env[i] = g
trilha *= env[:, None]

efeitos = np.zeros((N, 2), np.float32); cache = {}
for t, f, gdb in cfg.get('cues', []):
    if f not in cache:
        x = load(P / 'assets/sfx' / f) if (P / 'assets/sfx' / f).exists() else load(SK / 'kit/sfx' / f)
        e = np.abs(x).max(1); fim = np.nonzero(e > 1e-4)[0]; x = x[:fim[-1] + 1] if len(fim) else x[:1]
        k = int(0.01 * SR); pk = int(np.argmax(np.convolve(np.abs(x).max(1), np.ones(k) / k, mode='same')))
        cache[f] = (x / (np.abs(x).max() + 1e-9), pk)
    x, pk = cache[f]; s = int((t + 1 / 30) * SR) - pk
    a0, b0 = max(0, s), min(N, s + len(x))
    if b0 > a0: efeitos[a0:b0] += x[a0 - s:b0 - s] * nivel_voz * 2.5 * 10 ** (gdb / 20)

mix = voz + trilha + efeitos
mix /= max(1.0, np.abs(mix).max() / 0.95)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-i', '-', '-c:a', 'pcm_s16le', str(P / 'assets/audio/mix.wav')],
               input=mix.astype(np.float32).tobytes(), check=True)
print(f'mix.wav pronto ({D:.1f} s) · trilha: {musica.name} · {len(cfg.get("cues", []))} efeitos')

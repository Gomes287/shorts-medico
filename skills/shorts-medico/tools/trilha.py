"""Trilha de fundo calma feita por código (R$ 0, nada baixado): pad de acordes lentos + notinhas de sino com eco.
uso: python -I -X utf8 trilha_espaco.py <pasta> <duração_s> --titulo <t_s> [--seed 7]
A música termina naturalmente no título: o último acorde (resolução) começa em --titulo, cresce ~5 dB e se apaga até o
fim. Grava assets/audio/trilha.wav (48 kHz, estéreo, pico -1 dB). Determinístico: mesma semente, mesma música.
"""
import argparse, wave
from pathlib import Path
import numpy as np

ap = argparse.ArgumentParser(); ap.add_argument('pasta'); ap.add_argument('dur', type=float)
ap.add_argument('--titulo', type=float, required=True); ap.add_argument('--seed', type=int, default=7)
a = ap.parse_args(); P = Path(a.pasta); SR = 48000; N = int(a.dur * SR)
rng = np.random.default_rng(a.seed); L = np.zeros(N); R = np.zeros(N)
f = lambda m: 440 * 2 ** ((m - 69) / 12)
# progressão lenta (Lá menor -> Fá -> Dó -> Sol), última = Lá suspenso resolvendo em Dó com 9ª
PROG = [[57, 60, 64, 71], [53, 57, 60, 67], [48, 55, 64, 71], [55, 59, 62, 69]]
FINAL = [48, 55, 60, 64, 74]


def pad(notes, t0, t1, gain, att=1.6, rel=2.2):
    i0, i1 = int(t0 * SR), min(N, int((t1 + rel) * SR)); n = i1 - i0
    if n <= 0: return
    t = np.arange(n) / SR; env = np.minimum(1, t / att) * np.clip(1 - (t - (t1 - t0)) / rel, 0, 1)
    for m in notes:
        for det, pan in ((-.07, .3), (.07, .7)):
            w = np.sin(2 * np.pi * f(m + det / 1) * t + rng.random() * 6) + .25 * np.sin(2 * np.pi * 2 * f(m) * t) + .08 * np.sin(2 * np.pi * 3 * f(m) * t)
            w *= 1 + .15 * np.sin(2 * np.pi * .17 * t + m)
            L[i0:i1] += w * env * gain * (1 - pan); R[i0:i1] += w * env * gain * pan


def bell(m, t0, gain):
    i0 = int(t0 * SR); n = min(N - i0, int(3.5 * SR))
    if n <= 0: return
    t = np.arange(n) / SR; env = np.exp(-t * 1.6) * np.minimum(1, t / .01)
    w = (np.sin(2 * np.pi * f(m) * t) + .35 * np.sin(2 * np.pi * f(m) * 2.76 * t) * np.exp(-t * 3)) * env * gain
    pan = .25 + .5 * rng.random()
    for k, (dl, g) in enumerate(((0, 1), (.38, .45), (.76, .22), (1.14, .1))):   # eco
        j = i0 + int(dl * SR); m2 = min(n, N - j)
        if m2 > 0: L[j:j + m2] += w[:m2] * g * (1 - pan if k % 2 == 0 else pan); R[j:j + m2] += w[:m2] * g * (pan if k % 2 == 0 else 1 - pan)


bar = 3.2; t = 0.0; k = 0
while t < a.titulo - .2:
    t1 = min(t + bar, a.titulo); pad(PROG[k % 4], t, t1, .05)
    for j in range(4):
        tb = t + j * bar / 4 + .4
        if tb < a.titulo - .3 and rng.random() < .7: bell(PROG[k % 4][rng.integers(4)] + 12, tb, .035)
    t += bar; k += 1
pad(FINAL, a.titulo - .15, a.dur - 2.4, .05 * 10 ** (5 / 20), att=.9, rel=2.3)          # resolução: +5 dB no título
bell(FINAL[-1] + 12, a.titulo, .05); bell(FINAL[2] + 12, a.titulo + .4, .04)
x = np.stack([L, R], 1)
for d, g in ((.031, .35), (.053, .28), (.079, .2), (.113, .14)):                         # sala grande simples
    s = int(d * SR); y = np.zeros_like(x); y[s:] = x[:-s] * g; x = x + y[:, ::-1]
fade = int(.8 * SR); x[-fade:] *= np.linspace(1, 0, fade)[:, None]
x /= np.abs(x).max() + 1e-9; x *= 10 ** (-1 / 20)
(P / 'assets/audio').mkdir(parents=True, exist_ok=True)
with wave.open(str(P / 'assets/audio/trilha.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype('<i2').tobytes())
print(f'trilha.wav {a.dur:.1f}s, título em {a.titulo:.2f}s')

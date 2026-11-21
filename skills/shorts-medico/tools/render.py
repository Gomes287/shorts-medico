"""Render final: HyperFrames → masteriza o som (-14 LUFS, pico -1,5 dB) → entrega/<nome>.mp4 + folha de conferência.
uso: render.py <projeto> <nome-do-arquivo> [--rascunho]
--rascunho renderiza rápido (qualidade draft) para conferir · --so-som só troca o som (depois de mixar.py).
"""
import sys, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import *

ap = argparse.ArgumentParser(); ap.add_argument('projeto'); ap.add_argument('nome'); ap.add_argument('--rascunho', action='store_true'); ap.add_argument('--so-som', action='store_true')
a = ap.parse_args(); P = Path(a.projeto).resolve()
raw = P / 'renders/bruto.mp4'
if not a.so_som: run(['npx', '--yes', HF, 'render', str(P), '-o', str(raw), '--fps', str(FPS), '-q', 'draft' if a.rascunho else 'delivery', '--quiet'], cwd=P)
out = P / 'entrega' / f'{a.nome}.mp4'; out.parent.mkdir(exist_ok=True)
run(['ffmpeg', '-v', 'error', '-y', '-i', str(raw), '-i', str(P / 'assets/audio/mix.wav'), '-map', '0:v', '-map', '1:a',
     '-c:v', 'copy', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', str(out)])
run(['ffmpeg', '-v', 'error', '-y', '-i', str(out), '-vf', 'fps=2,scale=216:-1,tile=10x6', '-frames:v', '1', str(P / 'work/folha.jpg')])
print('vídeo:', out, f'({duracao(out):.1f} s)'); print('folha de conferência (2 quadros/s):', P / 'work/folha.jpg')

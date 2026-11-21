"""Prepara o vídeo do médico (o MP4/WebM baixado do site do HeyGen, de preferência com fundo verde #00FF00).
uso: preparar.py <projeto> [--video arquivo.mp4|webm] [--fundo auto|transparente|verde|ia]
Faz:
  1. assets/audio/vo.wav  — a voz tirada do próprio vídeo (é ela que vale: os lábios batem com ela)
  2. assets/video/medico.webm — o médico SEM fundo (VP9 com alfa, 30 fps):
       transparente = WebM com alfa · verde = chroma key no verde · ia = remove-background (sem tela verde)
  3. work/rosto.json — caixa do rosto (mediana em ~24 quadros) para os enquadramentos (close = cabeça ~42% da tela)
  4. work/capa_candidatos.jpg — 12 quadros numerados com o tempo para escolher a expressão da capa (miniatura)
"""
import sys, json, argparse, shutil, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import *

ap = argparse.ArgumentParser(); ap.add_argument('projeto'); ap.add_argument('--video'); ap.add_argument('--fundo', default='auto')
a = ap.parse_args(); P = Path(a.projeto)
src = Path(a.video) if a.video else next((f for f in (P / 'assets/video/heygen.webm', P / 'assets/video/heygen.mp4', P / 'assets/video/heygen.mov') if f.exists()), None)
if not src or not src.exists(): sys.exit('não achei o vídeo do HeyGen. Passe --video <arquivo>')
if a.video:
    dst = P / f'assets/video/heygen{src.suffix.lower()}'
    if src.resolve() != dst.resolve(): shutil.copy(src, dst)
    src = dst
D = duracao(src); print(f'vídeo: {src.name} ({D:.1f} s)')

# 1. voz
run(['ffmpeg', '-v', 'error', '-y', '-i', str(src), '-vn', '-af', 'loudnorm=I=-16:TP=-1.5:LRA=9', '-ar', '48000', '-ac', '2', str(P / 'assets/audio/vo.wav')])


def probe_alpha(f):
    o = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=codec_name,pix_fmt:stream_tags=alpha_mode', '-of', 'json', str(f)], capture_output=True, text=True).stdout
    s = json.loads(o)['streams'][0]; return s.get('tags', {}).get('alpha_mode') == '1' or 'a' in (s.get('pix_fmt') or '').replace('yuv', '')


def cor_cantos(f):
    import numpy as np
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(min(1.0, D / 2)), '-i', str(f), '-frames:v', '1', '-vf', 'scale=108:192', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True).stdout
    im = np.frombuffer(raw, np.uint8).reshape(192, 108, 3).astype(int)
    cantos = np.concatenate([im[:12, :12].reshape(-1, 3), im[:12, -12:].reshape(-1, 3), im[60:120, :6].reshape(-1, 3), im[60:120, -6:].reshape(-1, 3)])
    return np.median(cantos, 0).astype(int)


modo = a.fundo
if modo == 'auto':
    if src.suffix.lower() == '.webm' and probe_alpha(src): modo = 'transparente'
    else:
        r, g, b = cor_cantos(src); modo = 'verde' if (g > 120 and g > r * 1.5 and g > b * 1.5) else 'ia'
print('fundo:', modo)
if modo == 'ia':
    print('AVISO: o vídeo não tem fundo verde. O recorte por IA costuma ficar ruim — peça o vídeo de novo no HeyGen com fundo #00FF00.')
out = P / 'assets/video/medico.webm'
vp9 = ['-c:v', 'libvpx-vp9', '-pix_fmt', 'yuva420p', '-b:v', '0', '-crf', '22', '-row-mt', '1', '-auto-alt-ref', '0', '-an']
if modo == 'transparente':
    run(['ffmpeg', '-v', 'error', '-y', '-c:v', 'libvpx-vp9', '-i', str(src), '-vf', 'fps=30,scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih):color=black@0,format=yuva420p', *vp9, str(out)])
elif modo == 'verde':
    r, g, b = cor_cantos(src); key = '0x%02X%02X%02X' % (r, g, b)
    vf = (f'fps=30,scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih):color={key},'
          f'chromakey={key}:0.13:0.07,despill=type=green:mix=0.6:expand=0.1,format=yuva420p')
    run(['ffmpeg', '-v', 'error', '-y', '-i', str(src), '-vf', vf, *vp9, str(out)])
else:
    tmp = P / 'work/_src30.mp4'
    run(['ffmpeg', '-v', 'error', '-y', '-i', str(src), '-an', '-vf', 'fps=30,scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)', '-c:v', 'libx264', '-crf', '14', '-pix_fmt', 'yuv420p', str(tmp)])
    run(['npx', '--yes', HF, 'remove-background', str(tmp), '-o', str(out), '--quality', 'balanced'], capture_output=True)
    tmp.unlink(missing_ok=True)
print('médico recortado:', out)

# 3. rosto
import numpy as np, cv2
cas = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
caixas = []
for k in range(24):
    t = 0.3 + (D - 0.6) * k / 23
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.2f}', '-i', str(src), '-frames:v', '1', '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], capture_output=True).stdout
    if len(raw) != 1080 * 1920: continue
    g = np.frombuffer(raw, np.uint8).reshape(1920, 1080)
    fs = cas.detectMultiScale(g, 1.1, 6, minSize=(120, 120))
    if len(fs): caixas.append(max(fs, key=lambda f: f[2] * f[3]))
metodo = 'rosto'
if caixas:
    x, y, w, h = np.median(np.array(caixas), 0).astype(int).tolist()
else:  # plano B: estima a cabeça pela silhueta recortada (topo da pessoa até o começo dos ombros)
    metodo = 'silhueta'
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-c:v', 'libvpx-vp9', '-ss', f'{D / 2:.2f}', '-i', str(out), '-frames:v', '1', '-vf', 'alphaextract', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], capture_output=True).stdout
    if len(raw) != 1080 * 1920: sys.exit('não achei o rosto nem a silhueta do médico no vídeo.')
    m_ = np.frombuffer(raw, np.uint8).reshape(1920, 1080) > 128
    linhas = np.nonzero(m_.any(1))[0]
    if not len(linhas): sys.exit('o recorte ficou vazio: confira o fundo do vídeo.')
    topo = linhas[0]; larg = m_.sum(1)
    ref = max(1, int(np.median(larg[topo + 20:topo + 120])))
    ombro = next((r for r in range(topo + 120, 1920) if larg[r] > ref * 1.6), min(1919, topo + 400))
    hh = int((ombro - topo) * 0.85); cols = np.nonzero(m_[topo:topo + hh].any(0))[0]
    h = int(hh * 0.75); w = int(h * 0.8); cx = int(cols.mean()) if len(cols) else 540
    x, y = cx - w // 2, int(topo + hh * 0.55 - h / 2)
    print('aviso: rosto não detectado; estimei pela silhueta (confira o enquadramento nas prévias).')
json.dump({'x': x, 'y': y, 'w': w, 'h': h, 'cx': x + w // 2, 'cy': y + h // 2, 'W': 1080, 'H': 1920, 'amostras': len(caixas), 'metodo': metodo, 'duracao': D},
          open(P / 'work/rosto.json', 'w'), indent=1)
print(f'rosto: {w}x{h}px em ({x},{y}) · {len(caixas)}/24 quadros')

# 4. candidatos de capa
n = 12; ts = [0.2 + (D - 0.4) * k / (n - 1) for k in range(n)]
from PIL import Image, ImageDraw
folha = Image.new('RGB', (1200, 900), (20, 20, 20)); dr = ImageDraw.Draw(folha)
topo = int(min(max(0, y + h // 2 - 540), 1920 - 1080))
for k, t in enumerate(ts):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.2f}', '-i', str(src), '-frames:v', '1', '-vf',
                          f'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih),crop=1080:1080:0:{topo},scale=300:300',
                          '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
    if len(raw) == 300 * 300 * 3:
        folha.paste(Image.frombytes('RGB', (300, 300), raw), ((k % 4) * 300, (k // 4) * 300))
    dr.rectangle([(k % 4) * 300, (k // 4) * 300, (k % 4) * 300 + 120, (k // 4) * 300 + 34], fill=(0, 0, 0))
    dr.text(((k % 4) * 300 + 8, (k // 4) * 300 + 8), f'{k}: {t:.1f}s', fill=(255, 255, 255))
folha.save(P / 'work/capa_candidatos.jpg', quality=88)
json.dump([round(t, 2) for t in ts], open(P / 'work/capa_tempos.json', 'w'))
print('candidatos de capa:', P / 'work/capa_candidatos.jpg', '(quadro k = tempo', ', '.join(f'{k}:{t:.1f}s' for k, t in enumerate(ts)), ')')

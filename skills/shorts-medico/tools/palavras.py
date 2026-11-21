"""Tempo de cada palavra (em português) na voz FINAL (assets/audio/vo.wav, tirada do vídeo do HeyGen).
uso: palavras.py <projeto> [--modelo medium]
- Com work/roteiro.json: transcreve com faster-whisper (pt, word_timestamps) e casa com o roteiro conhecido, então a
  tela mostra a grafia certa do roteiro com o tempo real da fala. Palavras que o ouvinte não ouviu como escritas
  aparecem como SUSPEITAS (pronúncia errada no ElevenLabs/HeyGen: reescreva a coluna falada e gere de novo).
- Sem roteiro (plano B sem texto): cria work/roteiro.json a partir do que foi ouvido. CONFIRA a grafia (nomes de
  doenças, remédios, siglas) e rode de novo.
Grava work/words.json: [{i, text, start, end, line}] em palavras MOSTRADAS.
"""
import sys, json, re, unicodedata, difflib, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import *

ap = argparse.ArgumentParser(); ap.add_argument('projeto'); ap.add_argument('--modelo', default='medium')
a = ap.parse_args(); P = Path(a.projeto)
from faster_whisper import WhisperModel


def norm(s):
    s = unicodedata.normalize('NFD', s.lower()); s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]', '', s)


rot = roteiro(P)
m = WhisperModel(a.modelo, device='cpu', compute_type='int8')
segs, _ = m.transcribe(str(P / 'assets/audio/vo.wav'), language='pt', word_timestamps=True, vad_filter=False,
                       condition_on_previous_text=False)
segs = list(segs)
heard = [dict(w=w.word.strip(), s=w.start, e=w.end, p=w.probability) for s in segs for w in (s.words or []) if norm(w.word)]
if not heard: sys.exit('não ouvi fala nenhuma em assets/audio/vo.wav')

if not rot:
    linhas = [s.text.strip() for s in segs if s.text.strip()]
    rot = {'titulo_capa': [linhas[0][:40]], 'linhas': [[l, l] for l in linhas], 'origem': 'transcrito (confira a grafia)'}
    json.dump(rot, open(P / 'work/roteiro.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print('roteiro criado a partir da fala:', P / 'work/roteiro.json', '— confira nomes e números.')

# palavras faladas (tokens) -> grupo mostrado
tokens, mostradas = [], []
for li, linha in enumerate(rot['linhas']):
    sh, sp = falado(linha)
    sw, gw = sh.split(), sp.split()
    if len(sw) != len(gw):
        sys.exit(f'linha {li + 1}: a coluna mostrada tem {len(sw)} palavras e a falada {len(gw)}. Use "_" para juntar '
                 f'palavras faladas que viram uma só na tela (ex.: ["140/90", "catorze_por_nove"]).\n  {sh}\n  {sp}')
    for gi, (s_, g_) in enumerate(zip(sw, gw)):
        mi = len(mostradas); mostradas.append(dict(text=s_, line=li, toks=[]))
        for part in g_.split('_'):
            if norm(part):
                mostradas[mi]['toks'].append(len(tokens)); tokens.append(dict(n=norm(part), w=part, mi=mi))

A = [t['n'] for t in tokens]; B = [norm(h['w']) for h in heard]
sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
tempo = [None] * len(tokens); suspeitas = []
for op, i1, i2, j1, j2 in sm.get_opcodes():
    if op == 'equal':
        for k in range(i2 - i1): tempo[i1 + k] = (heard[j1 + k]['s'], heard[j1 + k]['e'])
    elif op == 'replace' and j2 > j1:
        s0, e0 = heard[j1]['s'], heard[j2 - 1]['e']; n = i2 - i1
        for k in range(n): tempo[i1 + k] = (s0 + (e0 - s0) * k / n, s0 + (e0 - s0) * (k + 1) / n)
        mostrado = ''.join(norm(mostradas[mi]['text']) for mi in dict.fromkeys(t['mi'] for t in tokens[i1:i2]))
        if mostrado != ''.join(B[j1:j2]):   # "vinte e oito por cento" ouvido como "28%" não é erro
            suspeitas.append((' '.join(t['w'] for t in tokens[i1:i2]), ' '.join(h['w'] for h in heard[j1:j2]), s0))
    elif op == 'delete':
        suspeitas.append((' '.join(t['w'] for t in tokens[i1:i2]), '(não ouvido)', None))
# preenche buracos por interpolação
for i in range(len(tempo)):
    if tempo[i] is None:
        prev = next((tempo[k][1] for k in range(i - 1, -1, -1) if tempo[k]), 0.0)
        nxt = next((tempo[k][0] for k in range(i + 1, len(tempo)) if tempo[k]), prev + 0.3)
        tempo[i] = (prev, max(prev + 0.05, min(nxt, prev + 0.3)))
words = []
for mi, m_ in enumerate(mostradas):
    if m_['toks']:
        s, e = tempo[m_['toks'][0]][0], tempo[m_['toks'][-1]][1]
    else:
        s = words[-1]['end'] if words else 0.0; e = s + 0.05
    words.append(dict(i=mi, text=m_['text'], start=round(s, 3), end=round(e, 3), line=m_['line']))
json.dump(words, open(P / 'work/words.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
baixa = [h for h in heard if h['p'] < 0.5]
print(f'{len(words)} palavras com tempo · fala de {words[0]["start"]:.2f} a {words[-1]["end"]:.2f} s → work/words.json')
if suspeitas:
    print('SUSPEITAS (roteiro → o que se ouve):')
    for s_, h_, t in suspeitas[:30]: print(f'  {t if t is not None else "":>6} {s_!r} → {h_!r}')
if baixa:
    print('palavras ouvidas com pouca certeza:', ', '.join(f"{h['w']}@{h['s']:.1f}s" for h in baixa[:20]))

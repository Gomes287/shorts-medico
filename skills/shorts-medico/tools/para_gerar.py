"""Instruções para a pessoa gerar a voz (site do ElevenLabs) e o vídeo (site do HeyGen) a partir do roteiro aprovado.
uso: para_gerar.py <projeto>   → grava <projeto>/para_gerar.txt e mostra na tela
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import *

P = Path(sys.argv[1]); rot = roteiro(P) or sys.exit('falta work/roteiro.json')
for i, l in enumerate(rot['linhas']):
    sh, sp = falado(l)
    if len(sh.split()) != len(sp.split()):
        sys.exit(f'linha {i + 1}: a coluna mostrada e a falada têm números de palavras diferentes (use "_" na falada).')
texto = texto_para_voz(rot).replace('^', '').replace('*', '')
txt = f"""1. ELEVENLABS (site) — Text to Speech
   Voz: a voz clonada do médico · Modelo: Eleven v4 (ou Multilingual v2) · Idioma: português
   Cole o texto inteiro abaixo, gere e baixe o MP3. Ouça uma vez: nome de doença, remédio ou sigla dito errado → me avise.
{'-' * 70}
{texto}
{'-' * 70}
   ({len(texto.split())} palavras, {len(texto)} caracteres)

2. HEYGEN (site)
   1. Avatar: o Digital Twin do médico.
   2. Voz: envie o MP3 do ElevenLabs (use o áudio, não digite o texto).
   3. Formato 9:16 (vertical), resolução 1080p.
   4. Fundo: cor sólida VERDE #00FF00 (obrigatório: o recorte por IA sem verde fica ruim).
   5. Expressividade alta. Sem legenda, sem música, sem logo.
   6. Baixe o MP4 e me mande o caminho do arquivo.
"""
(P / 'para_gerar.txt').write_text(txt, encoding='utf-8'); print(txt); print('salvo em', P / 'para_gerar.txt')

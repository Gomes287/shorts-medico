#!/bin/bash
# Configuração única da shorts-medico (grátis, sem sudo, ~600 MB). Tudo vai para ~/.cache/shorts-medico;
# rodar de novo termina em segundos.
set -e
V="$HOME/.cache/shorts-medico"; mkdir -p "$V"
PY=""
for p in python3.12 python3.11 python3.10 python3; do command -v $p >/dev/null && { PY=$p; break; }; done
[ -n "$PY" ] || { echo "precisa de Python 3.10+ (python.org)"; exit 1; }
VPY="$V/venv/bin/python"; [ -x "$V/venv/Scripts/python.exe" ] && VPY="$V/venv/Scripts/python.exe"
if [ ! -x "$VPY" ]; then
  "$PY" -m venv "$V/venv"
  [ -x "$V/venv/Scripts/python.exe" ] && VPY="$V/venv/Scripts/python.exe"
fi
"$VPY" -m pip install -q --upgrade pip
"$VPY" -m pip install -q faster-whisper "opencv-python-headless<5" numpy pillow
# baixa o modelo de transcrição em português uma vez (~1,5 GB do 'medium' fica em ~/.cache/huggingface)
"$VPY" -c "from faster_whisper import WhisperModel; WhisperModel('medium', device='cpu', compute_type='int8')" >/dev/null
# GSAP (animação) não vem no pacote por causa da licença da GreenSock: baixa do CDN oficial uma vez
G="$V/vendor/gsap-3.14.2.min.js"; mkdir -p "$V/vendor"
[ -s "$G" ] || curl -fsSL -o "$G" https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js
[ -s "$G" ] && echo "gsap ok" || echo "não consegui baixar o GSAP (internet?)"
ok=1
node -e 'process.exit(+process.versions.node.split(".")[0] >= 22 ? 0 : 1)' 2>/dev/null && echo "node $(node -v) ok" || { echo "precisa de Node 22+ (nodejs.org ou brew install node)"; ok=0; }
command -v ffmpeg >/dev/null && echo "ffmpeg ok" || { echo "precisa de ffmpeg (brew install ffmpeg / winget install ffmpeg)"; ok=0; }
npx --yes hyperframes@0.9.77 --version >/dev/null 2>&1 && echo "hyperframes ok" || { echo "não consegui rodar o hyperframes (npx)"; ok=0; }
echo "python da skill: $VPY"
[ $ok = 1 ] && echo "Tudo pronto." || { echo "arrume os itens acima e rode o setup.sh de novo"; exit 1; }

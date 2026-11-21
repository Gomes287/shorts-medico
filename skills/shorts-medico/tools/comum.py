"""Peças comuns da shorts-medico: caminhos, perfil do médico e a linha de identificação (CFM)."""
import json, os, sys, subprocess
from pathlib import Path

SK = Path(__file__).resolve().parent.parent
CONF = Path(os.environ.get('SHORTS_MEDICO_CONF', Path.home() / '.config/shorts-medico'))
PERFIL = CONF / 'perfil.json'
NOTAS = CONF / 'notas.md'          # regras da pessoa (ficam fora da pasta da skill, sobrevivem a atualizações)
CACHE = Path.home() / '.cache/shorts-medico'
GSAP_VER = '3.14.2'
HF = 'hyperframes@0.9.77'
W, H, FPS = 1080, 1920, 30

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

CORES_PADRAO = {"primaria": "#0E5E6F", "acento": "#F2A541", "claro": "#F4F1EA", "escuro": "#10181C",
                "texto_claro": "#FFFFFF", "texto_escuro": "#10181C"}
PERFIL_PADRAO = {
    "tratamento": "Dr.", "nome": "", "crm": "", "uf": "",
    "especialidades": [],            # [{"nome": "Cardiologia", "rqe": "12345"}] (até 2, Art. 13 §1º f)
    "pos_graduacao": "",             # se NÃO for especialista: "Medicina Esportiva" (vira "... NÃO ESPECIALISTA")
    "arroba": "", "cores": CORES_PADRAO, "fonte_titulo": "Anton",
    "horario_publicacao": "08:00", "aviso_ia_descricao": True,
}


def carregar_perfil(obrigatorio=True):
    if not PERFIL.exists():
        if obrigatorio:
            sys.exit('Sem perfil ainda. Faça a configuração guiada (SKILL.md, passo 0) e grave com: perfil.py definir ...')
        return json.loads(json.dumps(PERFIL_PADRAO))
    p = json.loads(json.dumps(PERFIL_PADRAO))
    salvo = json.load(open(PERFIL, encoding='utf-8'))
    for k, v in salvo.items():
        if isinstance(v, dict) and isinstance(p.get(k), dict):
            p[k].update(v)
        else:
            p[k] = v
    return p


def salvar_perfil(p):
    CONF.mkdir(parents=True, exist_ok=True)
    json.dump(p, open(PERFIL, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)


def linha_id(p):
    """Art. 4º da Res. CFM 2.336/2023: nome + CRM/UF + a palavra MÉDICO + especialidade com RQE (se houver)."""
    nome = f'{p["tratamento"]} {p["nome"]}'.strip()
    partes = [nome, f'MÉDICO · CRM-{p["uf"]} {p["crm"]}']
    if p.get('especialidades'):
        partes += [f'{e["nome"]} · RQE {e["rqe"]}' for e in p['especialidades'][:2]]
    elif p.get('pos_graduacao'):
        partes.append(f'Pós-graduação em {p["pos_graduacao"]} · NÃO ESPECIALISTA')
    return ' · '.join(partes)


def faltando_perfil(p):
    f = [k for k in ('nome', 'crm', 'uf') if not p.get(k)]
    for e in p.get('especialidades', []):
        if not e.get('rqe'):
            f.append(f'RQE de {e.get("nome")}')
    return f


# ---- projeto ---------------------------------------------------------------------------------------------------
def roteiro(P):
    f = Path(P) / 'work/roteiro.json'
    return json.load(open(f, encoding='utf-8')) if f.exists() else None


def falado(linha):
    """Uma linha do roteiro é [mostrado, falado] ou só "texto". '_' junta palavras faladas que viram uma mostrada."""
    if isinstance(linha, str):
        return linha, linha
    return linha[0], (linha[1] if len(linha) > 1 and linha[1] else linha[0])


def texto_para_voz(rot):
    return ' '.join(falado(l)[1].replace('_', ' ') for l in rot['linhas'])


def gsap():
    """GSAP não vem no pacote (licença da GreenSock): o setup.sh baixa do CDN oficial; aqui baixa se faltar."""
    f = CACHE / f'vendor/gsap-{GSAP_VER}.min.js'
    if not f.exists():
        import urllib.request
        f.parent.mkdir(parents=True, exist_ok=True)
        url = f'https://cdn.jsdelivr.net/npm/gsap@{GSAP_VER}/dist/gsap.min.js'
        try:
            urllib.request.urlretrieve(url, f)
        except Exception as e:
            sys.exit(f'não consegui baixar o GSAP ({e}). Rode tools/setup.sh com internet.')
    return f


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def duracao(arquivo):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(arquivo)],
                         capture_output=True, text=True, check=True).stdout.strip()
    return float(out)

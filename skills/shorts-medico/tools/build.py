"""Monta o Short (index.html do HyperFrames) a partir de:
  ~/.config/shorts-medico/perfil.json (cores, fonte, identificação CFM)
  work/roteiro.json (título da capa, linhas, palavra do CTA) · work/words.json (tempo de cada palavra)
  work/rosto.json (caixa do rosto) · work/edicao.json (as cenas)
uso: build.py <projeto>
Grava index.html, work/som.json (efeitos nas trocas) e work/eventos.json (para o medir.py).
Marcas no roteiro (coluna mostrada): *palavra* = cor de destaque na legenda · ^palavra = punch-in (zoom seco).
"""
import sys, json, re, html, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import *

esc = html.escape
FONTES = {'Anton': ('Anton', 'Anton.woff2', 400), 'ArchivoBlack': ('Archivo Black', 'ArchivoBlack.woff2', 400),
          'Playfair': ('Playfair Display', 'PlayfairDisplay-Roman.woff2', 700), 'Inter': ('Inter', 'Inter.woff2', 900)}
PLANOS = {  # altura da caixa do rosto (fração da tela), centro x, centro y (fração). cabeça ≈ caixa × 1,35
    'capa': (0.31, 540, 0.53), 'close': (0.31, 540, 0.50), 'xclose': (0.38, 540, 0.48),
    'medio': (0.17, 540, 0.40), 'split': (0.13, 540, 0.72), 'cta': (0.13, 540, 0.74), 'fora': (0.17, 540, 0.40), 'baixo': (0.15, 540, 0.70)}
DADOS = {'numero', 'barras', 'icones', 'estudo'}
PLANO_PADRAO = {'rosto': 'close', 'numero': 'split', 'barras': 'split', 'icones': 'split', 'estudo': 'split',
                'lista': 'split', 'mito': 'split', 'texto': 'baixo', 'broll': 'fora', 'cta': 'cta'}


def limpa(w):
    return w.replace('*', '').replace('^', '')


def css(p):
    c = p['cores']; ft = FONTES.get(p.get('fonte_titulo', 'Anton'), FONTES['Anton'])
    faces = ''.join(f"@font-face{{font-family:'{n}';src:url('assets/fonts/{f}') format('woff2');font-weight:{'100 900' if f == 'Inter.woff2' else w};font-display:block}}"
                    for n, f, w in FONTES.values())
    faces += "@font-face{font-family:'Playfair Display';font-style:italic;src:url('assets/fonts/PlayfairDisplay-Italic.woff2') format('woff2')}"
    return faces + f"""
:root{{--pri:{c['primaria']};--ace:{c['acento']};--claro:{c['claro']};--escuro:{c['escuro']};--tc:{c['texto_claro']};--te:{c['texto_escuro']};
--ft:'{ft[0]}',sans-serif;--ftw:{ft[2]}}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{margin:0;background:#000}}
#root{{position:relative;width:{W}px;height:{H}px;overflow:hidden;background:var(--escuro);font-family:Inter,sans-serif}}
.abs{{position:absolute}}
.mundo{{position:absolute;inset:0;visibility:hidden}}
.m-claro{{background:var(--claro)}} .m-escuro{{background:var(--escuro)}} .m-primaria{{background:var(--pri)}} .m-acento{{background:var(--ace)}}
.mundo .grade{{position:absolute;inset:-40px;opacity:.10;background-image:linear-gradient(currentColor 2px,transparent 2px),linear-gradient(90deg,currentColor 2px,transparent 2px);background-size:90px 90px}}
.m-claro .grade{{color:var(--te)}} .m-escuro .grade,.m-primaria .grade,.m-acento .grade{{color:#fff}}
.mundo .luz{{position:absolute;left:50%;top:46%;width:1500px;height:1500px;margin:-750px 0 0 -750px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.34),rgba(255,255,255,0) 62%)}}
.mundo .vinheta{{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 45%,rgba(0,0,0,0) 55%,rgba(0,0,0,.35))}}
#med{{position:absolute;left:0;top:0;width:{W}px;height:{H}px;transform-origin:0 0;z-index:10;filter:drop-shadow(0 30px 40px rgba(0,0,0,.35));-webkit-mask-image:linear-gradient(to bottom,#000 70%,transparent 97%),linear-gradient(to right,transparent 0,#000 7%,#000 93%,transparent 100%);mask-image:linear-gradient(to bottom,#000 70%,transparent 97%),linear-gradient(to right,transparent 0,#000 7%,#000 93%,transparent 100%);-webkit-mask-composite:source-in;mask-composite:intersect}}
.cena{{position:absolute;inset:0;visibility:hidden;z-index:6}}
.frente{{z-index:20}}
.painel{{position:absolute;left:60px;right:60px;top:190px;height:740px;display:flex;flex-direction:column;align-items:center;justify-content:center}}
.titulo{{position:absolute;left:50px;right:50px;top:150px;text-align:center;z-index:25;font-family:var(--ft);font-weight:var(--ftw);text-transform:uppercase;line-height:.98}}
.titulo .l{{display:block;font-size:128px;color:var(--tc);text-shadow:0 6px 0 rgba(0,0,0,.35),0 14px 34px rgba(0,0,0,.45)}}
.titulo .l.a{{color:var(--ace)}}
.titulo .l.p{{font-size:98px}}
.leg{{position:absolute;left:40px;right:40px;top:1290px;text-align:center;z-index:30;visibility:hidden;font-family:Inter;font-weight:900;font-size:84px;line-height:1.02;text-transform:uppercase;color:#fff;
  -webkit-text-stroke:3px rgba(0,0,0,.85);paint-order:stroke fill;text-shadow:0 8px 22px rgba(0,0,0,.55)}}
.leg .d{{color:var(--ace)}} .leg.alto{{top:975px}}
.idpill{{position:absolute;left:50%;top:1470px;width:max-content;max-width:960px;text-align:center;line-height:1.3;z-index:31;font:700 27px Inter;color:#fff;background:rgba(0,0,0,.62);border-left:8px solid var(--ace);padding:14px 26px;border-radius:14px;visibility:hidden}}
.fonte{{position:absolute;left:50%;bottom:-6px;transform:translateX(-50%);white-space:nowrap;font:600 25px Inter;color:#fff;background:rgba(0,0,0,.55);padding:10px 22px;border-radius:40px}}
.big{{font-family:var(--ft);font-weight:var(--ftw);line-height:.9;text-align:center}}
.rot{{font:800 46px Inter;text-align:center;line-height:1.15}}
.on-claro{{color:var(--te)}} .on-esc{{color:var(--tc)}}
.barra-l{{width:100%;margin:12px 0}}
.barra-n{{font:800 36px Inter;display:flex;justify-content:space-between;margin-bottom:8px}}
.barra-t{{height:58px;border-radius:12px;background:rgba(0,0,0,.12)}}
.barra-f{{height:100%;border-radius:12px;background:var(--pri);transform-origin:0 50%}}
.barra-f.d{{background:var(--ace)}}
.icones{{display:grid;gap:22px;justify-content:center}}
.icone{{width:110px;height:150px}}
.papel{{width:900px;background:#FBFAF7;color:#1b1b1b;border-radius:10px;padding:56px 60px;box-shadow:0 40px 80px rgba(0,0,0,.4);transform:rotate(-2deg);position:relative}}
.papel .rev{{font:800 30px Inter;letter-spacing:4px;text-transform:uppercase;color:#7a7a7a;border-bottom:3px solid #ddd;padding-bottom:18px;margin-bottom:26px}}
.papel .tt{{font:700 58px 'Playfair Display';line-height:1.12}}
.papel .hl{{position:relative;display:inline}}
.papel .hl i{{position:absolute;left:-6px;right:-6px;top:58%;bottom:-2px;background:var(--ace);opacity:.65;z-index:-1;transform-origin:0 50%;font-style:normal}}
.papel .fita{{position:absolute;top:-26px;left:50%;width:220px;height:60px;margin-left:-110px;background:rgba(255,240,180,.75);transform:rotate(3deg)}}
.papel img{{width:100%;border-radius:6px;display:block}}
.item{{display:flex;align-items:center;gap:36px;width:100%}}
.item .num{{flex:0 0 220px;height:220px;border-radius:40px;background:var(--ace);color:var(--te);display:flex;align-items:center;justify-content:center;font-family:var(--ft);font-weight:var(--ftw);font-size:170px}}
.item .tx{{font:900 72px Inter;line-height:1.05;text-transform:uppercase}}
.item .de{{font:700 34px Inter;opacity:.7;margin-top:10px}}
.cartao{{width:900px;padding:56px;border-radius:30px;background:#fff;color:#1b1b1b;box-shadow:0 40px 80px rgba(0,0,0,.35);font:800 60px Inter;line-height:1.12;text-align:center;position:relative}}
.carimbo{{position:absolute;right:-30px;bottom:-70px;font-family:var(--ft);font-weight:var(--ftw);font-size:120px;padding:6px 36px;border:12px solid currentColor;border-radius:24px;transform:rotate(-10deg);background:rgba(255,255,255,.9)}}
.carimbo.mito{{color:#D7263D}} .carimbo.verdade{{color:#1E9E5A}}
.frase{{font-family:var(--ft);font-weight:var(--ftw);font-size:150px;line-height:.95;text-align:center;text-transform:uppercase;color:var(--tc);}} .on-claro.frase{{color:var(--pri);text-shadow:0 10px 0 rgba(0,0,0,.25)}}
.broll{{position:absolute;inset:0;overflow:hidden}} .broll img,.broll video{{width:100%;height:100%;object-fit:cover}}
.coment{{width:920px;background:#fff;border-radius:34px;padding:34px 38px;box-shadow:0 30px 70px rgba(0,0,0,.4);display:flex;align-items:center;gap:26px;color:#111}}
.coment .av{{flex:0 0 96px;height:96px;border-radius:50%;background:var(--pri);color:#fff;font:900 44px Inter;display:flex;align-items:center;justify-content:center}}
.coment .cx{{flex:1;font:800 62px Inter;min-height:80px;line-height:1.2}}
.coment .ph{{color:#9a9a9a;font-weight:600;font-size:44px}}
.coment .env{{flex:0 0 90px;height:90px;border-radius:50%;background:var(--ace);display:flex;align-items:center;justify-content:center}}
.cta-t{{font-family:var(--ft);font-weight:var(--ftw);font-size:120px;color:var(--tc);text-transform:uppercase;text-align:center;line-height:.95;margin-bottom:40px;text-shadow:0 8px 0 rgba(0,0,0,.25)}}
.cta-t b{{color:var(--ace);font-weight:inherit}} .on-claro.cta-t{{color:var(--pri)}} .on-claro.cta-t b{{color:var(--escuro)}}
"""


ICONE = ('<svg class="icone" viewBox="0 0 110 150"><circle cx="55" cy="32" r="28" fill="{c}"/>'
         '<path d="M10 150 V102 Q10 70 42 68 H68 Q100 70 100 102 V150 Z" fill="{c}"/></svg>')


LARG = {'Anton': 0.47, 'ArchivoBlack': 0.78, 'Playfair': 0.66, 'Inter': 0.70}  # largura média de uma letra maiúscula (em)


def titulo_html(rot, idt='titulo', fonte='Anton'):
    linhas = rot.get('titulo_capa') or []
    out = []
    for k, l in enumerate(linhas):
        cls = 'l' + (' a' if k == len(linhas) - 1 and len(linhas) > 1 else '')
        tam = min(128, int(960 / (max(1, len(l)) * LARG.get(fonte, 0.6))))
        out.append(f'<span class="{cls}" style="font-size:{tam}px;white-space:nowrap">{esc(l)}</span>')
    return f'<div id="{idt}" class="titulo">{"".join(out)}</div>'


class Montagem:
    def __init__(self, P):
        self.P = Path(P); self.p = carregar_perfil(); self.rot = roteiro(P) or sys.exit('falta work/roteiro.json')
        self.words = json.load(open(self.P / 'work/words.json', encoding='utf-8'))
        self.rosto = json.load(open(self.P / 'work/rosto.json'))
        ed = self.P / 'work/edicao.json'
        self.ed = json.load(open(ed, encoding='utf-8')) if ed.exists() else {'cenas': [{'tipo': 'rosto'}]}
        self.D = round(max(self.rosto.get('duracao', 0), self.words[-1]['end'] + 0.6), 3)
        self.html, self.js, self.som, self.ev = [], [], [], []

    # ---- tempo ------------------------------------------------------------------------------------------------
    def acha(self, alvo, de=0):
        if alvo is None: return None
        if isinstance(alvo, (int, float)) and not isinstance(alvo, bool): return int(alvo)
        a = re.sub(r'[^\wà-ú]', '', limpa(str(alvo)).lower())
        for w in self.words[de:]:
            if re.sub(r'[^\wà-ú]', '', limpa(w['text']).lower()) == a: return w['i']
        lista = ', '.join(f"{w['i']}:{limpa(w['text'])}" for w in self.words[de:de + 60])
        sys.exit(f'não achei a palavra "{alvo}" depois da palavra {de}. Palavras: {lista}')

    def t(self, i, d=0.0): return round(self.words[i]['start'] + d, 3)

    # ---- médico ------------------------------------------------------------------------------------------------
    def tf(self, plano, zoom=1.0):
        fh, tx, ty = PLANOS[plano]; r = self.rosto
        s = fh * H / r['h'] * zoom; x = tx - r['cx'] * s; y = ty * H - r['cy'] * s
        return dict(x=round(x, 1), y=round(y, 1), scale=round(s, 4))

    def medico(self, cenas):
        js = []; first = True
        punches = [w['i'] for w in self.words if '^' in w['text']]
        for c in cenas:
            plano = c['plano']; t0, t1 = c['t0'], c['t1']
            vis = 0 if plano == 'fora' else 1
            js.append(f'tl.set("#med",{{opacity:{vis}}},{t0});')
            if first:
                js.append(f'tl.set("#med",{json.dumps(self.tf(plano))},0);'); first = False
            elif c.get('corte'):
                js.append(f'tl.set("#med",{json.dumps(self.tf(plano))},{t0});')
            else:
                js.append(f'tl.to("#med",{{...{json.dumps(self.tf(plano))},duration:0.32,ease:"expo.inOut"}},{t0});')
            # deriva lenta + punch-ins dentro da cena
            pts = [self.t(i) for i in punches if t0 + 0.4 < self.t(i) < t1 - 0.3] if plano in ('close', 'xclose', 'medio', 'capa') else []
            marcos = [t0 + (0 if c is cenas[0] else 0.32)] + pts + [t1]
            z = 1.0
            for k in range(len(marcos) - 1):
                a, b = marcos[k], marcos[k + 1]
                if k > 0:  # punch: zoom seco na palavra forte (alterna para dentro/fora)
                    z = 1.13 if z < 1.06 else 1.0
                    js.append(f'tl.to("#med",{{...{json.dumps(self.tf(plano, z))},duration:0.1,ease:"expo.out"}},{a});')
                    self.ev.append(a); a += 0.1
                if b - a > 0.3:
                    js.append(f'tl.to("#med",{{...{json.dumps(self.tf(plano, z * 1.06))},duration:{round(b - a, 3)},ease:"none"}},{round(a, 3)});')
        return js

    # ---- cenas ---------------------------------------------------------------------------------------------------
    def cenas(self):
        cs = [dict(c) for c in self.ed['cenas']]
        if not cs or cs[0].get('tipo') != 'rosto':
            cs.insert(0, {'tipo': 'rosto'})
        cs[0]['plano'] = 'capa'; cs[0]['i0'] = 0
        if not any(c['tipo'] == 'cta' for c in cs):
            cs.append({'tipo': 'cta', 'em': self.rot.get('cta_em', 'comenta')})
        de = 0
        for c in cs[1:]:
            c['i0'] = self.acha(c.get('em'), de); de = c['i0'] + 1
        for k, c in enumerate(cs):
            c['t0'] = 0.0 if k == 0 else self.t(c['i0'], -0.05)
        for k, c in enumerate(cs):
            c['t1'] = cs[k + 1]['t0'] if k + 1 < len(cs) else self.D
            c.setdefault('plano', PLANO_PADRAO[c['tipo']])
            if c['tipo'] in DADOS and not c.get('fonte'):
                sys.exit(f'cena {k} ({c["tipo"]}): todo dado precisa de "fonte" (regra de verdade / CFM Art. 11).')
        return cs

    def mundos(self, cs):
        seq = ['escuro', 'primaria', 'claro']; ult = None
        for k, c in enumerate(cs):
            m = c.get('fundo')
            if not m:
                m = 'primaria' if k == 0 else next(x for x in seq[k % 3:] + seq if x != ult)
            c['fundo'] = m; ult = m
            self.html.append(f'<div id="m{k}" class="mundo m-{m}" style="visibility:{"visible" if k == 0 else "hidden"}"><div class="grade"></div><div class="luz"></div><div class="vinheta"></div></div>')
            if k: self.js.append(f'tl.set("#m{k}",{{visibility:"visible"}},{c["t0"]});')
            self.js.append(f'tl.set("#m{k}",{{visibility:"hidden"}},{c["t1"]});')
            if k:
                self.ev.append(c['t0'])
                if c['tipo'] != 'rosto' or k == 1:
                    self.som.append([round(c['t0'], 3), 'whoosh.mp3', -18])

    def palavra_t(self, c, campo, padrao=0.25):
        if c.get(campo) is not None:
            return self.t(self.acha(c[campo], c['i0']))
        return round(c['t0'] + padrao, 3)

    def cena_html(self, k, c):
        tipo = c['tipo']; cid = f'c{k}'; t0 = c['t0']; on = 'on-claro' if c['fundo'] == 'claro' else 'on-esc'
        js = []; inner = ''
        fonte = f'<div class="fonte">Fonte: {esc(c["fonte"])}</div>' if c.get('fonte') else ''
        if tipo == 'numero':
            casas = c.get('casas', 0 if float(c['valor']).is_integer() else 1)
            inner = (f'<div class="painel">' + (f'<div class="rot {on}">{esc(c.get("antes", ""))}</div>' if c.get('antes') else '') +
                     f'<div id="{cid}n" class="big" style="font-size:{c.get("tamanho", 290)}px;color:var(--ace)">0</div>' +
                     (f'<div class="rot {on}" style="margin-top:14px">{esc(c.get("depois", ""))}</div>' if c.get('depois') else '') + fonte + '</div>')
            tn = self.palavra_t(c, 'valor_em', 0.2)
            js.append(f'SM.contador("#{cid}n",{{de:{c.get("de", 0)},ate:{c["valor"]},t0:{tn},dur:0.8,casas:{casas},prefixo:{json.dumps(c.get("prefixo", ""))},sufixo:{json.dumps(c.get("unidade", ""))}}});')
            js.append(f'tl.fromTo("#{cid} .painel",{{scale:.7,opacity:0}},{{scale:1,opacity:1,duration:.35,ease:"back.out(1.6)"}},{t0});')
            self.som.append([tn, 'impact-bass-1.mp3', -16]); self.ev += [t0, tn, tn + 0.8]
        elif tipo == 'barras':
            itens = c['itens'][:5]; vmax = c.get('vmax') or max(i['valor'] for i in itens) * 1.08; un = c.get('unidade', '')
            rows = []
            for j, it in enumerate(itens):
                d = ' d' if it.get('destaque') else ''
                rows.append(f'<div class="barra-l"><div class="barra-n {on}"><span>{esc(it["nome"])}</span><span id="{cid}v{j}">0</span></div>'
                            f'<div class="barra-t"><div id="{cid}b{j}" class="barra-f{d}" style="width:{it["valor"] / vmax * 100:.1f}%"></div></div></div>')
            inner = f'<div class="painel" style="justify-content:center">' + (f'<div class="rot {on}" style="margin-bottom:24px">{esc(c["titulo"])}</div>' if c.get('titulo') else '') + ''.join(rows) + fonte + '</div>'
            for j, it in enumerate(itens):
                tj = self.t(self.acha(it['em'], c['i0'])) if it.get('em') else round(t0 + 0.2 + j * c.get('passo', 0.22), 3)
                casas = it.get('casas', c.get('casas', 0 if float(it['valor']).is_integer() else 1))
                js.append(f'tl.fromTo("#{cid}b{j}",{{scaleX:0}},{{scaleX:1,duration:.6,ease:"expo.out"}},{tj});')
                js.append(f'SM.contador("#{cid}v{j}",{{de:0,ate:{it["valor"]},t0:{tj},dur:0.6,casas:{casas},sufixo:{json.dumps(un)}}});')
                self.ev.append(tj); self.som.append([tj, 'pop.mp3', -20])
        elif tipo == 'icones':
            n = int(c.get('de', 10)); dest = int(c['destaque']); cols = 5 if n <= 10 else 10
            if n > 20: sys.exit('icones: use até 20 (ex.: 3 em cada 10)')
            cor_base = 'rgba(0,0,0,.18)' if c['fundo'] == 'claro' else 'rgba(255,255,255,.25)'
            ics = ''.join(f'<div id="{cid}i{j}" style="position:relative">{ICONE.format(c=cor_base)}<div class="abs" id="{cid}a{j}" style="inset:0;opacity:0">{ICONE.format(c="var(--ace)")}</div></div>' for j in range(n))
            inner = (f'<div class="painel"><div class="big" style="font-size:150px;color:var(--ace);margin-bottom:30px">{esc(c.get("texto", f"{dest} em cada {n}"))}</div>'
                     f'<div class="icones" style="grid-template-columns:repeat({cols},110px)">{ics}</div>'
                     + (f'<div class="rot {on}" style="margin-top:30px">{esc(c["depois"])}</div>' if c.get('depois') else '') + fonte + '</div>')
            js.append(f'tl.fromTo("#{cid} .icone",{{y:30,opacity:0}},{{y:0,opacity:1,duration:.25,stagger:.03,ease:"power2.out"}},{t0});')
            ta = self.palavra_t(c, 'destaque_em', 0.6)
            for j in range(dest):
                js.append(f'tl.fromTo("#{cid}a{j}",{{opacity:0,scale:1.4}},{{opacity:1,scale:1,duration:.18,ease:"back.out(2)"}},{round(ta + j * 0.12, 3)});')
                self.ev.append(round(ta + j * 0.12, 3))
            self.som.append([ta, 'pop.mp3', -18]); self.ev.append(t0)
        elif tipo == 'estudo':
            if c.get('imagem'):
                corpo = f'<img src="{esc(c["imagem"])}">'
            else:
                tt = esc(c['titulo']); dst = c.get('destaque')
                if dst and dst in c['titulo']:
                    tt = esc(c['titulo']).replace(esc(dst), f'<span class="hl">{esc(dst)}<i id="{cid}h"></i></span>', 1)
                corpo = f'<div class="rev">{esc(c.get("revista", ""))} · {esc(str(c.get("ano", "")))}</div><div class="tt">{tt}</div>'
            inner = f'<div class="painel"><div class="papel"><div class="fita"></div>{corpo}</div>{fonte}</div>'
            js.append(f'tl.fromTo("#{cid} .papel",{{y:900,rotation:8}},{{y:0,rotation:-2,duration:.5,ease:"expo.out"}},{t0});')
            th = self.palavra_t(c, 'destaque_em', 0.7)
            js.append(f'tl.fromTo("#{cid}h",{{scaleX:0}},{{scaleX:1,duration:.4,ease:"power2.inOut"}},{th});')
            self.ev += [t0, th]; self.som.append([t0, 'swish_1.wav', -20])
        elif tipo == 'lista':
            inner = (f'<div class="painel"><div class="item"><div class="num">{c["n"]}</div><div><div class="tx {on}">{esc(c["texto"])}</div>'
                     + (f'<div class="de {on}">{c["n"]} de {c["total"]}</div>' if c.get('total') else '') + '</div></div></div>')
            js.append(f'tl.fromTo("#{cid} .num",{{scale:0,rotation:-25}},{{scale:1,rotation:0,duration:.35,ease:"back.out(2)"}},{t0});')
            js.append(f'tl.fromTo("#{cid} .tx",{{x:500,opacity:0}},{{x:0,opacity:1,duration:.4,ease:"expo.out"}},{round(t0 + 0.12, 3)});')
            self.ev += [t0, t0 + 0.12]; self.som.append([t0, 'pop.mp3', -16])
        elif tipo == 'mito':
            v = c.get('veredito', 'mito')
            inner = f'<div class="painel"><div class="cartao">{esc(c["texto"])}<div id="{cid}s" class="carimbo {v}">{"MITO" if v == "mito" else "VERDADE"}</div></div></div>'
            js.append(f'tl.fromTo("#{cid} .cartao",{{y:-900}},{{y:0,duration:.45,ease:"back.out(1.2)"}},{t0});')
            ts = self.palavra_t(c, 'veredito_em', 0.9)
            js.append(f'tl.fromTo("#{cid}s",{{scale:2.6,opacity:0}},{{scale:1,opacity:1,duration:.22,ease:"back.out(2.4)"}},{ts});')
            self.ev += [t0, ts]; self.som.append([ts, 'impact-bass-1.mp3', -16])
        elif tipo == 'texto':
            inner = f'<div class="painel" style="top:170px"><div class="frase {on}">{esc(c["texto"])}</div></div>'
            js.append(f'tl.fromTo("#{cid} .frase",{{scale:1.6,opacity:0,filter:"blur(12px)"}},{{scale:1,opacity:1,filter:"blur(0px)",duration:.3,ease:"expo.out"}},{t0});')
            self.ev.append(t0)
        elif tipo == 'broll':
            src = esc(c['arquivo'])
            midia = f'<img src="{src}">' if not src.lower().endswith(('.mp4', '.webm', '.mov')) else ''
            inner = f'<div class="broll">{midia}</div>' + (f'<div class="fonte" style="bottom:auto;top:1600px">{esc(c["credito"])}</div>' if c.get('credito') else '')
            if midia:
                js.append(f'tl.fromTo("#{cid} .broll img",{{scale:1.0}},{{scale:1.12,duration:{round(c["t1"] - t0, 3)},ease:"none"}},{t0});')
            else:
                self.extra_media.append(f'<video id="{cid}v" class="clip" src="{src}" muted playsinline data-start="{t0}" data-duration="{round(c["t1"] - t0, 3)}" data-track-index="3" style="position:absolute;left:0;top:0;width:{W}px;height:{H}px;object-fit:cover;z-index:7"></video>')
            self.ev.append(t0)
        elif tipo == 'cta':
            # CTA padrão = convite para contar a própria experiência (NOTES 2026-11-21); "palavra" é opcional
            cfg = self.rot.get('cta') or {}
            if self.rot.get('palavra_cta') and cfg.get('modo') != 'experiencia':
                pal = self.rot['palavra_cta'].upper(); dt = 0.08
                topo = f'<div class="cta-t {on}">COMENTA<br><b>{esc(pal)}</b></div>'; cx = ''
            else:
                pal = cfg.get('exemplo') or 'Eu já vi isso quando…'; dt = 0.045
                topo = (f'<div class="cta-t {on}" style="font-size:64px;margin-bottom:12px">COMENTA AQUI</div>'
                        f'<div class="cta-t {on}" style="font-size:{cfg.get("tamanho", 96)}px"><b>{esc(cfg.get("pergunta") or "E VOCÊ, JÁ VIU ISSO?")}</b></div>')
                cx = ' style="font-size:44px;font-weight:600"'
            letras = '<span>' + ''.join(f'<span id="{cid}l{j}" style="opacity:0">{esc(ch)}</span>' for j, ch in enumerate(pal)) + '</span>'
            ini = esc((self.p.get('nome') or 'M')[:1].upper())
            seta = '<svg width="46" height="46" viewBox="0 0 24 24"><path d="M3 20 L21 12 L3 4 L5 12 Z" fill="#111"/></svg>'
            inner = (f'<div class="painel" style="top:200px;height:700px">{topo}'
                     f'<div class="coment"><div class="av">{ini}</div><div class="cx"{cx}><span id="{cid}ph" class="ph">Adicione um comentário…</span>{letras}</div><div id="{cid}e" class="env">{seta}</div></div></div>')
            js.append(f'tl.fromTo("#{cid} .coment",{{y:600,opacity:0}},{{y:0,opacity:1,duration:.4,ease:"expo.out"}},{t0});')
            js.append(f'tl.fromTo("#{cid} .cta-t",{{scale:.6,opacity:0}},{{scale:1,opacity:1,duration:.3,ease:"back.out(2)"}},{round(t0 + 0.1, 3)});')
            tp = self.palavra_t(c, 'palavra_em', 0.6)
            js.append(f'tl.set("#{cid}ph",{{display:"none"}},{tp});')
            for j in range(len(pal)):
                js.append(f'tl.set("#{cid}l{j}",{{opacity:1}},{round(tp + j * dt, 3)});')
            te = round(tp + len(pal) * dt + 0.15, 3)
            js.append(f'tl.fromTo("#{cid}e",{{scale:1}},{{scale:1.3,duration:.12,yoyo:true,repeat:1}},{te});')
            self.ev += [t0, t0 + 0.1, tp, te]; self.som += [[tp, 'pop.mp3', -18], [te, 'sparkle.mp3', -16]]
        elif tipo == 'rosto':
            return
        z = ' frente' if tipo in ('estudo', 'mito', 'cta') and c['plano'] != 'split' else ''
        self.html.append(f'<div id="{cid}" class="cena{z}" style="z-index:{8 if tipo == "broll" else 6}">{inner}</div>')
        self.js.append(f'tl.set("#{cid}",{{visibility:"visible"}},{t0});tl.set("#{cid}",{{visibility:"hidden"}},{c["t1"]});')
        self.js += js

    # ---- legenda ---------------------------------------------------------------------------------------------------
    def legendas(self, t_titulo, cs):
        grupos, g = [], []
        for w in self.words:
            if w['start'] < t_titulo: continue
            txt = limpa(w['text'])
            if g and (len(g) >= 3 or w['line'] != g[-1]['line'] or sum(len(limpa(x['text'])) for x in g) + len(txt) > 15
                      or re.search(r'[.!?,:;]$', g[-1]['text'])):
                grupos.append(g); g = []
            g.append(w)
        if g: grupos.append(g)
        for k, g in enumerate(grupos):
            s = g[0]['start']; e = grupos[k + 1][0]['start'] if k + 1 < len(grupos) else min(self.D, g[-1]['end'] + 0.5)
            spans = []
            for w in g:
                tx = esc(re.sub(r'[.,;:]$', '', limpa(w['text'])))
                d = '*' in w['text'] or re.search(r'\d', w['text'])
                spans.append(f'<span class="d">{tx}</span>' if d else tx)
            pl = next((c['plano'] for c in cs if c['t0'] <= s < c['t1']), 'close')
            alto = ' alto' if pl in ('split', 'cta', 'baixo') else ''
            self.html.append(f'<div id="g{k}" class="leg{alto}">{" ".join(spans)}</div>')
            self.js.append(f'tl.set("#g{k}",{{visibility:"visible"}},{round(s, 3)});tl.set("#g{k}",{{visibility:"hidden"}},{round(e, 3)});'
                           f'tl.fromTo("#g{k}",{{scale:.88}},{{scale:1,duration:.09,ease:"back.out(3)"}},{round(s, 3)});')
            self.ev.append(round(s, 3))

    # ---- montagem ---------------------------------------------------------------------------------------------------
    def build(self):
        self.extra_media = []
        cs = self.cenas(); self.mundos(cs)
        self.html.append(f'<video id="med" class="clip" src="assets/video/medico.webm" muted playsinline data-start="0" data-duration="{self.D}" data-track-index="2"></video>')
        self.js += self.medico(cs)
        for k, c in enumerate(cs): self.cena_html(k, c)
        # título da capa = 1ª frase falada; sai no fim dela
        l0 = [w for w in self.words if w['line'] == 0]
        t_tit = round(l0[-1]['end'] + 0.12, 3) if l0 else 2.0
        self.html.append(titulo_html(self.rot, fonte=self.p.get('fonte_titulo', 'Anton')))
        self.js.append(f'tl.to("#titulo",{{y:-260,opacity:0,filter:"blur(10px)",duration:.28,ease:"power3.in"}},{t_tit});')
        self.ev.append(t_tit)
        # loop: nos últimos 0,35 s volta ao enquadramento e ao título da capa
        tl0 = round(self.D - 0.35, 3)
        self.js.append(f'tl.to("#med",{{...{json.dumps(self.tf("capa"))},opacity:1,duration:.33,ease:"expo.inOut"}},{tl0});')
        self.js.append(f'tl.fromTo("#titulo",{{y:-120,opacity:0,filter:"blur(10px)"}},{{y:0,opacity:1,filter:"blur(0px)",duration:.3,ease:"expo.out",immediateRender:false}},{tl0});')
        self.js.append(f'tl.set(".cena,.leg",{{visibility:"hidden"}},{tl0});tl.set("#m0",{{visibility:"visible"}},{tl0});')
        self.legendas(t_tit, cs)
        # identificação CFM (Art. 4º): depois do título e durante o CTA
        idt = esc(linha_id(self.p))
        cta = next(c for c in cs if c['tipo'] == 'cta')
        fim_id = min([t_tit + 4.3] + [c['t0'] for c in cs if c['t0'] > t_tit + 2.3 and c['plano'] not in ('close', 'xclose', 'capa')])
        for n, (a, b) in enumerate([(t_tit + 0.3, fim_id), (cta['t0'] + 0.2, tl0)]):
            self.html.append(f'<div id="id{n}" class="idpill" style="{"top:1110px" if n else ""}">{idt}</div>')
            self.js.append(f'tl.set("#id{n}",{{visibility:"visible"}},{round(a, 3)});tl.set("#id{n}",{{visibility:"hidden"}},{round(b, 3)});'
                           f'tl.fromTo("#id{n}",{{xPercent:-50,x:-80,opacity:0}},{{xPercent:-50,x:0,opacity:1,duration:.3,ease:"expo.out"}},{round(a, 3)});')
        self.html.append(f'<audio id="mix" class="clip" src="assets/audio/mix.wav" data-start="0" data-duration="{self.D}" data-track-index="10" data-volume="1"></audio>')
        doc = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width={W}, height={H}">
<title>{esc(self.P.name)}</title>
<script src="assets/vendor/gsap.min.js"></script><script src="assets/kit/shorts.js"></script>
<style>{css(self.p)}</style></head>
<body><div id="root" data-composition-id="main" data-start="0" data-duration="{self.D}" data-width="{W}" data-height="{H}" data-fps="{FPS}">
{chr(10).join(self.html)}
{chr(10).join(self.extra_media)}
</div>
<script>
const tl = gsap.timeline({{paused:true}});
{chr(10).join(self.js)}
SM.ligar(tl);
window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = tl;
</script></body></html>"""
        (self.P / 'index.html').write_text(doc, encoding='utf-8')
        planos = [(c['plano'], c['t1'] - c['t0']) for c in cs]
        close = sum(d for p_, d in planos if p_ in ('capa', 'close', 'xclose'))
        face_frac = PLANOS['capa'][0] * 1.35
        json.dump({'duracao': self.D, 'eventos': sorted(set(round(e, 2) for e in self.ev)), 'close_s': round(close, 2),
                   'cabeca_quadro0': round(face_frac, 3), 'cenas': [{'tipo': c['tipo'], 'plano': c['plano'], 't0': c['t0'], 't1': c['t1']} for c in cs],
                   'titulo_sai': t_tit}, open(self.P / 'work/eventos.json', 'w'), indent=1)
        json.dump({'duracao': self.D, 'cues': sorted(self.som)}, open(self.P / 'work/som.json', 'w'), indent=1)
        print(f'index.html pronto · {len(cs)} cenas · {self.D:.1f} s · rosto em close {close / self.D * 100:.0f}% do tempo')
        for k, c in enumerate(cs):
            print(f'  {k:>2} {c["tipo"]:<7} {c["plano"]:<6} {c["t0"]:6.2f}–{c["t1"]:6.2f}  fundo {c["fundo"]}')


if __name__ == '__main__':
    Montagem(sys.argv[1]).build()

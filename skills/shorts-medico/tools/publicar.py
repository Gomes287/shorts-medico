"""Texto pronto para o médico publicar: título, descrição (busca), comentário fixado, passo a passo por rede,
checklist CFM conferido e o diagnóstico de 48 h.  uso: publicar.py <projeto> <nome>
Lê work/roteiro.json → "post": {titulo, descricao, hashtags, comentario_fixado}, "dados", "cfm", "compartilhar", "so_dele".
"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import *

P = Path(sys.argv[1]); nome = sys.argv[2]; p = carregar_perfil(); rot = roteiro(P); post = rot.get('post', {})
med = json.load(open(P / 'work/medidas.json', encoding='utf-8')) if (P / 'work/medidas.json').exists() else {}
tit = post.get('titulo', '')
if len(tit) > 50: sys.exit(f'título do post com {len(tit)} caracteres: o máximo é 50.')
if '#' in tit: sys.exit('título do post não leva hashtag.')
nm = f'{p["tratamento"]} {p["nome"]}'.strip()
desc = post.get('descricao', '').strip()
tags = ' '.join(h if h.startswith('#') else '#' + h for h in post.get('hashtags', [])[:5])
prop = 'da própria' if p['tratamento'].lower().startswith('dra') else 'do próprio'
aviso = f'Vídeo produzido com apoio de inteligência artificial (avatar e voz {prop} {nm}).' if p.get('aviso_ia_descricao', True) else ''
cta_txt = post.get('cta_legenda') or (f'Comenta {rot["palavra_cta"].upper()} 👇' if rot.get('palavra_cta')
                                      else ((rot.get('cta') or {}).get('pergunta', '').capitalize() + ' Conta aqui nos comentários 👇').strip())
educ = 'Conteúdo educativo: não substitui a consulta médica.' if post.get('aviso_educativo', True) else ''
legenda = '\n\n'.join(x for x in [desc, cta_txt, educ, linha_id(p), aviso, tags] if x)
fontes = '\n'.join(f'  • {d.get("o_que", "")}: {d.get("numero", "")} — {d.get("fonte", "")} {d.get("link", "")}'.rstrip() for d in rot.get('dados', [])) or '  (sem números no vídeo)'
cfm = '\n'.join(f'  ✓ {n}' for n in (rot.get('cfm') or {}).get('notas', [])) or '  (rodar a checagem CFM do SKILL.md)'
medidas = '\n'.join(f'  {k}: {v}' for k, v in med.items()) or '  (rodar medir.py)'
txt = f"""PUBLICAR — {nome}
{'=' * 60}
ARQUIVOS
  vídeo: {nome}.mp4  ·  capa (miniatura): {nome}_capa.png

TÍTULO (até 50 caracteres, sem hashtag) — {len(tit)} caracteres
  {tit}

LEGENDA / DESCRIÇÃO (copie tudo)
{'-' * 60}
{legenda}
{'-' * 60}

COMENTÁRIO PARA FIXAR (logo depois de publicar)
  {post.get('comentario_fixado') or cta_txt}

YOUTUBE SHORTS (pelo computador, no YouTube Studio)
  [ ] Enviar o MP4 → Título acima → Descrição: a legenda acima
  [ ] Miniatura: enviar {nome}_capa.png (mesmo layout de toda a série)
  [ ] Tags: deixar em branco (ajudam pouco)
  [ ] "Conteúdo alterado ou sintético": marcar SIM (avatar e voz realistas feitos com IA — regra da plataforma)
  [ ] Vídeo relacionado: o ÚLTIMO Short que você publicou (corrente: quem assiste um vê os anteriores)
  [ ] Visibilidade → Programar → sempre no mesmo horário ({p.get('horario_publicacao', '08:00')})

INSTAGRAM REELS (o mesmo MP4)
  [ ] Mesma legenda · capa: {nome}_capa.png · ativar o rótulo "Feito com IA" · compartilhar também no feed

TIKTOK (o mesmo MP4)
  [ ] Mesma legenda · em "Mais opções", ativar "Conteúdo gerado por IA"

NÃO FAÇA
  • não peça inscrição no meio do vídeo (já está fora) · não apague um Short que começou fraco
  • não reposte o mesmo arquivo · não troque título/capa antes de 48 h · não use música com direitos autorais

PRIMEIRA HORA
  [ ] Responder os primeiros comentários  [ ] Fixar o comentário acima  [ ] Não mexer no vídeo

48 HORAS DEPOIS (Studio → Conteúdo → Shorts → o vídeo → Análise)
  1. "Continuaram assistindo" — meta acima de 75–80%. Abaixo: o problema são os 3 primeiros segundos
     (título/primeira frase mais forte, rosto já reagindo, algo acontecendo no 1º segundo).
  2. Duração média — meta perto do vídeo inteiro (90–95%+). Bem abaixo: cortar frase que não acrescenta.
  3. Curva de retenção — ache o segundo da maior queda e veja o que acontece nele:
     • despenca no começo → gancho fraco
     • degrau no meio → a resposta veio cedo demais (guardar para o fim) ou um momento chato
     • desce aos poucos → faltou abrir uma curiosidade nova ("mas tem um detalhe…")
     • quedas por todo lado → ritmo: mais coisas novas na tela, mais close, punch-in
     • plana e começa acima de 100% → está ótimo: repita a receita no próximo
  Se travou: mude UMA coisa no próximo vídeo (a que o número apontou) e compare.

DADOS E FONTES DO VÍDEO
{fontes}

CHECAGEM CFM (Res. 2.336/2023 e 2.454/2026) — feita antes de gerar
{cfm}
  ✓ Identificação no vídeo e na legenda: {linha_id(p)}
  ✓ Confira também: nome, CRM e RQE na página principal do perfil (Art. 6º)
  O médico é integralmente responsável pelo conteúdo feito com IA (Res. 2.454/2026, Art. 7º).

POR QUE ALGUÉM COMPARTILHARIA: {rot.get('compartilhar', '-')}
SÓ ESTE MÉDICO DIRIA (teste da troca): {rot.get('so_dele', '-')}

MEDIDAS DO VÍDEO
{medidas}
"""
out = P / 'entrega' / f'{nome}_publicar.txt'; out.parent.mkdir(exist_ok=True); out.write_text(txt, encoding='utf-8'); print('texto de publicação:', out)

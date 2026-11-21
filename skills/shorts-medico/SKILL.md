---
name: shorts-medico
description: >-
  Shorts/Reels/TikTok (9:16, 45–57 s) de MÉDICO em PORTUGUÊS, prontos para publicar: o avatar do próprio médico (HeyGen)
  falando com a voz clonada dele (ElevenLabs), recortado na frente de gráficos — número que conta, ícones "3 em cada 10",
  barras, estudo com marca-texto, mito × verdade, lista — com a FONTE de todo dado na tela, legenda palavra a palavra,
  capa no 1º quadro (rosto ~42% da tela + título), CTA convidando a contar a experiência e loop. Checagem CFM (Res. 2.336/2023
  e 2.454/2026) antes de gerar, identificação nome/CRM/RQE no vídeo e na legenda, e entrega MP4 + capa PNG + texto de
  publicação (título, descrição para busca, comentário fixado, passo a passo por rede, diagnóstico de 48 h).
  A pessoa gera a voz e o vídeo nos sites do ElevenLabs e do HeyGen (fundo verde) e entrega o MP4. Use quando pedirem
  "short de médico", "vídeo para o Instagram do doutor", "reels de saúde", "conteúdo médico com avatar", "shorts-medico",
  ou derem um tema de saúde para virar vídeo curto com o médico aparecendo.
---

# Shorts de médico — autoridade com o rosto dele, retenção medida, CFM conferido

`SK` = a pasta desta skill (a que contém este SKILL.md; o Claude Code mostra o caminho ao carregar a skill como
"Base directory". Instalada como plugin fica em `~/.claude/plugins/...`; copiada à mão, em `~/.claude/skills/shorts-medico`).
Se tiver dúvida: `SK=$(dirname "$(find ~/.claude -path '*shorts-medico/SKILL.md' -print -quit)")`.
`PY=~/.cache/shorts-medico/venv/bin/python` (rode tudo com `$PY -I`).
Referências: `referencia/cfm.md` (regras com artigos) · `referencia/retencao.md` (metas medidas) ·
`referencia/formatos.md` (formatos e roteiro) · `NOTES.md` (decisões de base da skill) ·
`~/.config/shorts-medico/notas.md` (regras da PESSOA: LEIA antes de todo vídeo e acrescente cada correção que ela der,
com data e o porquê. Fica fora da pasta da skill para não se perder quando o plugin atualizar; valem acima do resto).

## 0. Primeira vez (configuração guiada — uma vez por pessoa)
1. Rode `bash $SK/tools/setup.sh` (≈2 min + download do modelo de transcrição). Precisa de Node 22+ e ffmpeg.
2. `$PY -I $SK/tools/perfil.py mostrar`. Se não houver perfil, pergunte EM UMA MENSAGEM, curta:
   - nome como aparece (Dr./Dra.), CRM e UF, especialidade(s) registradas com RQE (até 2). Sem RQE = não é especialista:
     pergunte a pós-graduação (vira "Pós-graduação em X · NÃO ESPECIALISTA", Art. 13) e **nunca** escreva especialidade;
   - @ do perfil;
   - cores: código hex, OU um print do Instagram/logo (`perfil.py paleta <imagem>` sugere primária e acento);
     sem resposta = paleta padrão (petróleo + âmbar);
   - fonte do título: Anton (padrão, condensada), ArchivoBlack, Playfair (elegante) ou Inter;
3. Grave: `perfil.py definir '{"tratamento":"Dra.","nome":"…","crm":"…","uf":"SP","especialidades":[{"nome":"…","rqe":"…"}],"arroba":"@…","cores":{"primaria":"#…","acento":"#…"},"fonte_titulo":"Anton"}'`.
4. **Mostre a prévia** antes de seguir: `$PY -I $SK/tools/capa.py --previa ./previa_capa.png` e abra a imagem para a
   pessoa ("é assim que toda capa vai ficar; quer mudar cor ou fonte?"). Mudar depois é só pedir: `perfil.py definir`.
5. `perfil.py checar` até dizer "Pronto para gerar".

## 1. Roteiro (nada é gerado antes do "pode")
Pergunte o tema (e, se ela tiver, um caso real do consultório SEM identificar paciente). Escreva `work/roteiro.json`
(modelo: `$SK/exemplo/roteiro.json`) seguindo `referencia/formatos.md`:
- **título da capa = a 1ª frase falada** (2 linhas curtas, a 2ª vira cor de destaque);
- 110–140 palavras (≈ 45–57 s); a resposta do gancho só no fim; a cada curiosidade que fecha, abra outra;
- **uma frase que só esse médico diria** (`so_dele`, o teste da troca) e **para quem alguém mandaria** (`compartilhar`);
- **sem pedido de inscrição**; fim = **convite para a pessoa contar a experiência dela** ("comenta aqui em que situação
  você já viu isso"), e a última frase emenda na primeira (loop). Grave em `roteiro.cta`: `{"modo":"experiencia",
  "pergunta":"EM QUE SITUAÇÃO VOCÊ JÁ VIU ISSO?","exemplo":"Vi um hospital…"}` (o painel digita o exemplo) e
  `post.cta_legenda`. "Comenta PALAVRA" só se a pessoa pedir (`palavra_cta`). Tema não clínico: `post.aviso_educativo: false`;
- coluna falada: números por extenso, siglas como se falam, `_` junta palavras faladas que viram uma na tela
  (`["140/90", "catorze_por_nove"]`); `*palavra*` = destaque na legenda, `^palavra` = zoom seco (2–3 nos primeiros 3 s);
- todo número com fonte em `dados` (OMS, Ministério da Saúde, diretriz de sociedade médica, estudo com DOI) — **número
  sem fonte não entra**; arredonde igual na fala e na tela;
- `post`: título ≤ 50 caracteres sem hashtag; descrição que começa com o que a pessoa digitaria na busca; 3–5 hashtags.

**Checagem CFM** (`referencia/cfm.md`) linha por linha, e grave o resultado em `roteiro.cfm.notas`:
sem promessa/insinuação de resultado; sem sensacionalismo nem medo coletivo (título incluído: "isso pode te matar" ✗);
sem autopromoção ("o melhor", "único"); sem medicamento/produto/marca; sem técnica não reconhecida; não diz tratar
órgão/doença fora da especialidade registrada; sem diagnóstico ou consulta pelos comentários; sem paciente identificável;
dado estatístico fiel à fonte. Achou algo? Reescreva e diga o porquê.

Mostre à pessoa, ANTES de ela gastar créditos nos sites: o roteiro, a tabela de dados com fontes e a checagem CFM.
Só siga depois do "pode".

## 2. Vídeo do médico
`$PY -I $SK/tools/novo_projeto.py <pasta>` → copie o roteiro aprovado para `<pasta>/work/roteiro.json` →
`$PY -I $SK/tools/para_gerar.py <pasta>`: grava `para_gerar.txt` com o texto exato para o ElevenLabs e as
configurações do HeyGen (**9:16, 1080p, fundo verde #00FF00**, expressividade alta). Passe isso para a pessoa e espere
o MP4. Se o vídeo chegar SEM fundo verde, peça de novo com verde (o recorte por IA fica ruim — NOTES).
Com o MP4: `$PY -I $SK/tools/preparar.py <pasta> --video <arquivo>` (voz, recorte, rosto, candidatos de capa)
e `$PY -I $SK/tools/palavras.py <pasta>` (tempo de cada palavra). Se aparecer SUSPEITA de pronúncia (nome de doença,
remédio, sigla), conserte a coluna falada e peça a voz/vídeo de novo — não publique palavra dita errado. Se ela
mudou alguma frase na hora de gerar, ajuste `roteiro.json` para o que foi dito antes de seguir.

## 3. Edição (`work/edicao.json`, modelo `$SK/exemplo/edicao.json`)
Uma cena a cada 2–5 s; `em` = a palavra da fala em que a cena começa. Cena 0 é sempre a capa (rosto + título).
| tipo | para quê | campos |
|---|---|---|
| `rosto` | o médico falando (autoridade) | `plano`: close · xclose · medio; `corte`: true = troca seca |
| `numero` | o dado grande que conta | `valor`, `unidade`, `antes`, `depois`, `valor_em`, `casas`, `prefixo`, **`fonte`** |
| `icones` | "3 em cada 10" | `de` (≤20), `destaque`, `texto`, `depois`, `destaque_em`, **`fonte`** |
| `barras` | comparação (≤5) | `itens:[{nome,valor,destaque,em}]`, `unidade`, `titulo`, **`fonte`** |
| `estudo` | o artigo com marca-texto | `revista`, `ano`, `titulo`, `destaque` (trecho do título), `destaque_em`, ou `imagem` (print), **`fonte`** |
| `mito` | mito × verdade com carimbo | `texto`, `veredito` (mito/verdade), `veredito_em` |
| `lista` | item numerado | `n`, `total`, `texto` |
| `texto` | palavra-chave gigante | `texto` |
| `broll` | 1–3 s de imagem/vídeo em tela cheia (o médico some) | `arquivo` (em assets/img, com licença), `credito` |
| `cta` | pergunta + painel de comentário digitando um exemplo de relato | `em` ("Comenta"), `palavra_em` (onde a digitação começa), `fundo` |
Regras: rosto em close 25–55% do tempo; nunca dois fundos iguais seguidos (automático: escuro/primária/claro);
dado sem `fonte` não monta (o build recusa); b-roll só em rajadas curtas; imagem de paciente não entra.

## 4. Montar, conferir, medir
1. `$PY -I $SK/tools/build.py <pasta>` → `$PY -I $SK/tools/mixar.py <pasta>`.
2. **Olhe** antes de renderizar: `npx --yes hyperframes@0.9.77 snapshot <pasta> --no-end -o <pasta>/work/snaps --at 0,…`
   (o quadro 0 e o meio de cada cena) e abra a folha: título legível e dentro da tela, legenda sem cobrir o rosto,
   nada importante abaixo de y=1560 (interface do app), número parado ≥ 1 s, rosto bem recortado.
3. `$PY -I $SK/tools/render.py <pasta> <Nome>` (≈2 min) → `$PY -I $SK/tools/medir.py <pasta> <pasta>/entrega/<Nome>.mp4`.
   Corrija cada `!!` e renderize de novo (só o som? `mixar.py` + `render.py … --so-som`). Abra `work/folha.jpg`.
4. Capa: abra `work/capa_candidatos.jpg`, escolha a expressão mais forte e rode `$PY -I $SK/tools/capa.py <pasta> <Nome> --t <s>`.
5. `$PY -I $SK/tools/publicar.py <pasta> <Nome>`.

## 5. Entrega
Em `<pasta>/entrega/`: `<Nome>.mp4`, `<Nome>_capa.png`, `<Nome>_publicar.txt`. Diga em 3 linhas: duração, as medidas,
as fontes dos dados — e lembre: **marcar "conteúdo de IA" na plataforma** (é regra do YouTube/Instagram/TikTok para
avatar e voz realistas), vídeo relacionado = o último Short, horário fixo, e que o médico responde pelo conteúdo.
O som você não ouve: peça para a pessoa ouvir uma vez antes de publicar.

## Regras fixas
- Voz = ElevenLabs, vídeo = HeyGen, gerados pela pessoa nos sites (sem integração por API). Não use outra voz nem outro avatar.
- Sem selo "feito com IA" dentro do vídeo (decisão da pessoa); o aviso vai na legenda e no rótulo da plataforma.
- Identificação (nome · MÉDICO · CRM-UF · especialidade · RQE) aparece no vídeo (depois do título e no CTA) e na legenda.
- Nada de "se inscreve", logo, vinheta ou "oi, gente" — o 1º quadro já é rosto + título.
- Vídeo do HeyGen já fechado no rosto (comum): o médico vira busto com a base esfumada nos planos médios — normal.
- Cena com a cor de destaque clara (areia, creme): prefira `"fundo":"primaria"` ou `"escuro"` no CTA.

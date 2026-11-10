# mos-eval — contrato de dados (UI v3.x)

UI do listening test mini-MOS (**protocolo v4**, ICASSP 2027). Uma submissão Netlify Forms (`form-name: mos-eval`) **por página/etapa** — não há mais submit único no fim. Campos do form:

> **Mudanças da v4 (UI 3.0.0, 2026-08-16)** — detalhe no `protocolo_mos` §2/§3/§6:
> 1. `kind` ganha `definitions` e `probe` (a sonda emite submissão própria: a ideia de embuti-la na página seguinte existia para poupar cota, e a cota deixou de morder); **`esa_page` não é emitido no núcleo** (`manifest.esa_enabled: false`), só se a contingência disparar num link separado.
> 2. `rating_page.items[].nat` passa a ser `null` quando a naturalidade não é perguntada; o campo novo `asked_nat` diz qual era o caso. **Filtrar por `asked_nat`, nunca tratar `null` como zero.**
> 3. Trappings de resposta instruída saíram (`placeholders.trapping[].active: false`); o check de atenção agora é o `probe`.
> 4. A seed deixa de vir de convite individual: é sorteada no navegador na primeira visita (6 dígitos) e fixada no URL. Colisão é possível em tese, ~0,05% com 30 raters; conferir duplicatas de `rater_seed` com perfis demográficos incompatíveis antes de analisar.

> **Mudança da UI 3.1.0 (2026-08-24, antes dos convites):** a qualificação passa a exigir `email`, normalizado com `trim().toLowerCase()`. O e-mail aparece somente no `payload_json` da submissão `qualification`; a `rater_seed` liga essa submissão às demais etapas. Seu uso é restrito ao controle de conclusão e ao lembrete, e ele deve ser removido de qualquer dataset analítico ou publicado.

| campo | conteúdo |
|---|---|
| `rater_seed` | seed numérica do rater (vem do URL `?r=`) — identifica o participante |
| `kind` | `qualification` · `headphone` · `definitions` · `rating_page` · `probe` · `pause` · `final` (· `esa_page` só na contingência) |
| `step_id` | id determinístico da etapa (`qual`, `hp`, `definitions`, `training`, `rating_pt_p0..`, `probe_rating_pt_p<N>`, `rating_en_p0..`, `pause1`, `final`; `esa_intro`/`esa_p0..` só na contingência) |
| `payload_json` | JSON com o conteúdo da etapa (abaixo) |
| `timestamp` | ISO-8601 do envio |
| `ui_version` | versão da UI |

## Determinismo (para reproduzir a sessão no `analyze_mos.py`)

- RNG: `mulberry32(xmur3(seed + ":" + proposito))` com streams independentes: `rating_pt`, `rating_en`, `esa`. Mesma seed ⇒ mesma ordem de itens, mesma paginação, mesma ordem intra-par do ESA.
- **Counterbalancing pré-registrado:** seed **par** = EN→PT, **ímpar** = PT→EN.
- A reprodução em Python é opcional: a ordem realizada está registrada nos payloads (`pos`, `first_shown`), que são a fonte primária da análise.
- Paginação: blocos de rating em páginas ≤10 (distribuição equilibrada), ESA ≤9 pares.

## Payloads por `kind`

Todo payload tem `shown_at`, `submitted_at` (ISO-8601) e `debug` (bool — **descartar sessões com `debug: true`**).

- `qualification`: `email`, `age`, `gender|null`, `cefr_en` (A1–C2), `headphones_confirmed`, `consent`, `user_agent`, `screen`, `manifest_version`, `manifest_seed`. `email` existe apenas nesta etapa, em minúsculas e sem espaços nas extremidades; ligar às demais etapas por `rater_seed` e excluir dos dados de análise/publicação.
- `headphone`: `mode: "confirm_only"` (placeholder atual) ou `"trials"` com `answers: [{id, answer, expected, audio}]` e `passed`. Reprovado em `trials` ⇒ sessão encerra (rater não entra no painel).
- `definitions`: só timestamps. Registra que o rater viu a tela de definições operacionais das emoções antes do treino.
- `rating_page`: `block` (`training`/`rating_pt`/`rating_en`), `page_index`, `training` (bool — **treino não conta**), `min_audio_s` (soma das durações dos áudios da página, para a regra de cleansing de duração), `items: [{id, pos, emos, nat, asked_nat, plays, played_ms}]`. `plays` = reproduções completas (evento `ended`). `nat` é `null` sempre que `asked_nat` for `false`.
- `probe` (sonda de conteúdo, protocolo v4 §3): submissão própria, `block`, `target_id` (item do manifest sobre o qual se pergunta, o **último** da página anterior), `options` (as 4 frases exibidas, na ordem em que apareceram), `chosen_text`. **O gabarito não trafega**: a correção compara `chosen_text` com `items[target_id].text` do manifest. Regra de descarte (§6, fixada em 2026-08-16): **erro em qualquer uma das 2 sondas de PORTUGUÊS descarta o rater**; chance de passar por acaso 6,25%. As 2 sondas em inglês são coletadas e reportadas como descritivo, **fora da regra** (frases do ESD curtas e agramaticais demais para servirem de portão a um painel B2). Filtrar por `block` ao aplicar a regra.
- `esa_page`: `page_index` (`-1` = exemplo, `counts: false`), `min_audio_s`, `pairs: [{pair_id, a, b, first_shown, chosen, first_audio, second_audio}]`. `a`/`b` são os ids do manifest; `first_shown` diz qual tocou como "Áudio A" na tela; `chosen` é o **id do item escolhido** (semântica resolvida, não posição).
- `pause`: só timestamps.
- `final`: `comments|null`, `confirmation_code`, `started_at`, `steps_completed`.

## ⚠️ Como ler os dados (medido em 2026-08-16, e não é opcional)

O filtro anti-spam do Netlify deixa passar as **3 a 5 primeiras submissões de uma sessão** e classifica **todo o resto como `spam`**, devolvendo HTTP 200 em todas. Numa sessão real de 22 etapas: 5 `verified`, 17 `spam`. O honeypot `bot-field` está implantado e não altera o comportamento. Nada é perdido, mas:

- O **painel do Netlify, o export CSV e `submission_count` mostram apenas `verified`.** Ler por ali perde ~3/4 do campo, em silêncio.
- A porta de entrada correta é `qwen3-tts/scripts/mos_power/fetch_submissions.py`, que lê os dois baldes (`?state=verified` e `?state=spam`), deduplica por id e grava `data/experiments/mos_field/submissions.jsonl`.
- Rodar periodicamente durante o campo (retenção do balde de spam é desconhecida). A coleta é idempotente.

## Regras de cleansing que dependem destes campos (protocolo §6)

- Trapping/gold: ids e gabaritos estão no `manifest.json` (`is_gold` + `expected`; `esa_pairs[].kind` = `gold`/`trapping` com `expected_winner`) e no mapping privado em `data/experiments/mos_stimuli/private/` (repo qwen3-tts).
- Duração da página: `submitted_at − shown_at < min_audio_s` ⇒ descarta a página.
- Rater incompleto: manter páginas completas (cada página é uma submissão independente).

## Placeholders pendentes no manifest

- ⛔ `placeholders.trapping[]`: **aposentado na v4** (`active: false`). Os 4 áudios gravados em 2026-08-07 continuam em disco e listados, mas a UI não os injeta. Não re-rodar `build_trappings.py`, que voltaria a preencher `audio`.
- `placeholders.headphone_check[]`: adicionar `audio`, `question`, `options: [..]`, `expected` (índice da opção correta) — a UI troca o modo `confirm_only` pelos trials reais com gate de reprovação.
- `esa_pairs[]` com `kind: "trapping"`: preencher `a`/`b` com os ids dos áudios gravados (adicionados a `items` como bloco `esa_extra`).

## Retomada e confiabilidade

- Progresso salvo em `localStorage` (`mos-eval-v1:<seed>`); reabrir o link individual retoma na primeira etapa não concluída.
- Submissões com falha ficam numa fila local e são reenviadas (evento `online`, próximas etapas, botão na tela final); fallback final = download de JSON de backup com todos os payloads.
- Execução local (`localhost`/`file:`) não envia ao Netlify — exporta JSON no fim.

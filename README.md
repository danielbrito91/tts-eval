# tts-eval — listening test mini-MOS (ICASSP 2027)

UI web estática para o listening test do protocolo v3 (P.808 adaptado a painel voluntário): EMOS 1–5 + naturalidade ACR 1–5 por item, bloco final ESA (pares A/B), check de fones, treino, trapping/gold, submissão parcial por página via Netlify Forms e retomada por seed/localStorage.

A versão anterior desta UI (avaliação do PROPOR: MOS/spk-sim/emo-sim, submit único) está no histórico git (`git log -- index.html`).

## Como funciona

- `index.html` — app único, vanilla JS, sem build. Lê `manifest.json` e monta a sessão deterministicamente a partir da seed do rater (`?r=<int>` no URL do convite): ordem dos itens, paginação, counterbalancing PT/EN (paridade da seed) e ordem intra-par do ESA.
- `manifest.json` + `audio/*.wav` — estímulos cegos (111 wavs, loudnorm −26, ids hasheados), gerados por `scripts/mos_power/select_stimuli.py` (repo qwen3-tts, seed 20260721). O mapping id→condição fica **fora** deste repo (`data/experiments/mos_stimuli/private/`).
- Cada página enviada = uma submissão do form `mos-eval` no Netlify. Schema completo e regras de retomada/fallback: [`docs/PAYLOAD.md`](docs/PAYLOAD.md).
- `?debug=1` — desativa validações de escuta e marca os payloads com `debug: true` (descartados na análise).

## Pendências antes do campo

- Gravar os 4 trappings, o trapping-pair do ESA e os 2 trials do check de fones; preencher os `placeholders` do manifest (campos esperados em `docs/PAYLOAD.md`) e recopiar os wavs.
- Piloto com 2 pessoas (~11–15/08); staging no Netlify até ~04/08 valida o submit parcial via Forms.

## Desenvolvimento local

```bash
python3 -m http.server 8000
# http://localhost:8000/?r=1017  (local não envia ao Netlify; exporta JSON no fim)
```

## Deploy

Netlify via CLI ou drag-and-drop (site já existente, coleta via Netlify Forms). O form `mos-eval` é declarado estaticamente no HTML — o Netlify o detecta no deploy.

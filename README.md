# TTS Evaluation System

A web-based system for evaluating Text-to-Speech (TTS) quality through perceptual listening tests, with built-in data analysis tools.

## Features

- **Blind evaluation** of TTS models (VECL vs CML)
- **Multi-dimensional rating**: MOS, Speaker Similarity, Emotion Similarity
- **Cross-lingual evaluation**: EN→PT, PT→EN, same-language
- **Modern UI** with progress tracking and keyboard shortcuts
- **Automatic result collection** (when deployed to Netlify)
- **Data analysis tools** for processing evaluation results

## Live Demo

The evaluation system is already deployed and available at: **[TTS Evaluation System](https://fascinating-licorice-a86265.netlify.app/)**

Results are automatically collected via Netlify Forms.

## Local Development
```bash
uv run python -m http.server 8000
# Visit: http://localhost:8000
```

## File Structure
```
tts-eval/
├── index.html          # Main evaluation interface
├── src/
│   └── prep_eval_data.py # Data processing utilities
├── notebooks/          # Analysis notebooks
├── audio/              # Audio samples
│   ├── refs/          # Reference recordings
│   ├── vecl/          # VECL model outputs  
│   └── cml/           # CML model outputs
├── netlify.toml       # Netlify configuration
└── DEPLOYMENT.md      # Detailed deployment guide
```

## Evaluation Protocol

1. **Quality (MOS)**: Rate naturalness (1-5 scale)
2. **Speaker Similarity**: Compare synthesized vs reference voice
3. **Emotion Similarity**: Compare emotional expression

**32 samples total** • **~20 minutes** • **Requires headphones**

## Results Collection

- **Netlify**: Automatic form submission + CSV export
- **Other platforms**: JSON file downloads

## For Researchers

The system implements a blind evaluation protocol comparing:
- **VECL** vs **CML** models
- **Cross-lingual** vs **same-language** synthesis
- **Multiple emotions**: neutral, happy, sad, angry
- **Multiple speakers**: RAVDESS + custom Portuguese speakers

Results include evaluation times, presentation order, and hidden metadata for analysis.

## Data Analysis

After collecting evaluation results, use the provided analysis tools:

### Processing Results
```bash
# Install dependencies
uv sync

# Process evaluation data
uv run python -c "from src.prep_eval_data import prep_eval_data; df = prep_eval_data(); print(df.groupby('model')['quality'].mean())"
```

### Analysis Features
- **Automatic data parsing** from Netlify form submissions or JSON files
- **Quality metrics** aggregation by model, emotion, and language pair
- **Statistical analysis** of MOS scores, speaker similarity, and emotion similarity
- **Cross-lingual comparison** between EN→PT, PT→EN, and same-language synthesis

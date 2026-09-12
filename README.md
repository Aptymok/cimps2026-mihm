# MIHM · CIMPS2026

**Multinode Homeostatic Integral Model (MIHM)** — motor operacional, notebook de auditoría, evidencia derivada, Hub de reproducibilidad y manuscrito asociado a CIMPS2026, submission 724450.

MIHM se presenta como un marco metodológico de observación centrada en evidencia. No se asume una fórmula física universal entre dominios: cada instrumento declara objeto, pregunta, observables, extractor, referencia, perturbaciones, umbrales, ground truth disponible, estados epistémicos y condiciones de fallo.

## Hub

La superficie académica está en [`hub/index.html`](hub/index.html). Resume:

- proceso auditable DANE/SEN adaptado;
- estado epistémico de cada objeto/modalidad;
- resultados acústicos, visuales, audiovisuales y CTC;
- política de thresholds y blank spaces;
- notebook y evidencia derivada;
- pasos de reproducción.

> El despliegue de GitHub Pages requiere que Pages esté habilitado para este repositorio con **Source: GitHub Actions**. El contenido del Hub ya forma parte del árbol activo aunque Pages no esté habilitado.

## Ejecución rápida

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src pytest -q
python scripts/run_pipeline.py --phase audit
```

## Video por URL

Los videos públicos/autorizados pueden resolverse desde su URL. El proceso registra URL, metadatos y SHA-256 de los bytes recuperados antes de medirlos.

```bash
python scripts/fetch_video_url.py \
  --object REM618 \
  --url "https://youtu.be/JTepOraQwGY" \
  --out evidence/raw/kxtxr/video
```

## CTC

`Fluo-N2DL-HeLa` **no se redistribuye** en este repositorio. El script de ingesta recupera el dataset desde la fuente oficial y permite verificar su identidad antes de ejecutar el protocolo. El ground truth permanece separado de la construcción del instrumento.

```bash
python scripts/fetch_ctc.py --out evidence/raw/ctc
```

## Estructura DANE/SEN adaptada

1. Necesidad de información
2. Diseño
3. Construcción
4. Recolección / ingesta
5. Procesamiento
6. Análisis
7. Difusión
8. Evaluación

La adaptación organiza auditabilidad y reproducibilidad; **no se presenta como fundamento matemático del MIHM**.

## Evidencia publicada

- [`evidence/derived/audio/audio_clean_summary.csv`](evidence/derived/audio/audio_clean_summary.csv)
- [`evidence/derived/image/image_clean_newcovers.csv`](evidence/derived/image/image_clean_newcovers.csv)
- [`evidence/derived/video/video_identity_summary_corrected.csv`](evidence/derived/video/video_identity_summary_corrected.csv)
- [`evidence/derived/ctc/ctc_perturbation_sensitivity.csv`](evidence/derived/ctc/ctc_perturbation_sensitivity.csv)
- [`evidence/derived/blank_space_contract.csv`](evidence/derived/blank_space_contract.csv)
- [`evidence/derived/instrument_threshold_taxonomy.csv`](evidence/derived/instrument_threshold_taxonomy.csv)

## Principios de auditoría

- Toda variable tiene definición, fuente y fórmula o extractor.
- Todo resultado derivado conserva trazabilidad suficiente para reconstrucción.
- Una ausencia no se convierte en cero ni se imputa silenciosamente.
- Los thresholds son específicos del instrumento, salvo demostración independiente de transportabilidad.
- Un resultado negativo se conserva.
- Los estados calculados en dominios distintos no se sustituyen ni promedian por igualdad de escala.

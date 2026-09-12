# MIHM · CIMPS2026

**Multinode Homeostatic Integral Model (MIHM)** — motor operacional, notebook de auditoría, evidencia derivada, Hub público de reproducibilidad y materiales asociados a CIMPS2026, submission **724450**.

**Hub público:** https://aptymok.github.io/cimps2026-mihm/

MIHM se presenta como un marco metodológico de observación centrada en evidencia. No se asume una fórmula física universal entre dominios: cada instrumento declara objeto, pregunta, observables, extractor, referencia, perturbaciones, umbrales, ground truth disponible, estados epistémicos y condiciones de fallo.

## Estado de la entrega

La camera-ready fue enviada a CIMPS2026 con tres archivos separados. Sus SHA-256 se conservan en [`paper/submission/SUBMISSION_FREEZE.md`](paper/submission/SUBMISSION_FREEZE.md) y en [`evidence/manifest.json`](evidence/manifest.json).

El repositorio y el Hub constituyen la superficie de reproducibilidad citada por el manuscrito; no sustituyen los archivos enviados mediante el portal de CIMPS2026.

## Hub

[`hub/index.html`](hub/index.html) / [`hub/home.html`](hub/home.html) presentan:

- proceso auditable DANE/SEN adaptado;
- estado epistémico de cada objeto/modalidad;
- resultados acústicos, visuales, audiovisuales y CTC;
- política de thresholds y blank spaces;
- notebook y evidencia derivada;
- pasos de reproducción;
- snapshot de la entrega y referencias de datos.

GitHub Pages se despliega automáticamente desde `main` mediante [`.github/workflows/pages.yml`](.github/workflows/pages.yml).

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

El video público completo de REM618 se conserva actualmente como `UNRESOLVED_EXTERNAL_FETCH` porque la ejecución neutral en GitHub Actions fue bloqueada por el mecanismo anti-bot/rate-limit de YouTube. No se sustituye ese estado por una inferencia. La medición `0.9886` reportada para REM618 corresponde al **clip audiovisual preservado** que sí fue observado y comparado contra el master; la relación cover ↔ video público permanece `UNRESOLVED`.

## CTC · Fluo-N2DL-HeLa

`Fluo-N2DL-HeLa` **no se redistribuye** en este repositorio. El script de ingesta recupera el dataset desde la fuente oficial y permite verificar su identidad antes de ejecutar el protocolo. El ground truth permanece separado de la construcción del instrumento.

Crédito del proveedor utilizado en el manuscrito:

- **MitoCheck Consortium**.
- Neumann et al., *Phenotypic profiling of the human genome by time-lapse microscopy reveals cell division genes*, Nature 464, 721–727 (2010).
- DOI: https://doi.org/10.1038/nature08869

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
- [`evidence/manifest.json`](evidence/manifest.json)

## Principios de auditoría

- Toda variable tiene definición, fuente y fórmula o extractor.
- Todo resultado derivado conserva trazabilidad suficiente para reconstrucción.
- Una ausencia no se convierte en cero ni se imputa silenciosamente.
- Los thresholds son específicos del instrumento, salvo demostración independiente de transportabilidad.
- Un resultado negativo se conserva.
- Los estados calculados en dominios distintos no se sustituyen ni promedian por igualdad de escala.
- Una URL pública declarada no equivale a un objeto observado hasta que sus bytes hayan sido resueltos y registrados.

## Snapshot científico

Una rama congelada `cimps2026-724450-camera-ready` se mantiene como referencia reproducible del estado correspondiente a la entrega camera-ready. El desarrollo posterior debe ocurrir fuera de esa referencia congelada.

# MIHM · CIMPS2026

**Multinode Homeostatic Integral Model (MIHM) — motor operacional, notebook de auditoría, evidencia derivada y manuscrito CIMPS2026.**

Este repositorio acompaña al artículo académico y contiene una especificación ejecutable y auditable. MIHM no se presenta como teoría matemática universal: cada dominio declara un instrumento computable, sus observables, referencia, perturbaciones, umbrales, ground truth disponible, estados epistémicos y condiciones de fallo.

La rama activa fue reconstruida para la segunda evaluación CIMPS2026. Los artefactos históricos incompatibles ya no forman parte del árbol activo.

## Principio de alcance

MIHM comparte una gramática de observación y evidencia, no features físicas universales. Los valores de estado sólo tienen significado dentro del contrato del instrumento que los produjo. Una relación cross-domain requiere un MTC explícito.

## Ejecución rápida

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src pytest -q
python scripts/run_pipeline.py --phase audit
```

## Datos externos

El dataset Fluo-N2DL-HeLa del Cell Tracking Challenge no se redistribuye. `scripts/fetch_ctc.py` obtiene el archivo desde la fuente oficial y registra su hash. Los medios KXTXR de gran tamaño tampoco se duplican en Git: se resuelven por ruta local autorizada o URL pública/autorizada, y el ledger registra la identidad del recurso medido.

## Estructura de auditoría DANE/SEN adaptada

1. Necesidad de información
2. Diseño
3. Construcción
4. Recolección / ingesta
5. Procesamiento
6. Análisis
7. Difusión
8. Evaluación

La adaptación organiza auditabilidad y reproducibilidad; no se presenta como fundamento matemático del MIHM.

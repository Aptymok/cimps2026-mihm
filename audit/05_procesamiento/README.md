# 5. Procesamiento

**Entrada:** evidencia registrada y contrato del instrumento.

**Operaciones:** preparar la señal según dominio, extraer observables, aplicar normalización declarada y producir el vector de características. Toda transformación conserva configuración y versión.

**Salida:** vector de observables `V_d` + estado epistémico de cada componente.

**Regla:** normalizar a una escala común no vuelve semánticamente equivalentes las coordenadas de dos dominios distintos.

# Sistema Concurrente de Análisis Biométrico con Blockchain Local

**Alumno:** Ian Olmedo 
**Legajo:** 62199 

Este proyecto consiste en la implementación de un sistema concurrente que simula una prueba de esfuerzo médica, en la cual se generan datos biométricos (frecuencia cardíaca, presión arterial y oxígeno en sangre) en tiempo real. Cada tipo de dato es procesado de forma paralela mediante hilos que calculan estadísticas en ventanas móviles de los últimos 30 segundos.

Los resultados son verificados y almacenados en una cadena de bloques local, garantizando integridad y trazabilidad. Finalmente, se realiza una verificación externa de la blockchain para validar su consistencia y generar un informe estadístico.

Este trabajo aplica los conceptos clave de concurrencia y sincronización estudiados en clase, utilizando estructuras como `threading`, `queue`, `lock`, `event` y mecanismos de comunicación segura entre hilos.

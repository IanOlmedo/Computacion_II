# Sistema Concurrente de Análisis Biométrico con Blockchain Local

**Autor:** Ian Olmedo  
**Legajo:** 62199  

Este proyecto implementa un sistema concurrente de análisis biométrico, en el cual se simulan datos fisiológicos de una prueba de esfuerzo (frecuencia cardíaca, presión arterial y oxígeno en sangre). Cada tipo de señal es procesado en paralelo por procesos independientes, que calculan estadísticas sobre ventanas móviles de tiempo.

Los resultados son verificados y almacenados en una cadena de bloques local, garantizando su integridad mediante un sistema de hash encadenado. Además, se incluye un script externo que permite verificar la consistencia de la blockchain y generar un reporte de alertas y promedios generales.

Este trabajo fue desarrollado como parte de la asignatura Computación II, aplicando conceptos de concurrencia, sincronización, comunicación entre procesos (IPC), y estructuras de datos seguras.

---

## Guía de Ejecución

Antes de comenzar, se recomienda la creación de un entorno virtual para aislar las dependencias del proyecto y evitar conflictos con otros entornos de Python instalados en el sistema.

### 1. Crear un entorno virtual (opcional pero recomendado)

Desde la terminal, ubicándose en la carpeta del proyecto:

```bash
python3 -m venv env
source env/bin/activate      # En Linux o MacOS
env\Scripts\activate.bat   # En Windows
```

---

### 2. Instalar las dependencias del proyecto

Una vez activado el entorno virtual, se deben instalar las dependencias necesarias ejecutando:

```bash
pip install -r requirements.txt
```

Este comando instalará los paquetes requeridos (por ejemplo, `numpy`), utilizados para el procesamiento de datos biométricos.

---

### 3. Ejecutar el sistema y generar los datos

Para iniciar la simulación de la prueba de esfuerzo y procesar los datos, ejecutar el siguiente comando:

```bash
python3 main.py
```

Durante su ejecución, el sistema generará datos biométricos simulados, los analizará en paralelo y almacenará los resultados en un archivo llamado `blockchain.json`.

---

### 4. Analizar los datos y generar el reporte final

Finalizada la ejecución del sistema, se puede correr el siguiente script para analizar la cadena generada:

```bash
python3 verificar_cadena.py
```

Este script validará la integridad de la blockchain, verificará si hay alertas o bloques corruptos, y generará un archivo `reporte.txt` con los resultados estadísticos y la cantidad de alertas detectadas.
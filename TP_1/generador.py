# generador.py

import time
import random
from datetime import datetime

def generar_dato():
    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "frecuencia": random.randint(60, 210),
        "presion": [random.randint(110, 220), random.randint(70, 110)],
        "oxigeno": random.randint(85, 100)
    }

def hilo_generador(colas_entrada, evento_fin_generacion):
    """
    colas_entrada: lista con 3 colas (frecuencia, presion, oxigeno)
    """
    for i in range(60):
        dato = generar_dato()
        for cola in colas_entrada:
            cola.put(dato)
        print(f"[Generador] Dato {i+1}/60 generado y enviado: {dato}")
        time.sleep(1)

    evento_fin_generacion.set()
    print("[Generador] Finalizó la generación de datos.")

# generador.py

import time
import random
from datetime import datetime

def generar_dato():
    """Genera un dato biométrico simulado."""
    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "frecuencia": random.randint(60, 180),
        "presion": [random.randint(110, 180), random.randint(70, 110)],
        "oxigeno": random.randint(90, 100)
    }

def hilo_generador(cola_entrada, evento_fin_generacion):
    """
    Hilo que genera un dato por segundo y lo pone en la cola de entrada.
    Al terminar, activa el evento de fin.
    """
    for i in range(60):
        dato = generar_dato()
        cola_entrada.put(dato)
        print(f"[Generador] Dato {i+1}/60 generado y enviado: {dato}")
        time.sleep(1)

    # Avisamos al resto que la generación terminó
    evento_fin_generacion.set()
    print("[Generador] Finalizó la generación de datos.")

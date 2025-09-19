import time
import random
from datetime import datetime

def generar_dato():
    # Data biometrico
    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "frecuencia": random.randint(60, 210),
        "presion": [random.randint(110, 220), random.randint(70, 110)],
        "oxigeno": random.randint(85, 100)
    }

def proceso_generador(pipes_analizadores, evento_fin_generacion):
   # Enviar los datos generados a los analizadores
    print("[Generador] Iniciado.")
    for i in range(60):
        dato = generar_dato()
        for pipe in pipes_analizadores:
            pipe.send(dato)
        print(f"[Generador] Dato {i+1}/60 generado y enviado: {dato}")
        time.sleep(1)

    evento_fin_generacion.set()
    print("[Generador] Finalizado.")

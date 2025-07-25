# analizador.py

from collections import deque
import numpy as np
import threading

def hilo_analizador(tipo, cola_entrada, cola_resultados, evento_fin_generacion):
    """
    tipo: 'frecuencia', 'presion' o 'oxigeno'
    cola_entrada: cola compartida desde la cual se reciben los datos biométricos
    cola_resultados: cola donde se envían los resultados calculados
    evento_fin_generacion: se activa cuando el generador terminó su trabajo
    """
    ventana = deque(maxlen=30)

    print(f"[{threading.current_thread().name}] Iniciado.")

    while not (evento_fin_generacion.is_set() and cola_entrada.empty()):
        try:
            dato = cola_entrada.get(timeout=0.5)  # espera medio segundo
            timestamp = dato["timestamp"]

            if tipo == "frecuencia":
                valor = dato["frecuencia"]
            elif tipo == "presion":
                valor = dato["presion"][0]  # presión sistólica
            elif tipo == "oxigeno":
                valor = dato["oxigeno"]
            else:
                continue

            ventana.append(valor)

            if len(ventana) > 1:
                media = float(np.mean(ventana))
                desv = float(np.std(ventana))

                resultado = {
                    "tipo": tipo,
                    "timestamp": timestamp,
                    "media": media,
                    "desv": desv
                }

                cola_resultados.put(resultado)
                print(f"[{threading.current_thread().name}] Resultado enviado: {resultado}")

            cola_entrada.task_done()

        except Exception as e:
            pass  # Puede ser por timeout cuando la cola está vacía

    print(f"[{threading.current_thread().name}] Finalizado.")

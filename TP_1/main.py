# main.py

import threading
import queue
import time

from generador import hilo_generador
from analizador import hilo_analizador
from verificador import hilo_verificador

def main():
    # Creamos las colas compartidas
    cola_entrada = queue.Queue()  # Del generador hacia los analizadores
    cola_resultados = queue.Queue()  # De los analizadores hacia el verificador

    # Evento para indicar fin del generador
    evento_fin_generacion = threading.Event()

    # Lanzamos el hilo generador (produce 60 datos biométricos, 1 por segundo)
    generador = threading.Thread(target=hilo_generador, args=(cola_entrada, evento_fin_generacion), name="Generador")
    generador.start()

    # Creamos los 3 hilos analizadores
    tipos = ["frecuencia", "presion", "oxigeno"]
    analizadores = []
    for tipo in tipos:
        hilo = threading.Thread(
            target=hilo_analizador,
            args=(tipo, cola_entrada, cola_resultados, evento_fin_generacion),
            name=f"Analizador-{tipo}"
        )
        hilo.start()
        analizadores.append(hilo)

    # Lanzamos el hilo verificador
    verificador = threading.Thread(
        target=hilo_verificador,
        args=(cola_resultados, len(tipos), evento_fin_generacion),
        name="Verificador"
    )
    verificador.start()

    # Esperamos que todos los hilos terminen
    generador.join()
    for hilo in analizadores:
        hilo.join()
    verificador.join()

    print("Todo el procesamiento ha finalizado correctamente.")

if __name__ == "__main__":
    main()

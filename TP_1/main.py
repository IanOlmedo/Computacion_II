import threading
import queue
import time

from generador import hilo_generador
from analizador import hilo_analizador
from verificador import hilo_verificador

def main():
    # Una cola de salida común
    cola_resultados = queue.Queue()

    # Una cola de entrada POR tipo de analizador
    cola_frecuencia = queue.Queue()
    cola_presion = queue.Queue()
    cola_oxigeno = queue.Queue()

    evento_fin_generacion = threading.Event()

    # Hilo generador recibe las 3 colas
    generador = threading.Thread(
        target=hilo_generador,
        args=([cola_frecuencia, cola_presion, cola_oxigeno], evento_fin_generacion),
        name="Generador"
    )
    generador.start()

    # Analizadores (cada uno escucha su propia cola)
    analizadores = []
    for tipo, cola in zip(["frecuencia", "presion", "oxigeno"],
                          [cola_frecuencia, cola_presion, cola_oxigeno]):
        hilo = threading.Thread(
            target=hilo_analizador,
            args=(tipo, cola, cola_resultados, evento_fin_generacion),
            name=f"Analizador-{tipo}"
        )
        hilo.start()
        analizadores.append(hilo)

    # Verificador (escucha resultados)
    verificador = threading.Thread(
        target=hilo_verificador,
        args=(cola_resultados, 3, evento_fin_generacion),
        name="Verificador"
    )
    verificador.start()

    # Esperamos a que todos los hilos terminen
    generador.join()
    for hilo in analizadores:
        hilo.join()
        cola_resultados.put("FIN")
    
    verificador.join()
    

    print("Todo el procesamiento ha finalizado correctamente.")

if __name__ == "__main__":
    main()

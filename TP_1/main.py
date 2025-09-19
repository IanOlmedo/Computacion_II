# main.py

from multiprocessing import Process, Pipe, Queue, Event
from generador import proceso_generador
from analizador import proceso_analizador
from verificador import proceso_verificador
import time

def main():
    # Pipes para enviar datos a los analizadores
    parent_frec, child_frec = Pipe()
    parent_pres, child_pres = Pipe()
    parent_oxi, child_oxi = Pipe()

    cola_resultados = Queue()

    evento_fin_generacion = Event()

    # Lanzar proceso generador
    generador = Process(
        target=proceso_generador,
        args=([parent_frec, parent_pres, parent_oxi], evento_fin_generacion),
        name="ProcesoGenerador"
    )
    generador.start()

    # Lanzar procesos analizadores
    analizador_frec = Process(
        target=proceso_analizador,
        args=("frecuencia", child_frec, cola_resultados, evento_fin_generacion),
        name="AnalizadorFrecuencia"
    )

    analizador_pres = Process(
        target=proceso_analizador,
        args=("presion", child_pres, cola_resultados, evento_fin_generacion),
        name="AnalizadorPresion"
    )

    analizador_oxi = Process(
        target=proceso_analizador,
        args=("oxigeno", child_oxi, cola_resultados, evento_fin_generacion),
        name="AnalizadorOxigeno"
    )

    analizador_frec.start()
    analizador_pres.start()
    analizador_oxi.start()

    # Lanzar verificador
    verificador = Process(
        target=proceso_verificador,
        args=(cola_resultados, 3, evento_fin_generacion),
        name="Verificador"
    )
    verificador.start()

    # esperarar a que terminen los procesos
    generador.join()
    analizador_frec.join()
    analizador_pres.join()
    analizador_oxi.join()

    # Enviar señal de fin al verificador
    cola_resultados.put("FIN")

    verificador.join()

    print(">> Todos los procesos han finalizado correctamente.")

if __name__ == "__main__":
    main()

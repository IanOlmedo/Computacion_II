from multiprocessing import Process, Queue
import time
import random

def productor(q):
    tareas = ['descargar archivo', 'procesar imagen', 'enviar email', 'generar reporte']
    for tarea in tareas:
        print(f"[Productor] Enviando tarea: {tarea}")
        q.put(tarea)
        time.sleep(random.uniform(0.2, 0.6))  
    q.put(None)  # Termina de enviar
    print("[Productor] Envío de tareas finalizado.")

def consumidor(q):
    while True:
        tarea = q.get()
        if tarea is None:
            print("[Consumidor] Señal de fin recibida. Terminando...")
            break
        print(f"[Consumidor] Procesando tarea: {tarea}")
        time.sleep(random.uniform(0.5, 1))  # Simula procesamiento

if __name__ == '__main__':
    cola = Queue()

    p1 = Process(target=productor, args=(cola,))
    p2 = Process(target=consumidor, args=(cola,))

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    print("Proceso principal finalizado.")
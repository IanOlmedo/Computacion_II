from multiprocessing import Process, Queue, current_process
import time
import random

def productor(q_tareas, n_tareas, n_consumidores):
    tareas = [f"Tarea {i}" for i in range(n_tareas)]
    for tarea in tareas:
        print(f"[{current_process().name}] Enviando: {tarea}")
        q_tareas.put(tarea)
        time.sleep(random.uniform(0.1, 0.3))
    
    # Señales de fin para cada consumidor
    for _ in range(n_consumidores):
        q_tareas.put(None)
    print(f"[{current_process().name}] Tareas enviadas y señales de fin colocadas.")

def consumidor(q_tareas, q_resultados):
    while True:
        tarea = q_tareas.get()
        if tarea is None:
            print(f"[{current_process().name}] Recibido fin. Terminando.")
            break
        print(f"[{current_process().name}] Procesando: {tarea}")
        time.sleep(random.uniform(0.3, 0.6))
        resultado = f"{current_process().name} completó {tarea}"
        q_resultados.put(resultado)

def recolector(q_resultados, total_resultados):
    recibidos = 0
    while recibidos < total_resultados:
        resultado = q_resultados.get()
        print(f"[Recolector] Resultado recibido: {resultado}")
        recibidos += 1
    print("[Recolector] Todos los resultados recibidos. Finalizando.")

if __name__ == '__main__':
    N_CONSUMIDORES = 4
    N_TAREAS = 10

    q_tareas = Queue()
    q_resultados = Queue()

    start_time = time.time()

    # Crear procesos
    productor_proc = Process(target=productor, args=(q_tareas, N_TAREAS, N_CONSUMIDORES), name="Productor")
    recolector_proc = Process(target=recolector, args=(q_resultados, N_TAREAS), name="Recolector")

    consumidores = []
    for i in range(N_CONSUMIDORES):
        c = Process(target=consumidor, args=(q_tareas, q_resultados), name=f"Consumidor-{i+1}")
        consumidores.append(c)

    # Iniciar procesos
    productor_proc.start()
    for c in consumidores:
        c.start()
    recolector_proc.start()

    # Esperar que todos terminen
    productor_proc.join()
    for c in consumidores:
        c.join()
    recolector_proc.join()

    end_time = time.time()
    print(f"\n⏱️ Tiempo total de ejecución: {end_time - start_time:.2f} segundos")
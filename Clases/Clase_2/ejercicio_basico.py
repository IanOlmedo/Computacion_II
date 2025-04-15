import os
import time
import random
import signal
from multiprocessing import Process

def hijo(id_hijo, tiempo_inicio):
    """Función que ejecuta cada proceso hijo"""
    tiempo_dormido = random.randint(1, 5)
    time.sleep(tiempo_dormido)
    tiempo_real = time.time() - tiempo_inicio
    print(f"[Hijo-{id_hijo}] PID: {os.getpid():<6} | Durmió: {tiempo_dormido}s | T. Real: {tiempo_real:.2f}s")

def limpiar_procesos(procesos):
    """Función para limpiar procesos en caso de interrupción"""
    for p in procesos:
        if p.is_alive():
            p.terminate()
    print("\n[Padre] Procesos hijos terminados forzosamente")

if __name__ == '__main__':
    procesos = []
    tiempo_inicio = time.time()
    
    # Configurar manejo de Ctrl+C
    signal.signal(signal.SIGINT, lambda s, f: limpiar_procesos(procesos))

    try:
        # Crear 3 procesos hijos
        for i in range(1, 4):
            try:
                p = Process(target=hijo, args=(i, tiempo_inicio))
                p.start()
                procesos.append(p)
                print(f"[Padre] Creado hijo {i} con PID: {p.pid}")
            except Exception as e:
                print(f"[Error] No se pudo crear hijo {i}: {str(e)}")
                continue

        # Esperar a que terminen los hijos en orden
        for i, p in enumerate(procesos, 1):
            if p.is_alive():
                p.join()
            print(f"[Padre] Hijo {i} (PID {p.pid}) terminó con código {p.exitcode}")

    except Exception as e:
        print(f"[Error] Inesperado: {str(e)}")
        limpiar_procesos(procesos)
    finally:
        print("[Padre] Todos los procesos han finalizado")
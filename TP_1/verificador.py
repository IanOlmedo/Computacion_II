# verificador.py

import hashlib
import json
import os
import threading
import time

lock_bloqueo = threading.Lock()  # para sincronizar escritura

def calcular_hash(prev_hash, datos, timestamp):
    contenido = prev_hash + json.dumps(datos, sort_keys=True) + timestamp
    return hashlib.sha256(contenido.encode()).hexdigest()

def cargar_blockchain():
    if not os.path.exists("blockchain.json"):
        return []
    with open("blockchain.json", "r") as f:
        return json.load(f)

def guardar_blockchain(blockchain):
    with lock_bloqueo:
        with open("blockchain.json", "w") as f:
            json.dump(blockchain, f, indent=4)

def hilo_verificador(cola_resultados, cantidad_tipos, evento_fin_generacion):
    """
    Recibe los resultados procesados, agrupa por timestamp, valida y construye bloques.
    """
    print("[Verificador] Iniciado.")

    resultados_pendientes = {}  # agrupados por timestamp
    blockchain = cargar_blockchain()

    prev_hash = blockchain[-1]["hash"] if blockchain else "0"*64
    bloque_index = len(blockchain)

    while not (evento_fin_generacion.is_set() and cola_resultados.empty()):
        try:
            resultado = cola_resultados.get(timeout=0.5)
            ts = resultado["timestamp"]

            if ts not in resultados_pendientes:
                resultados_pendientes[ts] = {}

            resultados_pendientes[ts][resultado["tipo"]] = resultado

            if len(resultados_pendientes[ts]) == cantidad_tipos:
                # Ya tenemos los 3 tipos
                datos = resultados_pendientes.pop(ts)

                alerta = (
                    datos["frecuencia"]["media"] >= 200 or
                    datos["presion"]["media"] >= 200 or
                    not (90 <= datos["oxigeno"]["media"] <= 100)
                )

                bloque = {
                    "index": bloque_index,
                    "timestamp": ts,
                    "datos": datos,
                    "alerta": alerta,
                    "prev_hash": prev_hash,
                    "hash": calcular_hash(prev_hash, datos, ts)
                }

                blockchain.append(bloque)
                guardar_blockchain(blockchain)

                print(f"[Verificador] Bloque #{bloque_index} {'(ALERTA)' if alerta else ''}")
                print(f"Hash: {bloque['hash']}\n")

                bloque_index += 1
                prev_hash = bloque["hash"]

            cola_resultados.task_done()

        except Exception:
            pass  # Puede ser por timeout si la cola está vacía

    print("[Verificador] Finalizado.")

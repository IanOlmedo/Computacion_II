import json
import hashlib
import os

def calcular_hash(prev_hash, datos, timestamp):
    contenido = prev_hash + json.dumps(datos, sort_keys=True) + timestamp
    return hashlib.sha256(contenido.encode()).hexdigest()

def verificar_cadena(blockchain):
    bloques_corruptos = []
    alertas = 0
    total = len(blockchain)

    acumuladores = {
        "frecuencia": [],
        "presion": [],
        "oxigeno": []
    }

    for i, bloque in enumerate(blockchain):
        prev_hash = "0" * 64 if i == 0 else blockchain[i - 1]["hash"]
        hash_recalculado = calcular_hash(prev_hash, bloque["datos"], bloque["timestamp"])

        if bloque["hash"] != hash_recalculado:
            bloques_corruptos.append(i)

        if bloque["alerta"]:
            alertas += 1

        for tipo in acumuladores:
            acumuladores[tipo].append(bloque["datos"][tipo]["media"])

    promedios = {
        k: round(sum(v) / len(v), 2) if v else 0.0
        for k, v in acumuladores.items()
    }

    return {
        "total": total,
        "alertas": alertas,
        "corruptos": bloques_corruptos,
        "promedios": promedios
    }

def generar_reporte(info):
    with open("reporte.txt", "w") as f:
        f.write("=== Reporte de Blockchain ===\n")
        f.write(f"Total de bloques: {info['total']}\n")
        f.write(f"Bloques con alertas: {info['alertas']}\n")
        f.write(f"Bloques corruptos: {info['corruptos']}\n")
        f.write("\nPromedios generales:\n")
        for tipo, valor in info["promedios"].items():
            f.write(f" - {tipo}: {valor:.2f}\n")
    print("[Verificación] Reporte generado en 'reporte.txt'.")

def main():
    if not os.path.exists("blockchain.json"):
        print("[Error] No existe el archivo blockchain.json")
        return

    with open("blockchain.json", "r") as f:
        blockchain = json.load(f)

    info = verificar_cadena(blockchain)
    generar_reporte(info)

if __name__ == "__main__":
    main()

from collections import deque
import numpy as np

def proceso_analizador(tipo, pipe_entrada, cola_resultados, evento_fin_generacion):
    """
    tipo: 'frecuencia', 'presion' o 'oxigeno'
    pipe_entrada: Pipe desde el generador
    cola_resultados: Queue para enviar datos al verificador
    evento_fin_generacion: Event que se activa cuando termina el generador
    """
    print(f"[Analizador-{tipo}] Iniciado.")
    ventana = deque(maxlen=30)

    while not (evento_fin_generacion.is_set() and not pipe_entrada.poll()):
        try:
            if pipe_entrada.poll(timeout=0.5):
                dato = pipe_entrada.recv()
                timestamp = dato["timestamp"]

                if tipo == "frecuencia":
                    valor = dato["frecuencia"]
                elif tipo == "presion":
                    valor = dato["presion"][0] 
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
                    print(f"[Analizador-{tipo}] Resultado enviado: {resultado}")

        except Exception as e:
            print(f"[Analizador-{tipo}] Error: {e}")
            continue

    print(f"[Analizador-{tipo}] Finalizado.")

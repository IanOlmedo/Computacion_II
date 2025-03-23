import argparse

# Crear un parser
parser = argparse.ArgumentParser(description="Ejemplo de argparse")

# Definir argumentos
parser.add_argument("-f", "--file", required=True, help="Archivo")
parser.add_argument("-n", "--number", type=int, required=False, help="Número Entero")
parser.add_argument("-v", "--verbose", action="store_true", help="Modo detallado")

# Procesar argumentos
args = parser.parse_args()

# Usar los valores
print(f"Archivo: {args.file}")
if args.number:
    print(f"Número entero: {args.number}")
if args.verbose:
    print("Modo detallado: Activado")


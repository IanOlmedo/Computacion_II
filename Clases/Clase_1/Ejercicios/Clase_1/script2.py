import sys
import getopt

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:o:", ["help", "input=", "output="])
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)

    input_file = None
    output_file = None

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("Uso: script.py -i <archivo_entrada> -o <archivo_salida>")
            sys.exit()
        elif opt in ("-i", "--input"):
            input_file = arg
        elif opt in ("-o", "--output"):
            output_file = arg
       if not input_file or not output_file:
            print("Error: Debes especificar archivos de entrada y salida.")
            print("Uso: script.py -i <archivo_entrada> -o <archivo_salida>")
            sys.exit(1)
    print(f"Archivo de entrada: {input_file}")
    print(f"Archivo de salida: {output_file}")

if __name__ == "__main__":
    main()


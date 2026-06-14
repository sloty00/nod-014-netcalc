import subprocess
import json
import os

def generar_base_datos_ip():
    # 1. Compilar el núcleo nativo de C++ en el runner de Linux
    subprocess.run(["g++", "calculador.cpp", "-o", "calculador_core"], check=True)
    
    # 2. Ejecutar y capturar las subredes calculadas
    resultado = subprocess.run(["./calculador_core"], capture_output=True, text=True)
    
    lineas = resultado.stdout.strip().split("\n")
    subredes_lista = []
    
    for linea in lineas:
        if "|" in linea:
            parts = linea.split("|")
            subred = {
                "direccion_red": parts[0],
                "primer_ip": parts[1],
                "ultima_ip": parts[2],
                "broadcast": parts[3],
                "mascara": parts[4],
                "hosts": int(parts[5]),
                "prefijo": int(parts[6])
            }
            subredes_lista.append(subred)
            
    # 3. Guardar en la carpeta de datos de la página estática
    os.makedirs("../data", exist_ok=True)
    with open("../data/subredes.json", "w", encoding="utf-8") as f:
        json.dump(subredes_lista, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    generar_base_datos_ip()

import subprocess
import json
import os

def generar_base_datos_ip():
    # 1. Obtener la ruta del directorio donde está este script (src_core)
    dir_actual = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Definir rutas absolutas para evitar fallos de entorno en GitHub Actions
    ruta_cpp = os.path.join(dir_actual, "calculador.cpp")
    ruta_binario = os.path.join(dir_actual, "calculador_core")
    
    print(f"[*] Buscando código fuente en: {ruta_cpp}")
    
    if not os.path.exists(ruta_cpp):
        print("[!] Error crítico: No se encontró calculador.cpp en src_core.")
        # Fallback de emergencia a la raíz de ejecución actual
        ruta_cpp = os.path.join(os.getcwd(), "src_core", "calculador.cpp")
        ruta_binario = os.path.join(os.getcwd(), "src_core", "calculador_core")
    
    # 3. Compilar el núcleo nativo de C++
    print(f"[*] Compilando binario con G++...")
    subprocess.run(["g++", ruta_cpp, "-o", ruta_binario], check=True)
    
    # 4. Ejecutar el binario pasándole parámetros por defecto
    ip_defecto = "192.168.1.0"
    prefijo_defecto = "24"
    print(f"[*] Ejecutando núcleo nativo para {ip_defecto}/{prefijo_defecto}...")
    
    resultado = subprocess.run(
        [ruta_binario, ip_defecto, prefijo_defecto], 
        capture_output=True, 
        text=True, 
        check=True
    )
    
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
            
    # 5. Guardar el JSON en la carpeta /data en la raíz del proyecto
    ruta_salida_data = os.path.join(os.path.dirname(dir_actual), "data")
    os.makedirs(ruta_salida_data, exist_ok=True)
    
    ruta_json_final = os.path.join(ruta_salida_data, "subredes.json")
    with open(ruta_json_final, "w", encoding="utf-8") as f:
        json.dump(subredes_lista, f, indent=4, ensure_ascii=False)
        
    print(f"[+] Éxito: Infraestructura estática generada en {ruta_json_final}")

if __name__ == "__main__":
    generar_base_datos_ip()

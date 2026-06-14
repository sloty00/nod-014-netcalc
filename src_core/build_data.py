import subprocess
import json
import os

def generar_base_datos_ip():
    # 1. Obtener la ruta absoluta del directorio donde está ESTE script (src_core)
    dir_actual = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Definir las rutas absolutas de los archivos de C++
    ruta_cpp = os.path.join(dir_actual, "calculador.cpp")
    ruta_binario = os.path.join(dir_actual, "calculador_core")
    
    print(f"[*] Buscando código fuente en: {ruta_cpp}")
    
    # Verificación de seguridad estricta para GitHub Actions
    if not os.path.exists(ruta_cpp):
        print("[!] Advertencia: calculador.cpp no se encontró en src_core. Forzando ruta alternativa...")
        ruta_cpp = os.path.join(os.getcwd(), "src_core", "calculador.cpp")
        ruta_binario = os.path.join(os.getcwd(), "src_core", "calculador_core")
    
    # 3. Compilar el núcleo nativo de C++ usando las rutas verificadas
    print(f"[*] Compilando binario con G++ en: {ruta_binario}")
    subprocess.run(["g++", ruta_cpp, "-o", ruta_binario], check=True)
    
    # 4. Ejecutar el núcleo pasándole parámetros iniciales seguros (Evita ejecuciones vacías)
    # Aquí puedes cambiar la IP y el prefijo por defecto si deseas otro segmento base en el build
    ip_base_default = "192.168.1.0"
    prefijo_default = "24"
    
    print(f"[*] Ejecutando núcleo de cálculo nativo para {ip_base_default}/{prefijo_default}...")
    resultado = subprocess.run(
        [ruta_binario, ip_base_default, prefijo_default], 
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
            
    # 5. Guardar el JSON siempre en la carpeta /data de la raíz pública del proyecto
    # Si dir_actual es /src_core, el padre es la raíz. Raíz + "data" es lo correcto.
    ruta_salida_data = os.path.join(os.path.dirname(dir_actual), "data")
    os.makedirs(ruta_salida_data, exist_ok=True)
    
    ruta_json_final = os.path.join(ruta_salida_data, "subredes.json")
    with open(ruta_json_final, "w", encoding="utf-8") as f:
        json.dump(subredes_lista, f, indent=4, ensure_ascii=False)
        
    print(f"[+] Éxito: Infraestructura estática generada en {ruta_json_final}")

if __name__ == "__main__":
    generar_base_datos_ip()

import json
import os

def ip_to_int(ip_str):
    """Convierte un string de IP (Ej: 192.168.1.0) a un entero de 32 bits."""
    octetos = list(map(int, ip_str.split('.')))
    return (octetos[0] << 24) | (octetos[1] << 16) | (octetos[2] << 8) | octetos[3]

def int_to_ip(ip_int):
    """Convierte un entero de 32 bits de regreso a formato string de IP."""
    return f"{(ip_int >> 24) & 0xFF}.{(ip_int >> 16) & 0xFF}.{(ip_int >> 8) & 0xFF}.{ip_int & 0xFF}"

def calcular_subred(base_ip, prefijo):
    """Calcula la estructura completa de una subred usando matemática de bits."""
    # Máscara de red de 32 bits
    if prefijo == 0:
        mask = 0
    else:
        mask = (0xFFFFFFFF << (32 - prefijo)) & 0xFFFFFFFF

    ip_entero = ip_to_int(base_ip)
    
    # Operaciones lógicas de red
    direccion_red = ip_entero & mask
    subnet_size = 1 << (32 - prefijo)
    broadcast = direccion_red + subnet_size - 1
    
    # Determinar hosts y rangos útiles
    if prefijo < 31:
        primer_ip = direccion_red + 1
        ultima_ip = broadcast - 1
        hosts = subnet_size - 2
    elif prefijo == 31:
        primer_ip = direccion_red
        ultima_ip = broadcast
        hosts = 2
    else: # /32
        primer_ip = direccion_red
        ultima_ip = direccion_red
        hosts = 1

    return {
        "direccion_red": int_to_ip(direccion_red),
        "primer_ip": int_to_ip(primer_ip),
        "ultima_ip": int_to_ip(ultima_ip),
        "broadcast": int_to_ip(broadcast),
        "mascara": int_to_ip(mask),
        "hosts": hosts,
        "prefijo": prefijo
    }

def generar_base_datos_ip():
    print("[*] Iniciando motor de cálculo nativo en Python...")
    
    # Lista de subredes base que quieres pre-calcular para la carga inicial de tu web
    # ¡Aquí puedes meter todas las que quieras probar (incluyendo las /27)!
    segmentos_objetivo = [
        ("192.168.1.0", 24),
        ("192.168.2.0", 24),
        ("192.168.1.0", 27),
        {"ip": "192.168.1.32", "p": 27}, # Varias de prueba
        ("192.168.1.64", 27),
        ("10.0.0.0", 8),
        ("172.16.0.0", 12)
    ]
    
    subredes_lista = []
    
    for item in segmentos_objetivo:
        # Normalizar si es tupla o diccionario de mapeo
        ip = item[0] if isinstance(item, tuple) else item.get("ip")
        prefijo = item[1] if isinstance(item, tuple) else item.get("p")
        
        try:
            datos_red = calcular_subred(ip, prefijo)
            subredes_lista.append(datos_red)
        except Exception as e:
            print(f"[!] Error procesando {ip}/{prefijo}: {e}")

    # Definir rutas relativas seguras basadas en la ubicación del script
    dir_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_salida_data = os.path.join(os.path.dirname(dir_actual), "data")
    os.makedirs(ruta_salida_data, exist_ok=True)
    
    ruta_json_final = os.path.join(ruta_salida_data, "subredes.json")
    
    with open(ruta_json_final, "w", encoding="utf-8") as f:
        json.dump(subredes_lista, f, indent=4, ensure_ascii=False)
        
    print(f"[+] Éxito total: {len(subredes_lista)} registros estáticos inyectados en {ruta_json_final}")

if __name__ == "__main__":
    generar_base_datos_ip()

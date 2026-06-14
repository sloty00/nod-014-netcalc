import json
import os

def ip_to_int(ip_str):
    """Convierte un string de IP a un entero de 32 bits."""
    octetos = list(map(int, ip_str.split('.')))
    return (octetos[0] << 24) | (octetos[1] << 16) | (octetos[2] << 8) | octetos[3]

def int_to_ip(ip_int):
    """Convierte un entero de 32 bits a formato string de IP."""
    return f"{(ip_int >> 24) & 0xFF}.{(ip_int >> 16) & 0xFF}.{(ip_int >> 8) & 0xFF}.{ip_int & 0xFF}"

def generar_todos_los_tramos(base_ip, prefijo):
    """Calcula TODOS los tramos correlativos para un prefijo determinado dentro de una red clase C."""
    ip_entero = ip_to_int(base_ip)
    
    # Definir máscara
    if prefijo == 0:
        mask = 0
    else:
        mask = (0xFFFFFFFF << (32 - prefijo)) & 0xFFFFFFFF

    # El tamaño de cada bloque individual
    subnet_size = 1 << (32 - prefijo)
    
    # Forzar que la IP base apunte al inicio real de la red con la máscara
    network_base = ip_entero & mask
    
    # Determinar cuántos tramos existen. 
    # Si el prefijo es menor a 24, hacemos solo el primer tramo para no colapsar el JSON.
    # Si es entre 24 y 32, calculamos toda la topología del segmento.
    num_tramos = 1
    if 24 <= prefijo < 32:
        num_tramos = 1 << (prefijo - 24)

    tramos_calculados = []

    for i in range(num_tramos):
        # Calcular el desplazamiento para cada subred correlativa
        actual_subnet_base = network_base + (i * subnet_size)
        actual_broadcast = actual_subnet_base + subnet_size - 1
        
        if prefijo < 31:
            primer_ip = actual_subnet_base + 1
            ultima_ip = actual_broadcast - 1
            hosts = subnet_size - 2
        elif prefijo == 31:
            primer_ip = actual_subnet_base
            ultima_ip = actual_broadcast
            hosts = 2
        else: # /32
            primer_ip = actual_subnet_base
            ultima_ip = actual_subnet_base
            hosts = 1

        subred_info = {
            "direccion_red": int_to_ip(actual_subnet_base),
            "primer_ip": int_to_ip(primer_ip),
            "ultima_ip": int_to_ip(ultima_ip),
            "broadcast": int_to_ip(actual_broadcast),
            "mascara": int_to_ip(mask),
            "hosts": hosts,
            "prefijo": prefijo
        }
        tramos_calculados.append(subred_info)

    return tramos_calculados

def generar_base_datos_ip():
    print("[*] Iniciando motor de cálculo de topologías completas en Python...")
    
    # Definimos los segmentos base del proyecto.
    # Al poner un /26 o un /27, el script generará automáticamente TODOS los tramos que quepan ahí.
    segmentos_config = [
        ("192.168.1.0", 24),
        ("192.168.1.0", 26),  # Generará .0 y .64
        ("192.168.1.0", 27),  # Generará .0, .32, .64, .96, .128, .160, .192, .224
        ("10.0.0.0", 8)       # Un tramo base de clase A
    ]
    
    subredes_lista = []
    
    for ip, prefijo in segmentos_config:
        try:
            tramos = generar_todos_los_tramos(ip, prefijo)
            subredes_lista.extend(tramos)
        except Exception as e:
            print(f"[!] Error procesando el segmento {ip}/{prefijo}: {e}")

    # Rutas para el despliegue
    dir_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_salida_data = os.path.join(os.path.dirname(dir_actual), "data")
    os.makedirs(ruta_salida_data, exist_ok=True)
    
    ruta_json_final = os.path.join(ruta_salida_data, "subredes.json")
    
    with open(ruta_json_final, "w", encoding="utf-8") as f:
        json.dump(subredes_lista, f, indent=4, ensure_ascii=False)
        
    print(f"[+] Éxito: {len(subredes_lista)} tramos totales guardados en {ruta_json_final}")

if __name__ == "__main__":
    generar_base_datos_ip()

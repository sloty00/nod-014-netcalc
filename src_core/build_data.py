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
    """Calcula TODOS los tramos correlativos para el prefijo."""
    ip_entero = ip_to_int(base_ip)
    
    if prefijo == 0:
        mask = 0
    else:
        mask = (0xFFFFFFFF << (32 - prefijo)) & 0xFFFFFFFF

    subnet_size = 1 << (32 - prefijo)
    network_base = ip_entero & mask
    
    num_tramos = 1
    if 24 <= prefijo < 32:
        num_tramos = 1 << (prefijo - 24)

    tramos_calculados = []

    for i in range(num_tramos):
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
        else:
            primer_ip = actual_subnet_base
            ultima_ip = actual_subnet_base
            hosts = 1

        # CRUCIAL: Mantenemos la 'direccion_red' como la IP base consultada (ej: 192.168.1.0)
        # para que el buscador del frontend agrupe y muestre TODOS los tramos juntos.
        # Guardamos el segmento real en el rango de IPs para que se note la división.
        subred_info = {
            "direccion_red": base_ip,  # Permite que al buscar "192.168.1.0/26" aparezcan todas
            "primer_ip": int_to_ip(primer_ip),
            "ultima_ip": int_to_ip(ultima_ip),
            "broadcast": int_to_ip(actual_broadcast),
            "mascara": int_to_ip(mask),
            "hosts": hosts,
            "prefijo": f"/{prefijo}"
        }
        tramos_calculados.append(subred_info)

    return tramos_calculados

def generar_base_datos_ip():
    print("[*] Generando base de datos JSON compatible con el buscador...")
    
    subredes_lista = []
    
    # Pre-calcular esquemas comunes sobre la IP base clásica
    for p in [24, 25, 26, 27, 28, 29, 30, 31, 32]:
        subredes_lista.extend(generar_todos_los_tramos("192.168.1.0", p))
        
    # Redes de prueba extra para validar robustez
    subredes_lista.extend(generar_todos_los_tramos("10.0.0.0", 8))
    subredes_lista.extend(generar_todos_los_tramos("172.16.0.0", 12))

    dir_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_salida_data = os.path.join(os.path.dirname(dir_actual), "data")
    os.makedirs(ruta_salida_data, exist_ok=True)
    
    ruta_json_final = os.path.join(ruta_salida_data, "subredes.json")
    
    with open(ruta_json_final, "w", encoding="utf-8") as f:
        json.dump(subredes_lista, f, indent=4, ensure_ascii=False)
        
    print(f"[+] Archivo JSON actualizado con {len(subredes_lista)} tramos vinculados.")

if __name__ == "__main__":
    generar_base_datos_ip()

#include <iostream>
#include <vector>
#include <string>
#include <sstream>

// Función auxiliar para convertir enteros de 32 bits a strings de IP en formato decimal punteado
std::string intToIP(unsigned int ip) {
    std::ostringstream ss;
    ss << ((ip >> 24) & 0xFF) << "."
       << ((ip >> 16) & 0xFF) << "."
       << ((ip >> 8) & 0xFF) << "."
       << (ip & 0xFF);
    return ss.str();
}

int main() {
    // Lista de subredes base para precalcular en el build-time
    // Esto simula la generación nativa de segmentos fijos o dinámicos en entornos corporativos
    struct BaseNet {
        std::string ip_base;
        int prefijo;
    };

    std::vector<BaseNet> segmentos_base = {
        {"192.168.1.0", 24},
        {"192.168.2.0", 24},
        {"192.168.3.0", 24},
        {"192.168.4.0", 24},
        {"192.168.5.0", 24},
        {"192.168.6.0", 24},
        {"192.168.7.0", 24},
        {"192.168.8.0", 24}
    };

    for (const auto& net : segmentos_base) {
        // Parsear la IP base básica para operar con máscaras de bits
        unsigned int oct1, oct2, oct3, oct4;
        char ch;
        std::stringstream ss(net.ip_base);
        ss >> oct1 >> ch >> oct2 >> ch >> oct3 >> ch >> oct4;

        unsigned int ip_num = (oct1 << 24) | (oct2 << 16) | (oct3 << 8) | oct4;
        
        // Calcular Máscara de Subred mediante desplazamiento seguro usando literales Unsigned (U)
        unsigned int mask = 0;
        if (net.prefijo > 0) {
            mask = (net.prefijo == 32) ? ~0U : ~(~0U >> net.prefijo);
        }
        
        // Operaciones lógicas de red (Bitwise)
        unsigned int network_ip = ip_num & mask;
        unsigned int broadcast_ip = network_ip | ~mask;
        unsigned int first_ip = network_ip + 1;
        unsigned int last_ip = broadcast_ip - 1;
        
        // Control de hosts para prefijos especiales /31 y /32
        int num_hosts = 0;
        if (net.prefijo < 31) {
            num_hosts = broadcast_ip - network_ip - 1;
        } else if (net.prefijo == 31) {
            num_hosts = 2; // Enlaces punto a punto (RFC 3021)
        } else {
            num_hosts = 1; // Host único /32
        }

        // Salida estructurada limpia con delimitador '|' para el parseador de Python
        std::cout << intToIP(network_ip) << "|"
                  << intToIP(first_ip) << "|"
                  << intToIP(last_ip) << "|"
                  << intToIP(broadcast_ip) << "|"
                  << intToIP(mask) << "|"
                  << num_hosts << "|"
                  << net.prefijo << "\n";
    }

    return 0;
}

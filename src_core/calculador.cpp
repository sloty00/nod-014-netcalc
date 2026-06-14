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
    struct BaseNet {
        std::string ip_base;
        int prefijo;
    };

    // Matriz de infraestructura expandida con múltiples prefijos para pruebas del Frontend
    std::vector<BaseNet> segmentos_base = {
        {"192.168.1.0", 24},
        {"192.168.2.0", 24},
        {"10.0.0.0", 8},
        {"172.16.0.0", 12},
        // Segmentos de subredes con prefijo /27 para validar tu filtro instantáneo
        {"192.168.1.0", 27},
        {"192.168.1.32", 27},
        {"192.168.1.64", 27},
        // Otros prefijos críticos de alta densidad
        {"192.168.1.96", 28},
        {"192.168.1.112", 30}
    };

    for (const auto& net : segmentos_base) {
        unsigned int oct1, oct2, oct3, oct4;
        char ch;
        std::stringstream ss(net.ip_base);
        ss >> oct1 >> ch >> oct2 >> ch >> oct3 >> ch >> oct4;

        unsigned int ip_num = (oct1 << 24) | (oct2 << 16) | (oct3 << 8) | oct4;
        
        unsigned int mask = 0;
        if (net.prefijo > 0) {
            mask = (net.prefijo == 32) ? ~0U : ~(~0U >> net.prefijo);
        }
        
        unsigned int network_ip = ip_num & mask;
        unsigned int broadcast_ip = network_ip | ~mask;
        unsigned int first_ip = network_ip + 1;
        unsigned int last_ip = broadcast_ip - 1;
        
        int num_hosts = 0;
        if (net.prefijo < 31) {
            num_hosts = broadcast_ip - network_ip - 1;
        } else if (net.prefijo == 31) {
            num_hosts = 2;
        } else {
            num_hosts = 1;
        }

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

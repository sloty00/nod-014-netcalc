#include <iostream>
#include <sstream>
#include <string>
#include <vector>

using namespace std;

// Función para convertir una dirección IP a un número entero
uint32_t ipToInt(const string& ip) {
    uint32_t result = 0;
    istringstream iss(ip);
    string byte;
    while (getline(iss, byte, '.')) {
        result = (result << 8) | stoi(byte);
    }
    return result;
}

// Función para convertir un número entero a una dirección IP
string intToIp(uint32_t ip) {
    ostringstream oss;
    oss << ((ip >> 24) & 0xFF) << '.'
        << ((ip >> 16) & 0xFF) << '.'
        << ((ip >> 8) & 0xFF) << '.'
        << (ip & 0xFF);
    return oss.str();
}

int main(int argc, char* argv[]) {
    // Parámetros por defecto para que el pipeline no se detenga
    string baseIP = "192.168.1.0";
    int prefix = 24;

    // Si Python pasa argumentos por consola, los capturamos
    if (argc >= 3) {
        baseIP = argv[1];
        prefix = stoi(argv[2]);
    }

    // 1. CÁLCULO DE MÁSCARA SEGURA
    uint32_t mask = 0;
    if (prefix > 0) {
        mask = (prefix == 32) ? 0xFFFFFFFF : ~((1ULL << (32 - prefix)) - 1);
    }

    // 2. TAMAÑO DE LA SUBRED (Definición global para evitar el error de scope)
    uint32_t subnetSize = (prefix == 32) ? 1 : (1U << (32 - prefix));
    
    // 3. NÚMERO DE ITERACIONES
    int numSubnets = 1;
    if (prefix >= 24 && prefix < 32) {
        numSubnets = 1 << (prefix - 24);
    }

    uint32_t baseIpInt = ipToInt(baseIP);

    // Bucle de renderizado de segmentos
    for (int i = 0; i < numSubnets; ++i) {
        uint32_t subnetBase = (baseIpInt & mask) + (i * subnetSize);
        uint32_t broadcastBase = subnetBase + subnetSize - 1;
        
        string subnetIP = intToIp(subnetBase);
        string broadcastIP = intToIp(broadcastBase);
        string firstHostIP = (prefix == 32) ? intToIp(subnetBase) : intToIp(subnetBase + 1);
        string lastHostIP = (prefix == 32) ? intToIp(subnetBase) : intToIp(broadcastBase - 1);
        string maskIP = intToIp(mask);
        
        // Aquí se usa subnetSize de forma totalmente segura
        int hosts = (prefix < 31) ? (subnetSize - 2) : (prefix == 31 ? 2 : 1);

        // Salida limpia para que build_data.py parsee el JSON
        cout << subnetIP << "|"
             << firstHostIP << "|"
             << lastHostIP << "|"
             << broadcastIP << "|"
             << maskIP << "|"
             << hosts << "|"
             << prefix << "\n";
    }

    return 0;
}

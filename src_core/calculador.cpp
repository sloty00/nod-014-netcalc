#include <iostream>
#include <sstream>
#include <string>

using namespace std;

// Función para convertir una dirección IP a un número entero de 32 bits
uint32_t ipToInt(const string& ip) {
    uint32_t result = 0;
    istringstream iss(ip);
    string byte;
    while (getline(iss, byte, '.')) {
        result = (result << 8) | stoi(byte);
    }
    return result;
}

// Función para convertir un número entero de 32 bits a formato IP string
string intToIp(uint32_t ip) {
    ostringstream oss;
    oss << ((ip >> 24) & 0xFF) << '.'
        << ((ip >> 16) & 0xFF) << '.'
        << ((ip >> 8) & 0xFF) << '.'
        << (ip & 0xFF);
    return oss.str();
}

int main(int argc, char* argv[]) {
    // Valores base por defecto
    string baseIP = "192.168.1.0";
    int prefix = 24;

    // Recolectar de forma segura los argumentos inyectados desde el script de Python
    if (argc >= 3) {
        baseIP = argv[1];
        prefix = stoi(argv[2]);
    }

    // Calcular la máscara previniendo comportamientos indefinidos en arquitecturas de 32/64 bits
    uint32_t mask = 0;
    if (prefix > 0) {
        mask = (prefix == 32) ? 0xFFFFFFFF : ~((1ULL << (32 - prefix)) - 1);
    }

    uint32_t subnetSize = (prefix == 32) ? 1 : (1U << (32 - prefix));
    uint32_t baseIpInt = ipToInt(baseIP);

    // Aplicar máscara binaria para encontrar el inicio del segmento
    uint32_t subnetBase = baseIpInt & mask;
    uint32_t broadcastBase = subnetBase + subnetSize - 1;
    
    // Calcular cantidad de hosts direccionables reales
    int hosts = (prefix < 31) ? (subnetSize - 2) : (prefix == 31 ? 2 : 1);

    // Formatear salida estándar mediante delimitador pipe (|) para el parser de Python
    cout << intToIp(subnetBase) << "|"
         << intToIp(subnetBase + 1) << "|"
         << intToIp(broadcastBase - 1) << "|"
         << intToIp(broadcastBase) << "|"
         << intToIp(mask) << "|"
         << hosts << "|"
         << prefix << "\n";

    return 0;
}

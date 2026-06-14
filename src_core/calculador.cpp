#include <iostream>
#include <sstream>
#include <string>
#include <vector>

using namespace std;

uint32_t ipToInt(const string& ip) {
    uint32_t result = 0;
    istringstream iss(ip);
    string byte;
    while (getline(iss, byte, '.')) {
        result = (result << 8) | stoi(byte);
    }
    return result;
}

string intToIp(uint32_t ip) {
    ostringstream oss;
    oss << ((ip >> 24) & 0xFF) << '.'
        << ((ip >> 16) & 0xFF) << '.'
        << ((ip >> 8) & 0xFF) << '.'
        << (ip & 0xFF);
    return oss.str();
}

int main(int argc, char* argv[]) {
    // Valores por defecto si no se pasan argumentos (Evita que el pipeline falle)
    string baseIP = "192.168.1.0";
    int prefix = 24;

    // Si el script de Python le pasa parámetros, los usamos
    if (argc >= 3) {
        baseIP = argv[1];
        prefix = stoi(argv[2]);
    }

    // Cálculos de bits basados en tu ejemplo
    uint32_t mask = (prefix == 0) ? 0 : (~0 << (32 - prefix)) >>> 0; 
    if (prefix == 32) mask = 0xFFFFFFFF;
    
    uint32_t baseIpInt = ipToInt(baseIP);
    uint32_t subnetSize = 1 << (32 - prefix);
    
    // Evitar desbordes de memoria si el prefijo es muy bajo
    int numSubnets = 1;
    if (prefix >= 24 && prefix < 32) {
        numSubnets = 1 << (prefix - 24);
    }

    // Retornamos los datos formateados en texto plano para que Python los capture
    for (int i = 0; i < numSubnets; ++i) {
        uint32_t subnetBase = (baseIpInt & mask) + (i * subnetSize);
        uint32_t broadcastBase = subnetBase + subnetSize - 1;
        
        int hosts = (prefix < 31) ? (subnetSize - 2) : (prefix == 31 ? 2 : 1);

        cout << intToIp(subnetBase) << "|"
             << intToIp(subnetBase + 1) << "|"
             << intToIp(broadcastBase - 1) << "|"
             << intToIp(broadcastBase) << "|"
             << intToIp(mask) << "|"
             << hosts << "|"
             << prefix << "\n";
    }

    return 0;
}

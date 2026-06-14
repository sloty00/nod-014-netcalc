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
    string baseIP = "192.168.1.0";
    int prefix = 24;

    if (argc >= 3) {
        baseIP = argv[1];
        prefix = stoi(argv[2]);
    }

    uint32_t mask = (prefix == 0) ? 0 : ~((1ULL << (32 - prefix)) - 1);
    if (prefix == 32) mask = 0xFFFFFFFF;

    uint32_t baseIpInt = ipToInt(baseIP);
    uint32_t subnetSize = (prefix == 32) ? 1 : (1U << (32 - prefix));
    
    int numSubnets = 1;
    if (prefix >= 24 && prefix < 32) {
        numSubnets = 1 << (prefix - 24);
    }

    for (int i = 0; i < numSubnets; ++i) {
        uint32_t subnetBase = (baseIpInt & mask) + (i * subnetSize);
        uint32_t broadcastBase = subnetBase + subnetSize - 1;
        
        string subnetIP = intToIp(subnetBase);
        string broadcastIP = intToIp(broadcastBase);
        string firstHostIP = (prefix == 32) ? intToIp(subnetBase) : intToIp(subnetBase + 1);
        string lastHostIP = (prefix == 32) ? intToIp(subnetBase) : intToIp(broadcastBase - 1);
        string maskIP = intToIp(mask);
        
        int hosts = (prefix < 31) ? (subnetSize - 2) : (prefix == 31 ? 2 : 1);

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

document.addEventListener("DOMContentLoaded", () => {
    const tabla = document.getElementById("tabla-subredes");
    const filtroInput = document.getElementById("ip-filter");
    let todasLasSubredes = []; // Guarda las subredes base iniciales

    // 1. Forzar tabla limpia al iniciar (Inicialización vacía)
    const pathBase = window.location.pathname.endsWith('/') ? window.location.pathname : window.location.pathname + '/';
    const dataUrl = `${window.location.origin}${pathBase}data/subredes.json?v=${new Date().getTime()}`;

    if (tabla) {
        // Inicializamos vacío explícitamente para limpiar la vista inicial
        todasLasSubredes = []; 
        renderizarTabla(todasLasSubredes);
        
        // Mantenemos la consulta por compatibilidad de arquitectura
        fetch(dataUrl)
            .then(res => res.ok ? res.json() : [])
            .then(data => {
                // Si el JSON contiene datos válidos, los asigna, pero la grilla se mantendrá limpia si está vacío
                todasLasSubredes = Array.isArray(data) ? data : [];
                if (todasLasSubredes.length > 0) {
                    renderizarTabla(todasLasSubredes);
                }
            })
            .catch(() => {
                // Silenciamos errores para mantener una interfaz limpia sin alertas innecesarias
            });
    }

    // 2. FUNCIÓN DE CÁLCULO DINÁMICO (Lógica Bitwise en Frontend)
    function calcularSubredDinamica(ipString, prefijo) {
        const octetos = ipString.split('.').map(Number);
        if (octetos.length !== 4 || octetos.some(isNaN) || octetos.some(o => o < 0 || o > 255)) return null;
        if (prefijo < 0 || prefijo > 32 || isNaN(prefijo)) return null;

        // Convertir IP a entero de 32 bits
        const ipNum = (octetos[0] << 24) >>> 0 | (octetos[1] << 16) | (octetos[2] << 8) | octetos[3];

        // Calcular máscara
        const maskNum = prefijo === 0 ? 0 : (~0 << (32 - prefijo)) >>> 0;

        // Operaciones de red
        const netNum = (ipNum & maskNum) >>> 0;
        const broadNum = (netNum | ~maskNum) >>> 0;

        const firstNum = netNum + 1;
        const lastNum = broadNum - 1;

        // Formatear enteros a string IP
        const longToIP = (num) => [
            (num >>> 24) & 255,
            (num >>> 16) & 255,
            (num >>> 8) & 255,
            num & 255
        ].join('.');

        let hosts = 0;
        if (prefijo < 31) hosts = broadNum - netNum - 1;
        else if (prefijo === 31) hosts = 2;
        else hosts = 1;

        return {
            direccion_red: longToIP(netNum),
            primer_ip: prefijo === 32 ? longToIP(netNum) : longToIP(firstNum),
            ultima_ip: prefijo === 32 ? longToIP(netNum) : longToIP(lastNum),
            broadcast: prefijo === 32 ? longToIP(netNum) : longToIP(broadNum),
            mascara: longToIP(maskNum),
            hosts: hosts,
            prefijo: prefijo
        };
    }

    function renderizarTabla(lista) {
        if (!tabla) return;
        if (lista.length === 0) {
            tabla.innerHTML = `<tr><td colspan="7" style="color: #8b949e; text-align: center;">No hay coincidencias o formato inválido.</td></tr>`;
            return;
        }
        tabla.innerHTML = lista.map(item => `
            <tr>
                <td style="color: #ff7b72; font-weight: bold;">${item.direccion_red}</td>
                <td style="color: #a5d6ff;">${item.primer_ip}</td>
                <td style="color: #a5d6ff;">${item.ultima_ip}</td>
                <td style="color: #79c0ff;">${item.broadcast}</td>
                <td>${item.mascara}</td>
                <td style="color: #58a6ff;">${item.hosts}</td>
                <td>/${item.prefijo}</td>
            </tr>
        `).join('');
    }

    // 3. ESCUCHA REACTIVA INTELIGENTE (Multi-Tramo Correlativo)
    if (filtroInput) {
        filtroInput.addEventListener("input", (e) => {
            const valor = e.target.value.trim();

            // Detectar si el usuario metió una estructura completa CIDR (Ej: 192.168.1.0/27)
            if (valor.includes('/')) {
                const partes = valor.split('/');
                const ipParte = partes[0];
                const prefijoParte = parseInt(partes[1], 10);

                // Validamos que el prefijo ingresado sea un número de red válido
                if (!isNaN(prefijoParte) && prefijoParte >= 0 && prefijoParte <= 32) {
                    
                    // Si el prefijo es menor a 24, calculamos solo la subred específica de esa IP para evitar bucles gigantes
                    if (prefijoParte < 24) {
                        const resultadoDinamico = calcularSubredDinamica(ipParte, prefijoParte);
                        if (resultadoDinamico) {
                            renderizarTabla([resultadoDinamico]);
                            return;
                        }
                    } else {
                        // Para prefijos >= 24, calculamos de manera automática TODOS los tramos correlativos de la red
                        const octetos = ipParte.split('.').map(Number);
                        if (octetos.length === 4 && !octetos.some(isNaN) && !octetos.some(o => o < 0 || o > 255)) {
                            
                            const tamañoSubred = 1 << (32 - prefijoParte); // Cuántas IPs ocupa cada bloque
                            const cantidadTramos = 1 << (prefijoParte - 24); // Cuántos bloques caben en el último octeto
                            
                            const listaDeTramos = [];
                            
                            // Forzar que el cálculo comience desde la base real de la red con una operación de bits
                            const ipNumBase = (octetos[0] << 24) >>> 0 | (octetos[1] << 16) | (octetos[2] << 8) | octetos[3];
                            const maskNumBase = (~0 << (32 - prefijoParte)) >>> 0;
                            const netNumBase = (ipNumBase & maskNumBase) >>> 0;
                            
                            // Iteramos para calcular consecutivamente cada uno de los tramos (.0, .32, .64, etc.)
                            for (let i = 0; i < cantidadTramos; i++) {
                                const cuartoOctetoCalculado = (netNumBase & 255) + (i * tamañoSubred);
                                
                                // Construimos el string IP para mapear el tramo actual
                                const ipTramo = `${octetos[0]}.${octetos[1]}.${octetos[2]}.${cuartoOctetoCalculado}`;
                                const datosTramo = calcularSubredDinamica(ipTramo, prefijoParte);
                                
                                if (datosTramo) {
                                    listaDeTramos.push(datosTramo);
                                }
                            }
                            
                            if (listaDeTramos.length > 0) {
                                renderizarTabla(listaDeTramos); // Imprime la topología completa en pantalla
                                return;
                            }
                        }
                    }
                }
            }

            // Si no contiene la barra "/" o el cuadro de texto se limpia, vuelve al estado inicial (vacío)
            const busqueda = valor.toLowerCase();
            const filtradas = todasLasSubredes.filter(item => 
                item.direccion_red.toLowerCase().includes(busqueda) || 
                item.mascara.includes(busqueda)
            );
            renderizarTabla(filtradas);
        });
    }
});

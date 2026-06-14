document.addEventListener("DOMContentLoaded", () => {
    const tabla = document.getElementById("tabla-subredes");
    const filtroInput = document.getElementById("ip-filter");
    let todasLasSubredes = []; // Caché local de datos

    // 1. Resolver ruta base dinámica para soportar el subdirectorio de GitHub Pages
    const pathBase = window.location.pathname.endsWith('/') ? window.location.pathname : window.location.pathname + '/';
    const dataUrl = `${window.location.origin}${pathBase}data/subredes.json?v=${new Date().getTime()}`;

    // Validación temprana del DOM
    if (!tabla) {
        console.error("Error estructural: No se encontró el elemento con ID 'tabla-subredes'.");
        return;
    }

    // 2. Cargar los datos precalculados por el backend híbrido (C++ / Python)
    fetch(dataUrl)
        .then(res => {
            if (!res.ok) {
                throw new Error(`HTTP error! Estado: ${res.status} - Verifica que el pipeline haya generado el archivo.`);
            }
            return res.json();
        })
        .then(data => {
            todasLasSubredes = Array.isArray(data) ? data : [];
            if (todasLasSubredes.length === 0) {
                tabla.innerHTML = `<tr><td colspan="7" style="color: #ffa657; text-align: center;">⚠️ Matriz de red vacía. Esperando inicialización de datos.</td></tr>`;
            } else {
                renderizarTabla(todasLasSubredes);
            }
        })
        .catch(err => {
            console.error("Error al sincronizar mapa de red:", err);
            tabla.innerHTML = `<tr><td colspan="7" style="color: #ff7b72; text-align: center;">⚠️ Error en el enlace de datos. Asegúrate de que el pipeline de GitHub Actions haya terminado con éxito.</td></tr>`;
        });

    // 3. Función de renderizado optimizada con salvaguardas (Fallbacks)
    function renderizarTabla(lista) {
        tabla.innerHTML = lista.map(item => `
            <tr>
                <td style="color: #ff7b72; font-weight: bold;">${item.direccion_red || '0.0.0.0'}</td>
                <td style="color: #a5d6ff;">${item.primer_ip || '0.0.0.0'}</td>
                <td style="color: #a5d6ff;">${item.ultima_ip || '0.0.0.0'}</td>
                <td style="color: #79c0ff;">${item.broadcast || '0.0.0.0'}</td>
                <td>${item.mascara || '255.255.255.0'}</td>
                <td style="color: #58a6ff;">${item.hosts !== undefined ? item.hosts : 0}</td>
                <td>/${item.prefijo || 0}</td>
            </tr>
        `).join('');
    }

    // 4. Filtro reactivo en tiempo real protegido contra valores nulos
    if (filtroInput) {
        filtroInput.addEventListener("input", (e) => {
            const busqueda = e.target.value.trim().toLowerCase();
            
            const filtradas = todasLasSubredes.filter(item => {
                const red = item.direccion_red ? item.direccion_red.toLowerCase() : '';
                const mask = item.mascara ? item.mascara.toLowerCase() : '';
                const pref = item.prefijo ? item.prefijo.toString() : '';
                
                return red.includes(busqueda) || mask.includes(busqueda) || pref.includes(busqueda);
            });
            
            renderizarTabla(filtradas);
        });
    } else {
        console.warn("Advertencia: No se detectó el input '#ip-filter' para la búsqueda.");
    }
});

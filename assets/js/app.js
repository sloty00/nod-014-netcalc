document.addEventListener("DOMContentLoaded", () => {
    const tabla = document.getElementById("tabla-subredes");
    const filtroInput = document.getElementById("ip-filter");
    let todasLasSubredes = []; // Caché local de datos

    // Cargar los datos precalculados por el backend híbrido
    fetch(`./data/subredes.json?v=${new Date().getTime()}`)
        .then(res => res.json())
        .then(data => {
            todasLasSubredes = data;
            renderizarTabla(todasLasSubredes);
        })
        .catch(err => {
            console.error("Error al sincronizar mapa de red:", err);
            tabla.innerHTML = `<tr><td colspan="7" style="color: #ff7b72; text-align: center;">⚠️ Error en el enlace de datos.</td></tr>`;
        });

    function renderizarTabla(lista) {
        tabla.innerHTML = lista.map(item => `
            <tr>
                <td style="color: #ff7b72; font-weight: bold;">${item.direccion_red}</td>
                <td style="color: #a5d6ff;">${item.primer_ip}</td>
                <td style="color: #a5d6ff;">${item.ultima_ip}</td>
                <td style="color: #79c0ff;">${item.broadcast}</td>
                <td>${item.mascara}</td>
                <td style="color: #58a6ff;">${item.hosts}</td>
                <td>${item.prefijo}</td>
            </tr>
        `).join('');
    }

    // Filtro instantáneo por teclado
    filtroInput.addEventListener("input", (e) => {
        const busqueda = e.target.value.trim().toLowerCase();
        const filtradas = todasLasSubredes.filter(item => 
            item.direccion_red.toLowerCase().includes(busqueda) || 
            item.mascara.includes(busqueda)
        );
        renderizarTabla(filtradas);
    });
});


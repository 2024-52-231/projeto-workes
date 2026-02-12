document.getElementById("sandwich-menu").addEventListener("click", () => {
    document.getElementById("nav-drawer").classList.toggle("open");
});

document.getElementById("search-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const query = document.getElementById("search-input").value.trim();
    const container = document.getElementById("results-container");

    container.innerHTML = "<p class='placeholder-text'>Buscando...</p>";

    const resposta = await fetch("/buscar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query })
    });

    const dados = await resposta.json();

    const logado = dados.logado;
    const servicos = dados.servicos;

    if (servicos.length === 0) {
        container.innerHTML = "<p class='placeholder-text'>Nenhum resultado encontrado.</p>";
        return;
    }

    container.innerHTML = "";

    servicos.forEach(item => {
        container.innerHTML += `
            <div class="result-item">
                <h3>${item.nome}</h3>
                <p class="location">${item.local}</p>
                <p class="description">${item.descricao}</p>
                <p><b> TELEFONE:</b> ${item.telefone} </p>
                <p>${item.link}</p>
               <a href="${item.link}" target="_blank">Acesse o site</a>
            </div>`
    });

})

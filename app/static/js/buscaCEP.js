document.getElementById("cep").addEventListener("keyup", async function (e) {
    const valor = e.target.value.replace(/\D/g, "");
    const logradouro = document.getElementById("log");
    const cidade = document.getElementById("cidade");
    const uf = document.getElementById("uf");

    logradouro.disabled = true;
    cidade.disabled = true;
    uf.disabled = true;

    if (valor.length !== 8) return;

    try {
        const resposta = await fetch(`https://viacep.com.br/ws/${valor}/json/`);
        if (resposta.ok) {
            const data = await resposta.json();
            if (data.erro) {
                logradouro.disabled = false;
                cidade.disabled = false;
                uf.disabled = false;
                alert("O CEP não foi encontrado. Por favor, digite-o manualmente.");
                return;
            }
            logradouro.value = data.logradouro;
            cidade.value = data.localidade;
            uf.value = data.uf;
        }
    } catch (ex) {
        console.error("Erro na busca do CEP:", ex);
        logradouro.disabled = false;
        cidade.disabled = false;
        uf.disabled = false;
    }
});

document.getElementById("cep").addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        event.preventDefault();
    }
});

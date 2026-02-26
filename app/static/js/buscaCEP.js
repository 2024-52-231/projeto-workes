    document.getElementById("cep").addEventListener("keyup", async function(e){
        const valor = e.target.value.replace(/\D/g, '');

        if (valor.length !== 8) return;

        try {
            const resposta = await fetch(`https://viacep.com.br/ws/${valor}/json/`);
            if (resposta.ok) {
                const data = await resposta.json();
                if (data.erro) {
                    alert("O CEP não foi encontrado");
                    return;
                }
                document.getElementById("log").value = data.logradouro;
                document.getElementById("cidade").value = data.localidade;
                document.getElementById("uf").value = data.uf;
            }
        } catch (ex) {
            console.error("Erro na busca do CEP:", ex);
        }
    });

    document.getElementById("cep").addEventListener("keydown", function(event) {
        if (event.key === "Enter") {
            event.preventDefault();
        }
    });
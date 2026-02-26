const cep = document.getElementById('cep');
const telefone = document.getElementById('telefone');
const mascaraTelefone = {
    mask: '(00) 00000-0000'
};
const mascaraCEP = {
    mask: '00000-000'
};
IMask(cep, mascaraCEP);
IMask(telefone, mascaraTelefone);
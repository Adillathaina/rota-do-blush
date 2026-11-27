const campoCep = document.getElementById("cep");
const statusCep = document.getElementById("cep-status");

function mascaraCep(valor) {
  const digitos = valor.replace(/\D/g, "").slice(0, 8);
  return digitos.length > 5 ? digitos.slice(0, 5) + "-" + digitos.slice(5) : digitos;
}

function mostrarStatus(texto, erro = false) {
  statusCep.textContent = texto;
  statusCep.classList.toggle("campo__ajuda--erro", erro);
}

function bloquearCep(texto) {
  mostrarStatus(texto, true);
  campoCep.setCustomValidity(texto);
}

function preencher(id, valor) {
  if (valor) document.getElementById(id).value = valor;
}

async function buscarCep(cep) {
  mostrarStatus("Buscando endereço…");
  try {
    const resposta = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
    if (!resposta.ok) throw new Error("ViaCEP indisponível");
    const dados = await resposta.json();

    if (dados.erro) return bloquearCep("CEP não encontrado. Confira os números.");
    if (dados.uf !== "TO") return bloquearCep("Atendemos apenas Araguaína e região (TO).");

    preencher("rua", dados.logradouro);
    preencher("bairro", dados.bairro);
    preencher("cidade", dados.localidade);
    mostrarStatus("Endereço encontrado. Confira e informe o número.");
    document.getElementById("numero").focus();
  } catch {
    mostrarStatus("Não foi possível buscar o CEP. Preencha o endereço à mão.", true);
  }
}

campoCep.addEventListener("input", () => {
  campoCep.value = mascaraCep(campoCep.value);
  campoCep.setCustomValidity("");
  const digitos = campoCep.value.replace(/\D/g, "");
  if (digitos.length === 8) buscarCep(digitos);
});
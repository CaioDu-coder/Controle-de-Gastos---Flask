// Confirmação antes de excluir um gasto
function confirmarRemocao(evento, descricao) {
    const confirmado = window.confirm(`Tem certeza que deseja excluir o gasto "${descricao}"?`);
    if (!confirmado) {
        evento.preventDefault();
    }
    return confirmado;
}

// Faz o valor sempre ficar com 2 casas decimais amigáveis ao sair do campo
document.addEventListener("DOMContentLoaded", () => {
    const campoValor = document.getElementById("valor");

    if (campoValor) {
        campoValor.addEventListener("blur", () => {
            const numero = parseFloat(campoValor.value.replace(",", "."));
            if (!isNaN(numero) && numero > 0) {
                campoValor.value = numero.toFixed(2);
            }
        });
    }

    // Some automaticamente com as mensagens de flash após alguns segundos
    const mensagensFlash = document.querySelectorAll(".flash");
    mensagensFlash.forEach((mensagem) => {
        setTimeout(() => {
            mensagem.style.transition = "opacity 0.5s ease";
            mensagem.style.opacity = "0";
            setTimeout(() => mensagem.remove(), 500);
        }, 4000);
    });
});

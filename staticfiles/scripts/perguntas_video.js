document.addEventListener('DOMContentLoaded', function() {
    const tipoPergunta = document.querySelector('[name="tipo_pergunta"]');
    const alternativasDiv = document.getElementById('alternativas');
    const verdadeiroFalsoDiv = document.getElementById('verdadeiro_falso');

    function updateForm() {
        const tipo = tipoPergunta.value;
        alternativasDiv.style.display = tipo === 'alternativas' ? 'block' : 'none';
        verdadeiroFalsoDiv.style.display = tipo === 'verdadeiro_falso' ? 'block' : 'none';
    }

    tipoPergunta.addEventListener('change', updateForm);
    updateForm();
});
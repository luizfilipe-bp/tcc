const formulario_resposta = document.getElementById('formulario_resposta');


form.addEventListener('submit', event => {
    event.preventDefault();


})


const avancar = async () => {
    const formData = new FormData();
    formData.append('resposta', formulario_resposta.resposta.value);

    const response = await fetch('./checar_resposta', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        },
        body: formData, 
        mode: 'same-origin',
    })

    return await response.json();
}
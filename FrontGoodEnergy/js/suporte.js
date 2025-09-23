// Aguarda o DOM ser completamente carregado antes de executar o código
document.addEventListener('DOMContentLoaded', () => {

    // Seleciona todos os botões que servem de "pergunta"
    const faqQuestions = document.querySelectorAll('.faq-question');

    // Itera sobre cada botão de pergunta
    faqQuestions.forEach(question => {

        // Adiciona um "ouvinte de evento" de clique a cada botão
        question.addEventListener('click', () => {

            // Encontra a div de resposta associada ao botão clicado
            const answer = question.nextElementSibling;

            // Verifica se a resposta está "colapsada" (com altura 0)
            if (answer.style.maxHeight === '0px' || answer.style.maxHeight === '') {
                // Se estiver colapsada, expande a resposta
                // O scrollHeight retorna a altura real do conteúdo
                answer.style.maxHeight = answer.scrollHeight + 'px';
                // Adiciona o atributo para acessibilidade e a animação do ícone
                question.setAttribute('aria-expanded', 'true');
            } else {
                // Se já estiver expandida, colapsa a resposta
                answer.style.maxHeight = '0px';
                // Remove o atributo de acessibilidade e reseta a animação do ícone
                question.setAttribute('aria-expanded', 'false');
            }
        });
    });
});
// ia-assistant.js

document.addEventListener('DOMContentLoaded', () => {
    const chatWidget = document.getElementById('chat-widget');
    const toggleChatBtns = document.querySelectorAll('.js-toggle-chat'); // Seleciona todos os botões que abrem o chat
    const chatInputText = document.getElementById('chat-input-text');
    const chatSendBtn = document.getElementById('chat-send-btn');
    const chatMicBtn = document.getElementById('chat-mic-btn');
    const chatMessagesContainer = document.getElementById('chat-messages');

    // --- Controle de Exibição do Widget de Chat ---
    // Função para mostrar o chat
    function showChatWidget() {
        chatWidget.classList.add('show');
        // Ativa a classe 'active' em todos os botões que ativam o chat
        toggleChatBtns.forEach(button => button.classList.add('active'));
    }

    // Função para esconder o chat
    function hideChatWidget() {
        chatWidget.classList.remove('show');
        // Remove a classe 'active' de todos os botões que ativam o chat
        toggleChatBtns.forEach(button => button.classList.remove('active'));
    }

    // Evento para todos os botões que ativam o chat
    toggleChatBtns.forEach(button => {
        button.addEventListener('click', (event) => {
            // Previne o comportamento padrão de scroll se o href for #chat-widget
            if (button.getAttribute('href') === '#chat-widget') {
                event.preventDefault(); // Evita a rolagem automática da página
            }

            if (chatWidget.classList.contains('show')) {
                hideChatWidget();
            } else {
                showChatWidget();
            }
        });
    });

    // --- Lógica do Chat ---

    // Simulação de Respostas da IA (Substitua por sua lógica real)
    const aiResponses = {
        "olá": "Olá! Como posso ajudar você hoje com seu Assistente de IA?",
        "oi": "Olá! Como posso ajudar você hoje com seu Assistente de IA?",
        "como funciona a otimização de consumo": "Nossa IA analisa seus padrões de uso para sugerir os melhores horários para usar aparelhos de alto consumo, maximizando sua economia.",
        "o que é otimização de consumo": "É um recurso que ajuda você a economizar na conta de luz, aproveitando melhor a energia gerada pelos seus painéis solares.",
        "suporte instalação": "Para suporte com instalação, por favor, entre em contato com nossa central de atendimento em [telefone/email] ou agende uma visita pelo link na seção 'Suporte e Manutenção'.",
        "manutenção": "Recomendamos a checagem anual do seu sistema. Você pode agendar sua manutenção através do seu portal do cliente ou pedindo aqui pelo chat.",
        "como conectar alexa": "Para conectar com a Alexa, abra o app Alexa, procure pela skill 'GoodEnergy IA' e siga as instruções de login.",
        "casa inteligente": "A função Casa Inteligente permite controlar luzes, termostato e outros dispositivos compatíveis por voz ou app. Você pode gerenciar suas conexões na seção 'Casa Inteligente' ou pedindo pelo chat.",
        "qualquer coisa": "Desculpe, não entendi. Poderia reformular sua pergunta?",
        // Adicione mais respostas aqui
    };

    // Função para adicionar mensagens ao chat
    function addMessage(message, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender);
        messageElement.textContent = message;
        chatMessagesContainer.appendChild(messageElement); 
        chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight; // Rola para a última mensagem
    }

    // Função para processar a mensagem do usuário
    function processUserInput(input) {
        const userInput = input.toLowerCase().trim();
        addMessage(input, 'user'); // Mostra a mensagem do usuário

        // Simula o tempo de resposta da IA
        setTimeout(() => {
            let response = aiResponses[userInput] || aiResponses["qualquer coisa"];
            addMessage(response, 'bot');
        }, 1000); // Espera 1 segundo para a resposta
    }

    // Evento de clique para enviar mensagem
    chatSendBtn.addEventListener('click', () => {
        const message = chatInputText.value;
        if (message.trim()) {
            processUserInput(message);
            chatInputText.value = ''; // Limpa o campo de input
        }
    });

    // Evento para enviar mensagem ao pressionar Enter
    chatInputText.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            chatSendBtn.click();
        }
    });

    // --- Funcionalidade de Microfone (Web Speech API) ---
    let listening = false;
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'pt-BR';
    recognition.continuous = false; // Para capturar uma frase por vez
    recognition.interimResults = true;

    recognition.onresult = (event) => {
        const transcript = Array.from(event.results)
            .map((result) => result[0].transcript)
            .join('');
        chatInputText.value = transcript;
    };

    recognition.onend = () => {
        listening = false;
        chatMicBtn.classList.remove('listening'); // Remove classe de estilo para indicar que parou de ouvir
    };

    recognition.onerror = (event) => {
        console.error('Erro no reconhecimento de voz:', event.error);
        listening = false;
        chatMicBtn.classList.remove('listening');
    };

    chatMicBtn.addEventListener('click', () => {
        if (!listening) {
            recognition.start();
            listening = true;
            chatMicBtn.classList.add('listening'); // Adiciona classe para indicar que está ouvindo
            chatInputText.value = ''; // Limpa campo enquanto ouve
        } else {
            recognition.stop();
        }
    });

    // Inicializa o chat com uma mensagem de boas-vindas
    addMessage("Olá! Sou seu Assistente de IA. Como posso te ajudar hoje?", 'bot');
});
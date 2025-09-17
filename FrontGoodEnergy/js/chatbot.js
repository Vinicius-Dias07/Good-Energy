// chatbot.js (ou ia-assistant.js) - CÓDIGO COMPLETO E CORRIGIDO

document.addEventListener('DOMContentLoaded', () => {
    // --- Elementos do Chat ---
    const chatWidget = document.getElementById('chat-widget');
    const chatInputText = document.getElementById('chat-input-text');
    const chatSendBtn = document.getElementById('chat-send-btn');
    const chatMicBtn = document.getElementById('chat-mic-btn');
    const chatMessagesContainer = document.getElementById('chat-messages');
    
    // --- Elementos do Histórico de Conversas ---
    const historyList = document.getElementById('history-list');
    const conversationHistoryContainer = document.getElementById('conversation-history'); // Usado para controle de visibilidade

    // --- Controle de Exibição do Widget de Chat ---
    // As funções showChatWidget e hideChatWidget foram removidas pois não parecem ser chamadas por nenhum botão.
    // Se você tiver botões específicos para abrir/fechar o chat, precisará implementá-los e chamá-los.
    // O chat widget é exibido por padrão pois a classe 'show' está no HTML.

    // --- Lógica do Chat ---

    // Simulação de Respostas da IA
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

    /**
     * Adiciona uma mensagem ao chat principal e garante que o scroll vá para o final.
     * @param {string} message - O texto da mensagem.
     * @param {'user' | 'bot'} sender - Quem enviou a mensagem ('user' ou 'bot').
     */
    function addMessage(message, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender);
        messageElement.textContent = message;
        
        chatMessagesContainer.appendChild(messageElement); 
        // Garante que o scroll vá para a última mensagem adicionada
        chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight; 
    }

    /**
     * Adiciona uma entrada ao histórico de conversas.
     * As mensagens mais recentes aparecem no topo.
     * @param {string} message - O texto da mensagem do usuário.
     */
    function addHistoryEntry(message) {
        const historyItem = document.createElement('li');
        // Trunca a mensagem se for muito longa para caber bem no histórico
        historyItem.textContent = message.length > 50 ? message.substring(0, 47) + '...' : message; 
        historyList.prepend(historyItem); // Adiciona no topo da lista de histórico
    }

    /**
     * Processa a entrada do usuário, a adiciona ao chat e ao histórico.
     * @param {string} input - O texto digitado pelo usuário.
     */
    function processUserInput(input) {
        const userInput = input.toLowerCase().trim();
        
        if (!userInput) return; // Não processa mensagens vazias

        addMessage(input, 'user'); // Adiciona a mensagem no chat principal
        addHistoryEntry(input);    // Adiciona a mensagem no histórico

        // Simula o tempo de resposta da IA
        setTimeout(() => {
            let response = aiResponses[userInput] || aiResponses["qualquer coisa"];
            addMessage(response, 'bot');
        }, 1000); // Espera 1 segundo para a resposta
    }

    // --- Event Listeners para o Chat ---

    // Enviar mensagem ao clicar no botão
    chatSendBtn.addEventListener('click', () => {
        const message = chatInputText.value;
        if (message.trim()) {
            processUserInput(message);
            chatInputText.value = ''; // Limpa o campo de input
        }
    });

    // Enviar mensagem ao pressionar Enter no campo de input
    chatInputText.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault(); // Previne o comportamento padrão do Enter (nova linha)
            chatSendBtn.click(); // Simula um clique no botão de enviar
        }
    });

    // --- Funcionalidade de Microfone (Web Speech API) ---
    let listening = false;
    // Garante que a API de reconhecimento de voz esteja disponível
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.lang = 'pt-BR';
        recognition.continuous = false; // Captura uma frase por vez
        recognition.interimResults = true; // Permite obter resultados parciais enquanto fala

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
                recognition.stop(); // Para a gravação se já estiver ouvindo
            }
        });
    } else {
        console.warn("A API de Reconhecimento de Voz não é suportada por este navegador.");
        // Opcionalmente, desabilitar ou esconder o botão do microfone se não for suportado
        chatMicBtn.style.display = 'none'; 
    }


    // --- Inicialização ---

    // Adiciona a mensagem de boas-vindas ao chat principal
    addMessage("Olá! Sou seu Assistente de IA. Como posso te ajudar hoje?", 'bot');

    // Lógica para mostrar/esconder o histórico em telas menores (opcional)
    function toggleHistoryVisibility() {
        // Se a largura da tela for menor ou igual a 768px (ajuste conforme necessário)
        if (window.innerWidth <= 768) {
            if (conversationHistoryContainer) conversationHistoryContainer.style.display = 'none';
        } else {
            // Restaura a exibição padrão para telas maiores (flex, pois o CSS define)
            if (conversationHistoryContainer) conversationHistoryContainer.style.display = 'flex'; 
        }
    }

    // Chama a função de visibilidade ao carregar a página e quando a janela muda de tamanho
    toggleHistoryVisibility();
    window.addEventListener('resize', toggleHistoryVisibility);
});
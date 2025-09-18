// chatbot.js (ou ia-assistant.js) - VERSÃO COM HISTÓRICO DE CONVERSAS

document.addEventListener('DOMContentLoaded', () => {
    // --- Elementos do Chat ---
    const chatInputText = document.getElementById('chat-input-text');
    const chatSendBtn = document.getElementById('chat-send-btn');
    const chatMicBtn = document.getElementById('chat-mic-btn');
    const chatMessagesContainer = document.getElementById('chat-messages');
    
    // --- Elementos do Histórico ---
    const historyList = document.getElementById('history-list');

    // --- Controle das Conversas ---
    let conversations = {}; // Armazena todas as conversas
    let currentConversation = null; // ID da conversa atual

    // --- Simulação de Respostas da IA ---
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
    };

    // --- Funções do Chat ---

    function addMessage(message, sender) {
        if (!currentConversation) return;

        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender);
        messageElement.textContent = message;
        chatMessagesContainer.appendChild(messageElement);

        // Guarda no histórico de mensagens dessa conversa
        conversations[currentConversation].messages.push({ sender, text: message });

        // Scroll automático
        chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
    }

    function startNewConversation(initialMessage) {
        const convId = Date.now().toString();
        conversations[convId] = { messages: [] };

        const historyItem = document.createElement('li');
        historyItem.textContent = initialMessage.length > 30 ? initialMessage.slice(0, 27) + "..." : initialMessage;
        historyItem.dataset.id = convId;

        historyItem.addEventListener('click', () => {
            loadConversation(convId);
        });

        historyList.prepend(historyItem);

        currentConversation = convId;
        chatMessagesContainer.innerHTML = ""; // Limpa tela
        addMessage("Nova conversa iniciada!", "bot");
    }

    function loadConversation(convId) {
        currentConversation = convId;
        chatMessagesContainer.innerHTML = "";
        conversations[convId].messages.forEach(msg => {
            addMessage(msg.text, msg.sender);
        });
    }

    function processUserInput(input) {
        const userInput = input.toLowerCase().trim();
        if (!userInput) return;

        if (!currentConversation) {
            startNewConversation(input);
        }

        addMessage(input, 'user');

        setTimeout(() => {
            let response = aiResponses[userInput] || aiResponses["qualquer coisa"];
            addMessage(response, 'bot');
        }, 800);
    }

    // --- Event Listeners ---
    chatSendBtn.addEventListener('click', () => {
        const message = chatInputText.value;
        if (message.trim()) {
            processUserInput(message);
            chatInputText.value = '';
        }
    });

    chatInputText.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            chatSendBtn.click();
        }
    });

    // --- Boas-vindas ---
    chatMessagesContainer.innerHTML = "";
    addMessage("👋 Olá! Clique em 'Nova conversa' ou envie uma mensagem para começar.", "bot");

    // --- Extra: botão para iniciar manualmente ---
    const newConversationBtn = document.createElement('button');
    newConversationBtn.textContent = "➕ Nova conversa";
    newConversationBtn.style.margin = "10px";
    newConversationBtn.addEventListener('click', () => {
        startNewConversation("Conversa em branco");
    });
    historyList.parentNode.insertBefore(newConversationBtn, historyList);
});


document.addEventListener('DOMContentLoaded', () => {
    const chatMessagesContainer = document.getElementById('chat-messages');
    const chatInputText = document.getElementById('chat-input-text');
    const chatSendBtn = document.getElementById('chat-send-btn');
    const historyList = document.getElementById('history-list');

    let conversations = JSON.parse(localStorage.getItem("conversations")) || {};
    let currentConversation = null;

    const aiResponses = {
        "olá": "Olá! Como posso ajudar você hoje com seu Assistente de IA?",
        "oi": "Olá! Como posso ajudar você hoje com seu Assistente de IA?",
        "como funciona a otimização de consumo": "Nossa IA analisa seus padrões de uso para sugerir os melhores horários para usar aparelhos de alto consumo, maximizando sua economia.",
        "o que é otimização de consumo": "É um recurso que ajuda você a economizar na conta de luz, aproveitando melhor a energia gerada pelos seus painéis solares.",
        "suporte instalação": "Para suporte com instalação, por favor, entre em contato com nossa central de atendimento em [telefone/email] ou agende uma visita pelo link na seção 'Suporte e Manutenção'.",
        "manutenção": "Recomendamos a checagem anual do seu sistema. Você pode agendar sua manutenção através do seu portal do cliente ou pedindo aqui pelo chat.",
        "como conectar alexa": "Para conectar com a Alexa, abra o app Alexa, procure pela skill 'GoodEnergy IA' e siga as instruções de login.",
        "casa inteligente": "A função Casa Inteligente permite controlar luzes, termostato e outros dispositivos compatíveis por voz ou app.",
        "qualquer coisa": "Desculpe, não entendi. Poderia reformular sua pergunta?",
    };

    // --- Salva no localStorage ---
    function saveConversations() {
        localStorage.setItem("conversations", JSON.stringify(conversations));
    }

    // --- Renderiza histórico ---
    function renderHistory() {
        historyList.innerHTML = "";
        Object.entries(conversations).reverse().forEach(([id, conv]) => {
            const historyItem = document.createElement("li");
            historyItem.textContent = conv.title;
            historyItem.dataset.id = id;
            historyItem.addEventListener("click", () => loadConversation(id));
            historyList.appendChild(historyItem);
        });
    }

    // --- Adiciona mensagem ---
    function addMessage(message, sender) {
        const msg = document.createElement("div");
        msg.classList.add("message", sender);
        msg.textContent = message;
        chatMessagesContainer.appendChild(msg);

        // salva mensagem na conversa
        if (currentConversation) {
            conversations[currentConversation].messages.push({ sender, text: message });
            saveConversations();
        }

        chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
    }

    // --- Nova conversa ---
    function startNewConversation(initialMessage = "Nova conversa") {
        const convId = Date.now().toString();
        conversations[convId] = { messages: [], title: initialMessage };
        currentConversation = convId;
        chatMessagesContainer.innerHTML = "";
        addMessage("Nova conversa iniciada!", "bot");
        saveConversations();
        renderHistory();
    }

    // --- Atualiza título apenas na primeira msg ---
    function updateConversationTitle(convId, newTitle) {
        if (conversations[convId].title === "Nova conversa") {
            conversations[convId].title = newTitle.length > 30 ? newTitle.slice(0, 27) + "..." : newTitle;
            saveConversations();
            renderHistory();
        }
    }

    // --- Carrega conversa ---
    function loadConversation(convId) {
        currentConversation = convId;
        chatMessagesContainer.innerHTML = "";
        conversations[convId].messages.forEach(msg => {
            addMessage(msg.text, msg.sender);
        });
    }

    // --- Processa input do usuário ---
    function processUserInput(input) {
        const userInput = input.toLowerCase().trim();
        if (!userInput) return;

        if (!currentConversation) {
            startNewConversation("Nova conversa");
        }

        addMessage(input, "user");

        if (conversations[currentConversation].messages.length === 2) { 
            updateConversationTitle(currentConversation, input);
        }

        setTimeout(() => {
            const response = aiResponses[userInput] || aiResponses["qualquer coisa"];
            addMessage(response, "bot");
        }, 800);
    }

    // --- Eventos ---
    chatSendBtn.addEventListener("click", () => {
        const msg = chatInputText.value;
        if (msg.trim()) {
            processUserInput(msg);
            chatInputText.value = "";
        }
    });

    chatInputText.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            chatSendBtn.click();
        }
    });

    // --- Inicialização ---
    renderHistory();
    if (Object.keys(conversations).length === 0) {
        startNewConversation("Nova conversa");
    }
});
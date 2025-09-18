// chatbot.js - CÓDIGO FINAL E CORRIGIDO
document.addEventListener('DOMContentLoaded', () => {
    // --- Elementos do Chat ---
    const chatInputText = document.getElementById('chat-input-text');
    const chatSendBtn = document.getElementById('chat-send-btn');
    const chatMicBtn = document.getElementById('chat-mic-btn');
    const chatMessagesContainer = document.getElementById('chat-messages');

    // --- Elementos do Histórico ---
    const historyList = document.getElementById('history-list');

    // --- Controle das Conversas ---
    let conversations = JSON.parse(localStorage.getItem("conversations")) || {};
    let currentConversationId = null;

    // --- Simulação de Respostas da IA ---
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

    // --- Funções Auxiliares ---

    /**
     * Salva todas as conversas no localStorage.
     */
    function saveConversations() {
        localStorage.setItem("conversations", JSON.stringify(conversations));
    }

    /**
     * Adiciona uma mensagem ao chat e a salva na conversa atual.
     */
    function addMessage(message, sender) {
        if (!currentConversationId || !conversations[currentConversationId]) {
            console.error('Nenhuma conversa ativa para adicionar a mensagem.');
            return;
        }

        const msgElement = document.createElement("div");
        msgElement.classList.add("message", sender);
        msgElement.textContent = message;
        chatMessagesContainer.appendChild(msgElement);
        
        conversations[currentConversationId].messages.push({ sender, text: message });
        saveConversations();
        
        // Se a mensagem for do usuário e for a primeira do array (índice 0)
        if (sender === 'user' && conversations[currentConversationId].messages.length === 1) {
            updateConversationTitle(currentConversationId, message);
        }

        chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
    }

    /**
     * Atualiza o título da conversa no histórico.
     */
    function updateConversationTitle(convId, newTitle) {
        const truncatedTitle = newTitle.length > 30 ? newTitle.slice(0, 27) + "..." : newTitle;
        conversations[convId].title = truncatedTitle;
        saveConversations();
        renderHistory();
    }
    
    /**
     * Inicia uma nova conversa.
     */
    function startNewConversation() {
        const convId = Date.now().toString();
        conversations[convId] = { messages: [], title: "Nova conversa" };
        currentConversationId = convId;

        chatMessagesContainer.innerHTML = "";
        
        // A primeira mensagem agora é adicionada após a primeira entrada do usuário
        saveConversations();
        renderHistory();
        
        // Ativa o novo item no histórico
        const newItem = document.querySelector(`li[data-id="${convId}"]`);
        if (newItem) {
             document.querySelectorAll('#history-list li').forEach(li => li.classList.remove('active'));
             newItem.classList.add('active');
        }
    }

    /**
     * Carrega uma conversa do histórico para o chat.
     */
    function loadConversation(convId) {
        currentConversationId = convId;
        chatMessagesContainer.innerHTML = "";
        
        const conversation = conversations[convId];
        if (conversation) {
            conversation.messages.forEach(msg => {
                const msgElement = document.createElement("div");
                msgElement.classList.add("message", msg.sender);
                msgElement.textContent = msg.text;
                chatMessagesContainer.appendChild(msgElement);
            });
            chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
        }

        // Ativa o item correto no histórico
        document.querySelectorAll('#history-list li').forEach(li => li.classList.remove('active'));
        document.querySelector(`li[data-id="${convId}"]`).classList.add('active');
    }
    
    /**
     * Renderiza a lista de conversas no histórico.
     */
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

    /**
     * Processa a entrada do usuário e aciona a resposta da IA.
     */
    function processUserInput(input) {
        const userInput = input.toLowerCase().trim();
        if (!userInput) return;
        
        addMessage(input, "user");

        setTimeout(() => {
            const response = aiResponses[userInput] || aiResponses["qualquer coisa"];
            addMessage(response, "bot");
        }, 800);
    }

    // --- Event Listeners ---
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

    // --- Event Listeners ---
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

// ADICIONE ESTE CÓDIGO AQUI
chatMicBtn.addEventListener('click', () => {
    chatMicBtn.classList.toggle('recording'); // Adiciona ou remove a classe 'recording'
    
    // Simulação: após 3 segundos, remove a classe para parar a "gravação"
    setTimeout(() => {
        chatMicBtn.classList.remove('recording');
    }, 3000);
});
    
    // Adiciona o botão de "Nova Conversa" ao histórico
    const newConversationBtn = document.createElement('button');
    newConversationBtn.textContent = "➕ Nova conversa";
    newConversationBtn.classList.add('new-conversation-btn');
    newConversationBtn.addEventListener('click', startNewConversation);
    const historyContainer = document.getElementById('conversation-history');
    const historyTitle = historyContainer.querySelector('h4');
    historyContainer.insertBefore(newConversationBtn, historyTitle.nextSibling);

    // --- Inicialização ---
    renderHistory();
    if (Object.keys(conversations).length > 0) {
        const latestConvId = Object.keys(conversations).sort((a, b) => b - a)[0];
        loadConversation(latestConvId);
    } else {
        startNewConversation();
    }
});
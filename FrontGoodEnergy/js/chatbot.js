document.addEventListener("DOMContentLoaded", function() {
  const chatMessagesContainer = document.getElementById("chat-messages");
  const chatInputText = document.getElementById("chat-input-text");
  const chatSendBtn = document.getElementById("chat-send-btn");
  const chatMicBtn = document.getElementById("chat-mic-btn");
  const historyList = document.getElementById("history-list");
  
  // Variáveis de estado
  let conversations = JSON.parse(localStorage.getItem('conversations')) || {};
  let currentConversationId = localStorage.getItem('currentConversationId');

  // NOVO: Botão de Excluir Conversa Atual
  const deleteCurrentBtn = document.createElement('button');
  deleteCurrentBtn.classList.add('delete-current-btn', 'hide'); 
  deleteCurrentBtn.innerHTML = `
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="3 6 5 6 21 6"></polyline>
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
      </svg>
      Excluir esta conversa
  `;
  
  const sidebarFoot = document.querySelector('.sidebar .foot');
  const sidebar = document.querySelector('.sidebar');
  sidebar.insertBefore(deleteCurrentBtn, sidebarFoot);
  
  deleteCurrentBtn.addEventListener('click', deleteCurrentConversation);

  // NOVO: Constante para a mensagem inicial do bot
  const WELCOME_MESSAGE = "Olá! Eu sou o Assistente IA da GoodEnergy. Como posso te ajudar a economizar energia hoje?";

  // --- Botão de Nova Conversa ---
  const newConversationBtn = document.createElement('button');
  newConversationBtn.textContent = "➕ Nova conversa";
  newConversationBtn.classList.add('new-conversation-btn');
  newConversationBtn.addEventListener('click', startNewConversation);

  const historyContainer = document.getElementById('conversation-history');
  const historyTitle = historyContainer.querySelector('h4');
  // Insere o botão de Nova Conversa logo após o título H4
  historyContainer.insertBefore(newConversationBtn, historyTitle.nextSibling);

  // --- Funções Auxiliares ---
  function saveConversations() {
    localStorage.setItem('conversations', JSON.stringify(conversations));
    if (currentConversationId) {
        localStorage.setItem('currentConversationId', currentConversationId);
    } else {
        localStorage.removeItem('currentConversationId');
    }
  }

  // NOVO: Função para controlar a visibilidade do botão de exclusão
  function checkDeleteButtonVisibility() {
      // Oculta o botão se houver 1 ou 0 conversas
      const convCount = Object.keys(conversations).length;
      if (convCount > 1 && currentConversationId) {
          deleteCurrentBtn.classList.remove('hide');
      } else {
          deleteCurrentBtn.classList.add('hide');
      }
  }
  
  // NOVO: Função para excluir a conversa ativa
  function deleteCurrentConversation() {
    if (!currentConversationId || !conversations[currentConversationId]) return;

    if (confirm("Tem certeza que deseja excluir esta conversa? Esta ação é irreversível.")) {
      const idToDelete = currentConversationId;
      delete conversations[idToDelete]; 
      saveConversations(); 

      // Inicia a conversa mais recente restante
      const remainingIds = Object.keys(conversations).sort((a, b) => b - a);
      if (remainingIds.length > 0) {
        loadConversation(remainingIds[0]);
      } else {
        startNewConversation();
      }
      
      renderHistory(); 
      checkDeleteButtonVisibility(); 
    }
  }
  
  // MODIFICADO: Agora inclui a mensagem de boas-vindas
  function startNewConversation() {
    const convId = Date.now().toString();
    
    // MUDANÇA PRINCIPAL: Inicializa a nova conversa com a mensagem de boas-vindas do bot
    const initialBotMessage = { sender: 'bot', text: WELCOME_MESSAGE };
    
    conversations[convId] = { 
        messages: [initialBotMessage], // Adiciona a mensagem inicial
        title: "Nova conversa" // Título inicial
    };
    
    currentConversationId = convId;
    chatMessagesContainer.innerHTML = "";

    saveConversations();
    renderHistory();
    
    // Chama loadConversation para garantir que o chatMessagesContainer seja preenchido 
    // com a nova conversa (e a mensagem de boas-vindas)
    loadConversation(convId); 

    // O restante do código de UI que você tinha no startNewConversation
  const newItem = document.querySelector(`li[data-id="${convId}"]`);
    if (newItem) {
      document.querySelectorAll('#history-list li').forEach(li => li.classList.remove('active'));
      newItem.classList.add('active');
    }
    
    // Atualiza a visibilidade do botão de exclusão
    checkDeleteButtonVisibility();
  }

  // MODIFICADO: Atualiza a visibilidade do botão de exclusão
  function loadConversation(convId) {
    currentConversationId = convId;
    chatMessagesContainer.innerHTML = "";

    const conversation = conversations[convId];
    if (conversation) {
      conversation.messages.forEach(msg => {
        const msgElement = document.createElement("div");
        msgElement.classList.add("message", msg.sender);
        
        if (msg.sender === "bot") {
            // marked.js precisa ser incluído no HTML para esta linha funcionar
            msgElement.innerHTML = marked.parse(msg.text); 
        } else {
            msgElement.textContent = msg.text;
        }
        
        chatMessagesContainer.appendChild(msgElement);
      });
      chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
    }

    document.querySelectorAll('#history-list li').forEach(li => li.classList.remove('active'));
    // Se não houver elemento (pode acontecer após exclusão e recarregamento), pula
    const activeItem = document.querySelector(`li[data-id="${convId}"]`);
    if (activeItem) {
        activeItem.classList.add('active');
    }
    
    // NOVO: Verifica se deve mostrar ou ocultar o botão ao carregar uma conversa
    checkDeleteButtonVisibility(); 
  }

  // CORRIGIDO: Agora usa o título salvo em conv.title
  function renderHistory() {
    historyList.innerHTML = "";
    Object.entries(conversations).reverse().forEach(([id, conv]) => {
      const historyItem = document.createElement("li");
      
      // CORREÇÃO: Usar a propriedade 'title' atualizada pela primeira mensagem do usuário.
      // Se não tiver sido atualizado, usa "Nova conversa" como fallback.
      const title = conv.title.length > 0 && conv.title !== "Nova conversa"
          ? conv.title
          : "Nova conversa";
          
      historyItem.textContent = title;
      historyItem.dataset.id = id;
      historyItem.addEventListener("click", () => loadConversation(id));
      historyList.appendChild(historyItem);
    });
    // NOVO: Atualiza a visibilidade após renderizar o histórico
    checkDeleteButtonVisibility(); 
  }
  
  // Função que simula o processamento da mensagem e resposta do bot
  function processUserInput(text) {
    if (!currentConversationId) {
        startNewConversation();
    }
    const conversation = conversations[currentConversationId];
    
    // 1. Adiciona a mensagem do usuário
    const userMessage = { sender: 'user', text: text };
    conversation.messages.push(userMessage);
    
    // Renderiza a mensagem do usuário
    const userMsgElement = document.createElement("div");
    userMsgElement.classList.add("message", "user");
    userMsgElement.textContent = text;
    chatMessagesContainer.appendChild(userMsgElement);

    // 2. Simulação de resposta do Bot
    // Em um ambiente real, esta seria a chamada à API do modelo de IA
  const botResponseText = `Entendido! Sua pergunta sobre "${text.substring(0, 15)}..." está sendo processada. Como Assistente IA, posso te oferecer dicas de economia ou monitoramento de consumo.`;
    const botMessage = { sender: 'bot', text: botResponseText };
    conversation.messages.push(botMessage);

    // Renderiza a mensagem do bot
    const botMsgElement = document.createElement("div");
    botMsgElement.classList.add("message", "bot");
    botMsgElement.innerHTML = marked.parse(botResponseText); // Assumindo marked.js para markdown
    chatMessagesContainer.appendChild(botMsgElement);
    
    // 3. Atualiza o título da conversa (se ainda for "Nova conversa")
    // Esta parte garante que a PRIMEIRA mensagem do usuário defina o título.
    if (conversation.title === "Nova conversa") {
        conversation.title = text.substring(0, 25) + (text.length > 25 ? '...' : '');
        renderHistory();
    }
    
    // 4. Salva e rola para baixo
    saveConversations();
    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
  }
  
  // --- Event Listeners ---
  chatSendBtn.addEventListener("click", function() {
    const text = chatInputText.value.trim();
    if (text) {
      processUserInput(text);
      chatInputText.value = "";
    }
  });

  chatInputText.addEventListener("keypress", function(e) {
    if (e.key === "Enter") {
      chatSendBtn.click();
    }
  });

  chatMicBtn.addEventListener("click", function() {
    alert("Função de entrada de voz não implementada.");
  });
  
  // --- Inicialização ---
  renderHistory();
  if (Object.keys(conversations).length > 0 && currentConversationId) {
    // Se há histórico e uma conversa ativa, carrega ela
    loadConversation(currentConversationId);
  } else if (Object.keys(conversations).length > 0) {
     // Se há histórico mas não há ativa, carrega a mais recente
    const latestConvId = Object.keys(conversations).sort((a, b) => b - a)[0];
    loadConversation(latestConvId);
  } else {
    // Se não há histórico, inicia uma nova (agora com a mensagem de boas-vindas)
    startNewConversation();
  }

  // NOVO: Verificação inicial
  checkDeleteButtonVisibility();
});
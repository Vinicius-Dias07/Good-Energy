document.addEventListener("DOMContentLoaded", function() {
  // ADICIONADO: Pega o usuário logado do localStorage para usar o email na chamada da API
  const user = JSON.parse(localStorage.getItem('ge_user'));

  const chatMessagesContainer = document.getElementById("chat-messages");
  const chatInputText = document.getElementById("chat-input-text");
  const chatSendBtn = document.getElementById("chat-send-btn");
  const chatMicBtn = document.getElementById("chat-mic-btn");
  const historyList = document.getElementById("history-list");
  
  // Variáveis de estado
  let conversations = JSON.parse(localStorage.getItem('conversations')) || {};
  let currentConversationId = localStorage.getItem('currentConversationId');

  // Botão de Excluir Conversa Atual
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

  // Constante para a mensagem inicial do bot
  const WELCOME_MESSAGE = "Olá! Eu sou o Assistente IA da GoodEnergy. Como posso te ajudar a economizar energia hoje?";

  // --- Botão de Nova Conversa ---
  const newConversationBtn = document.createElement('button');
  newConversationBtn.textContent = "➕ Nova conversa";
  newConversationBtn.classList.add('new-conversation-btn');
  newConversationBtn.addEventListener('click', startNewConversation);

  const historyContainer = document.getElementById('conversation-history');
  const historyTitle = historyContainer.querySelector('h4');
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

  function checkDeleteButtonVisibility() {
      const convCount = Object.keys(conversations).length;
      if (convCount > 1 && currentConversationId) {
          deleteCurrentBtn.classList.remove('hide');
      } else {
          deleteCurrentBtn.classList.add('hide');
      }
  }
  
  function deleteCurrentConversation() {
    if (!currentConversationId || !conversations[currentConversationId]) return;

    if (confirm("Tem certeza que deseja excluir esta conversa? Esta ação é irreversível.")) {
      const idToDelete = currentConversationId;
      delete conversations[idToDelete]; 
      saveConversations(); 

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
  
  function startNewConversation() {
    const convId = Date.now().toString();
    const initialBotMessage = { sender: 'bot', text: WELCOME_MESSAGE };
    
    conversations[convId] = { 
        messages: [initialBotMessage],
        title: "Nova conversa"
    };
    
    currentConversationId = convId;
    chatMessagesContainer.innerHTML = "";

    saveConversations();
    renderHistory();
    loadConversation(convId); 

    const newItem = document.querySelector(`li[data-id="${convId}"]`);
    if (newItem) {
      document.querySelectorAll('#history-list li').forEach(li => li.classList.remove('active'));
      newItem.classList.add('active');
    }
    
    checkDeleteButtonVisibility();
  }

  function loadConversation(convId) {
    currentConversationId = convId;
    chatMessagesContainer.innerHTML = "";

    const conversation = conversations[convId];
    if (conversation) {
      conversation.messages.forEach(msg => {
        const msgElement = document.createElement("div");
        msgElement.classList.add("message", msg.sender);
        
        if (msg.sender === "bot") {
            msgElement.innerHTML = marked.parse(msg.text); 
        } else {
            msgElement.textContent = msg.text;
        }
        
        chatMessagesContainer.appendChild(msgElement);
      });
      chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
    }

    document.querySelectorAll('#history-list li').forEach(li => li.classList.remove('active'));
    const activeItem = document.querySelector(`li[data-id="${convId}"]`);
    if (activeItem) {
        activeItem.classList.add('active');
    }
    
    checkDeleteButtonVisibility(); 
  }

  function renderHistory() {
    historyList.innerHTML = "";
    Object.entries(conversations).reverse().forEach(([id, conv]) => {
      const historyItem = document.createElement("li");
      const title = conv.title.length > 0 && conv.title !== "Nova conversa"
          ? conv.title
          : "Nova conversa";
          
      historyItem.textContent = title;
      historyItem.dataset.id = id;
      historyItem.addEventListener("click", () => loadConversation(id));
      historyList.appendChild(historyItem);
    });
    checkDeleteButtonVisibility(); 
  }
  
  // --- FUNÇÃO MODIFICADA PARA USAR A API ---
  async function processUserInput(text) {
    if (!currentConversationId) {
      startNewConversation();
    }
    // Garante que o usuário está logado para obter o email
    if (!user || !user.email) {
      alert("Erro: Usuário não identificado. Por favor, faça o login novamente.");
      return;
    }
  
    const conversation = conversations[currentConversationId];
  
    // 1. Adiciona e renderiza a mensagem do usuário
    const userMessage = { sender: 'user', text: text };
    conversation.messages.push(userMessage);
    const userMsgElement = document.createElement("div");
    userMsgElement.classList.add("message", "user");
    userMsgElement.textContent = text;
    chatMessagesContainer.appendChild(userMsgElement);
    chatInputText.value = ""; // Limpa o input
  
    // 2. Renderiza um indicador de "digitando..."
    const botTypingElement = document.createElement("div");
    botTypingElement.classList.add("message", "bot", "typing");
    botTypingElement.innerHTML = "<span></span><span></span><span></span>"; // Animação de "digitando"
    chatMessagesContainer.appendChild(botTypingElement);
    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
  
    try {
      // 3. Faz a chamada real à API do backend
      const response = await fetch('http://localhost:5000/api/ask-agent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: text,
          email: user.email // Envia o email do usuário logado
        }),
      });
  
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || 'Ocorreu um erro ao contatar o assistente.');
      }
  
      const botResponseText = data.answer; // Pega a resposta da API
  
      // 4. Salva e renderiza a resposta do bot
      const botMessage = { sender: 'bot', text: botResponseText };
      conversation.messages.push(botMessage);
  
      // Remove o indicador de "digitando"
      botTypingElement.remove();
  
      const botMsgElement = document.createElement("div");
      botMsgElement.classList.add("message", "bot");
      botMsgElement.innerHTML = marked.parse(botResponseText); // Usa a biblioteca marked para formatar
      chatMessagesContainer.appendChild(botMsgElement);
  
    } catch (error) {
      // Em caso de erro, exibe uma mensagem de falha
      botTypingElement.remove();
      const errorMsgElement = document.createElement("div");
      errorMsgElement.classList.add("message", "bot");
      errorMsgElement.textContent = `Desculpe, ocorreu um erro: ${error.message}`;
      chatMessagesContainer.appendChild(errorMsgElement);
    }
  
    // 5. Atualiza o título e salva o histórico
    if (conversation.title === "Nova conversa") {
      conversation.title = text.substring(0, 25) + (text.length > 25 ? '...' : '');
      renderHistory();
    }
  
    saveConversations();
    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
  }
  
  // --- Event Listeners (Sem alterações) ---
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
  
  // --- Inicialização (Sem alterações) ---
  renderHistory();
  if (Object.keys(conversations).length > 0 && currentConversationId) {
    loadConversation(currentConversationId);
  } else if (Object.keys(conversations).length > 0) {
    const latestConvId = Object.keys(conversations).sort((a, b) => b - a)[0];
    loadConversation(latestConvId);
  } else {
    startNewConversation();
  }

  checkDeleteButtonVisibility();
});
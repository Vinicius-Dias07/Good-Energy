document.addEventListener('DOMContentLoaded', () => {
  // --- Elementos do Chat ---
  // Constante para a mensagem inicial do bot
const WELCOME_MESSAGE = "Olá! Eu sou o Assistente IA da GoodEnergy. Como posso te ajudar a economizar energia hoje?";
  const chatInputText = document.getElementById('chat-input-text');
  const chatSendBtn = document.getElementById('chat-send-btn');
  const chatMicBtn = document.getElementById('chat-mic-btn');
  const chatMessagesContainer = document.getElementById('chat-messages');

  // --- Elementos do Histórico ---
  const historyList = document.getElementById('history-list');

  // --- Controle das Conversas (usando localStorage) ---
  let conversations = JSON.parse(localStorage.getItem("conversations")) || {};
  let currentConversationId = null;
  const user = JSON.parse(localStorage.getItem('ge_user'));

  // --- Funções Auxiliares ---
  function saveConversations() {
    localStorage.setItem("conversations", JSON.stringify(conversations));
  }

  function addMessage(message, sender) {
    if (!currentConversationId || !conversations[currentConversationId]) return;

    const msgElement = document.createElement("div");
    msgElement.classList.add("message", sender);
    msgElement.innerHTML = sender === "bot" ? marked.parse(message) : message;
    chatMessagesContainer.appendChild(msgElement);
    
    conversations[currentConversationId].messages.push({ sender, text: message });
    saveConversations();

    if (sender === 'user' && conversations[currentConversationId].messages.length === 1) {
      updateConversationTitle(currentConversationId, message);
    }
    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
  }

  function updateConversationTitle(convId, newTitle) {
    const truncatedTitle = newTitle.length > 30 ? newTitle.slice(0, 27) + "..." : newTitle;
    conversations[convId].title = truncatedTitle;
    saveConversations();
    renderHistory();
  }

  function startNewConversation() {
    const convId = Date.now().toString();
    conversations[convId] = { messages: [], title: "Nova conversa" };
    currentConversationId = convId;
    chatMessagesContainer.innerHTML = "";
<<<<<<< HEAD
=======

    addMessage(WELCOME_MESSAGE, "bot"); // Mensagem inicial do bot

>>>>>>> 6d3704fcbf40c9c6486269e0c09353939064cfcf
    saveConversations();
    renderHistory();
    document.querySelectorAll('#history-list li').forEach(li => li.classList.remove('active'));
    document.querySelector(`li[data-id="${convId}"]`)?.classList.add('active');
  }

  function loadConversation(convId) {
    currentConversationId = convId;
    chatMessagesContainer.innerHTML = "";
    const conversation = conversations[convId];
    if (conversation) {
      conversation.messages.forEach(msg => {
        const msgElement = document.createElement("div");
        msgElement.classList.add("message", msg.sender);
        msgElement.innerHTML = msg.sender === 'bot' ? marked.parse(msg.text) : msg.text;
        chatMessagesContainer.appendChild(msgElement);
      });
      chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
    }
    document.querySelectorAll('#history-list li').forEach(li => li.classList.remove('active'));
    document.querySelector(`li[data-id="${convId}"]`)?.classList.add('active');
  }

  function renderHistory() {
    if (!historyList) return;
    historyList.innerHTML = "";
    Object.entries(conversations).reverse().forEach(([id, conv]) => {
      const historyItem = document.createElement("li");
      historyItem.textContent = conv.title;
      historyItem.dataset.id = id;
      historyItem.addEventListener("click", () => loadConversation(id));
      if (id === currentConversationId) {
        historyItem.classList.add('active');
      }
      historyList.appendChild(historyItem);
    });
  }

  // --- Funções de Voz ---
  function stripMarkdown(text) { return text.replace(/(\*|_|`|~)/g, ''); }

  function speak(text) {
    if ('speechSynthesis' in window) {
      const cleanText = stripMarkdown(text);
      const utterance = new SpeechSynthesisUtterance(cleanText);
      utterance.lang = 'pt-BR';
      speechSynthesis.speak(utterance);
    }
  }

  // --- Processa Entrada do Usuário ---
  function processUserInput(input, voiceMode = false) {
    const userInput = input.trim();
    if (!userInput) return;

    if (!currentConversationId) {
        startNewConversation();
    }
    addMessage(userInput, "user");
    chatInputText.value = "";

    const typingMsg = document.createElement("div");
    typingMsg.classList.add("message", "bot");
    typingMsg.textContent = "🤖 Analisando...";
    chatMessagesContainer.appendChild(typingMsg);
    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;

    fetch("http://localhost:5000/api/ask-agent", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: userInput, email: user.email }),
    })
    .then(res => res.json())
    .then(data => {
        chatMessagesContainer.removeChild(typingMsg);
        if (data.answer) {
            addMessage(data.answer, "bot");
            if (voiceMode) speak(data.answer);
        } else {
            addMessage("❌ Erro: " + (data.error || "Não consegui responder."), "bot");
        }
    })
    .catch(err => {
        console.error(err);
        chatMessagesContainer.removeChild(typingMsg);
        addMessage("⚠️ Erro de conexão com o servidor.", "bot");
    });
  }

  // --- Event Listeners ---
  chatSendBtn.addEventListener("click", () => processUserInput(chatInputText.value, false));

  chatInputText.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
        e.preventDefault();
        processUserInput(chatInputText.value, false);
    }
  });
  
  let recognition;
  if ("webkitSpeechRecognition" in window) {
    recognition = new webkitSpeechRecognition();
    recognition.lang = 'pt-BR';
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      processUserInput(transcript, true);
    };
    recognition.onerror = (event) => console.error("Erro no reconhecimento de voz:", event.error);
  } else {
    chatMicBtn.style.display = 'none';
  }

  chatMicBtn.addEventListener("click", () => { 
    if (recognition) {
        try { recognition.start(); } catch (error) { console.error("Erro ao iniciar reconhecimento:", error); }
    }
  });
<<<<<<< HEAD
  
  // --- Inicialização ---
=======

// ... (continuação do seu código chatbot.js)

  // --- Botão de Nova Conversa ---
>>>>>>> 6d3704fcbf40c9c6486269e0c09353939064cfcf
  const newConversationBtn = document.createElement('button');
  newConversationBtn.textContent = "➕ Nova conversa";
  newConversationBtn.classList.add('new-conversation-btn');
  newConversationBtn.addEventListener('click', startNewConversation);
  const historyContainer = document.getElementById('conversation-history');
<<<<<<< HEAD
  if(historyContainer){
    const historyTitle = historyContainer.querySelector('h4');
    historyContainer.insertBefore(newConversationBtn, historyTitle.nextSibling);
  }

  if (!user) {
    chatInputText.disabled = true;
    chatInputText.placeholder = "Faça login para conversar.";
  } else {
    renderHistory();
    const convIds = Object.keys(conversations);
    if (convIds.length > 0) {
      const latestConvId = convIds.sort((a, b) => b - a)[0];
      loadConversation(latestConvId);
    } else {
      startNewConversation();
    }
  }
});
=======
  const historyTitle = historyContainer.querySelector('h4');
  // Insere o botão de Nova Conversa logo após o título H4
  historyContainer.insertBefore(newConversationBtn, historyTitle.nextSibling);

// NOVO: -----------------------------------------------------

  // --- Botão de Excluir Conversa Atual ---
  const deleteCurrentBtn = document.createElement('button');
  deleteCurrentBtn.classList.add('delete-current-btn', 'hide'); // Começa oculto
  deleteCurrentBtn.innerHTML = `
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="3 6 5 6 21 6"></polyline>
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
      </svg>
      Excluir esta conversa
  `;
  
  // Insere o botão NO FINAL da sidebar, acima do foot ("Olá, Usuário")
  const sidebarFoot = document.querySelector('.sidebar .foot');
  const sidebar = document.querySelector('.sidebar');
  sidebar.insertBefore(deleteCurrentBtn, sidebarFoot);
  
  deleteCurrentBtn.addEventListener('click', deleteCurrentConversation);
  
  // --- Funções de Controle de Visibilidade e Exclusão (NOVAS) ---
  
  function checkDeleteButtonVisibility() {
      // Oculta o botão se houver 1 ou 0 conversas
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
      delete conversations[idToDelete]; // Remove a conversa do objeto
      saveConversations(); // Salva no localStorage

      // Inicia a conversa mais recente restante
      const remainingIds = Object.keys(conversations).sort((a, b) => b - a);
      if (remainingIds.length > 0) {
        loadConversation(remainingIds[0]);
      } else {
        startNewConversation();
      }
      
      renderHistory(); // Atualiza a exibição do histórico
      checkDeleteButtonVisibility(); // Verifica se o botão deve ser ocultado
    }
  }
  
  // --- Funções Existentes (Atualize a chamada da nova função) ---
  
  function startNewConversation() {
    const convId = Date.now().toString();
    conversations[convId] = { messages: [], title: "Nova conversa" };
    currentConversationId = convId;
    chatMessagesContainer.innerHTML = "";

    saveConversations();
    renderHistory();

    const newItem = document.querySelector(`li[data-id="${convId}"]`);
    if (newItem) {
      document.querySelectorAll('#history-list li').forEach(li => li.classList.remove('active'));
      newItem.classList.add('active');
    }
    
    // NOVO: Atualiza a visibilidade do botão após iniciar uma nova
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
document.querySelector(`li[data-id="${convId}"]`).classList.add('active');
    
    // NOVO: Atualiza a visibilidade do botão ao carregar uma conversa
    checkDeleteButtonVisibility();
  }

  function renderHistory() {
    historyList.innerHTML = "";
    Object.entries(conversations).reverse().forEach(([id, conv]) => {
      const historyItem = document.createElement("li");
      historyItem.textContent = conv.title;
      historyItem.dataset.id = id;
      historyItem.addEventListener("click", () => loadConversation(id));
      historyList.appendChild(historyItem);
    });
    // NOVO: Atualiza a visibilidade após renderizar o histórico (em caso de exclusão, por exemplo)
    checkDeleteButtonVisibility(); 
  }
  
  // ... (funções processUserInput, speak, etc.)

// --- Event Listeners ---
// ... (chatSendBtn, chatInputText, chatMicBtn)

// --- Inicialização ---
  renderHistory();
  if (Object.keys(conversations).length > 0) {
    const latestConvId = Object.keys(conversations).sort((a, b) => b - a)[0];
    loadConversation(latestConvId);
  } else {
    startNewConversation();
  }

  // NOVO: Verificação inicial ao carregar
  checkDeleteButtonVisibility();
});
  
>>>>>>> 6d3704fcbf40c9c6486269e0c09353939064cfcf

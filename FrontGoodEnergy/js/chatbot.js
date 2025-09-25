document.addEventListener('DOMContentLoaded', () => {
  // --- Elementos do Chat ---
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
    
    addMessage(WELCOME_MESSAGE, "bot");

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
    if(chatMicBtn) chatMicBtn.style.display = 'none';
  }

  if(chatMicBtn) {
    chatMicBtn.addEventListener("click", () => { 
        if (recognition) {
            try { recognition.start(); } catch (error) { console.error("Erro ao iniciar reconhecimento:", error); }
        }
    });
  }
  
  // --- Inicialização ---
  const newConversationBtn = document.createElement('button');
  newConversationBtn.textContent = "➕ Nova conversa";
  newConversationBtn.classList.add('new-conversation-btn');
  newConversationBtn.addEventListener('click', startNewConversation);
  const historyContainer = document.getElementById('conversation-history');
  
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
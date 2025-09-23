// chatbot.js - COM SUPORTE A VOZ
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

  // --- Funções Auxiliares ---
  function saveConversations() {
    localStorage.setItem("conversations", JSON.stringify(conversations));
  }

  function addMessage(message, sender) {
    if (!currentConversationId || !conversations[currentConversationId]) {
      console.error('Nenhuma conversa ativa para adicionar a mensagem.');
      return;
    }

    const msgElement = document.createElement("div");
    msgElement.classList.add("message", sender);

    if (sender === "bot") {
      msgElement.innerHTML = marked.parse(message); // renderiza Markdown no chat
    } else {
      msgElement.textContent = message;
    }

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

    saveConversations();
    renderHistory();

    const newItem = document.querySelector(`li[data-id="${convId}"]`);
    if (newItem) {
      document.querySelectorAll('#history-list li').forEach(li => li.classList.remove('active'));
      newItem.classList.add('active');
    }
  }

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

    document.querySelectorAll('#history-list li').forEach(li => li.classList.remove('active'));
    document.querySelector(`li[data-id="${convId}"]`).classList.add('active');
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
  }

  // --- Funções de Voz ---
  function stripMarkdown(text) {
    return text
      .replace(/\*\*/g, '')       // remove **
      .replace(/#+\s?/g, '')      // remove ## títulos
      .replace(/[*•-]\s?/g, '')   // remove bullets
      .replace(/_/g, '')          // remove _
      .replace(/\n+/g, '. ');     // troca \n por pausa
  }

  function speak(text) {
    const synth = window.speechSynthesis;
    const cleanText = stripMarkdown(text);
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = "pt-BR";
    utterance.rate = 1.1; // um pouco mais rápido = menos robótico
    synth.speak(utterance);
  }

  // --- Processa Entrada ---
  function processUserInput(input, voiceMode = false) {
    const userInput = input.trim();
    if (!userInput) return;

    addMessage(userInput, "user");

    const typingMsg = document.createElement("div");
    typingMsg.classList.add("message", "bot");
    typingMsg.textContent = "🤖 Digitando...";
    chatMessagesContainer.appendChild(typingMsg);

    fetch("http://localhost:5000/api/ask-agent", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: userInput }),
    })
      .then(res => res.json())
      .then(data => {
        chatMessagesContainer.removeChild(typingMsg);

        if (data.answer) {
          addMessage(data.answer, "bot");

          if (voiceMode) {
            speak(data.answer); // só fala se veio do mic
          }
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
  chatSendBtn.addEventListener("click", () => {
    const msg = chatInputText.value;
    if (msg.trim()) {
      processUserInput(msg, false); // texto → não fala
      chatInputText.value = "";
    }
  });

  chatInputText.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      chatSendBtn.click();
    }
  });

  // --- Reconhecimento de Voz ---
  let recognition;

  if ("webkitSpeechRecognition" in window) {
    recognition = new webkitSpeechRecognition();
    recognition.lang = "pt-BR";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      chatInputText.value = transcript;
      processUserInput(transcript, true); // voz → fala
    };
  }

  chatMicBtn.addEventListener("click", () => {
    if (recognition) recognition.start();
  });

  // --- Botão de Nova Conversa ---
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

// app.js - Versão COMPLETA E ESTÁVEL com todas as funções e correções

async function fetchWeather() {
    const apiKey = '288e9288c597f70a80a921fd488da25a'; 
    const lat = -23.5614;
    const lon = -46.6565;
    const apiUrl = `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&appid=${apiKey}&units=metric&lang=pt_br`;

    try {
        const response = await fetch(apiUrl);
        if (!response.ok) {
            throw new Error('Não foi possível obter a previsão do tempo.');
        }
        const data = await response.json();

        // --- Seleciona os elementos ANTIGOS ---
        const iconEl = el('weather-icon');
        const tempEl = el('weather-temp');
        const descEl = el('weather-desc');
        const locationEl = el('weather-location-name');

        // --- Seleciona os NOVOS elementos ---
        const humidityEl = el('weather-humidity');
        const windEl = el('weather-wind');
        const cloudsEl = el('weather-clouds');

        // --- Preenche TODOS os elementos com os dados da API ---
        
        // Dados principais
        iconEl.src = `https://openweathermap.org/img/wn/${data.weather[0].icon}@2x.png`;
        tempEl.textContent = `${Math.round(data.main.temp)}°C`;
        descEl.textContent = data.weather[0].description;
        locationEl.textContent = data.name;

        // Novos detalhes
        humidityEl.textContent = `${data.main.humidity} %`;
        // O vento vem em m/s, convertemos para km/h (multiplicando por 3.6)
        windEl.textContent = `${Math.round(data.wind.speed * 3.6)} km/h`;
        cloudsEl.textContent = `${data.clouds.all} %`;

    } catch (error) {
        console.error("Erro ao buscar dados do clima:", error);
        el('weather-desc').textContent = "Erro ao carregar dados.";
    }
}

const user = JSON.parse(localStorage.getItem('ge_user'));

if (!user && !['login', 'register', 'index', undefined].includes(document.body.dataset.active)) {
    window.location.href = 'login.html';
}

const el = id => document.getElementById(id);
const showLoader = () => el('loader-overlay')?.classList.remove('hide');
const hideLoader = () => el('loader-overlay')?.classList.add('hide');

function showToast(message, type = 'success') {
    const container = el('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4000); 
}

// --- FUNÇÕES DE TEMA (COM CORREÇÃO DE "PISCA-PISCA") ---
async function saveThemePreference(theme, colorTheme) {
    if (!user) return;
    try {
        const payload = { email: user.email };
        const updatedUser = { ...JSON.parse(localStorage.getItem('ge_user')) };

        if (theme !== undefined) {
            payload.theme = theme;
            updatedUser.theme = theme;
        }
        if (colorTheme !== undefined) {
            payload.colorTheme = colorTheme;
            updatedUser.colorTheme = colorTheme;
        }
        
        localStorage.setItem('ge_user', JSON.stringify(updatedUser));
        
        await fetch('http://127.0.0.1:5000/api/user/theme', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
    } catch (error) {
        console.error("Não foi possível salvar a preferência de tema:", error);
    }
}
function applyColorTheme(colorTheme) {
  document.body.dataset.colortheme = colorTheme;
  const switcher = el('colorThemeSwitcher');
  if (switcher) { switcher.querySelectorAll('button').forEach(btn => btn.classList.toggle('active', btn.dataset.colortheme === colorTheme)); }
}
function applyTheme(theme) {
  document.body.dataset.theme = theme;
  const switcher = el('themeSwitcher');
  if (switcher) { switcher.querySelectorAll('button').forEach(btn => btn.classList.toggle('active', btn.dataset.theme === theme)); }
}
function loadThemes() {
    const currentUser = JSON.parse(localStorage.getItem('ge_user'));
    const savedColorTheme = currentUser?.colorTheme || 'dark';
    const savedTheme = currentUser?.theme || 'padrão';
    applyColorTheme(savedColorTheme);
    applyTheme(savedTheme);
}

// --- MONTAGEM DA INTERFACE ---
function mountSidebar(active='dashboard'){
  const nav = document.querySelector('.nav');
  if(!nav) return;
  const icons = {
    dashboard: `<svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>`,
    devices: `<svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M5 12h14M12 5l7 7-7 7"></path></svg>`,
    reports: `<svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V7a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>`,
    user: `<svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>`,
    help: `<svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`,
    settings: `<svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>`,
    logout: `<svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path></svg>`
  };
  const navItems = [
    ['dashboard.html','dashboard','Dashboard'], ['devices.html','devices','Dispositivos'], ['reports.html','reports','Relatórios'],
    ['user.html','user','Usuário'], ['help.html','help','Ajuda & FAQ'], ['settings.html','settings','Configurações'],
  ];
  nav.innerHTML = navItems.map(([href, id, label]) => `<a href="${href}" class="${active === id ? 'active' : ''}" title="${label}">${icons[id] || ''}<span>${label}</span></a>`).join('');
  const logoutButton = document.createElement('a');
  logoutButton.href = "#"; logoutButton.id = "logoutBtn"; logoutButton.title = "Sair";
  logoutButton.innerHTML = `${icons.logout}<span>Sair</span>`;
  nav.appendChild(logoutButton);
  logoutButton.addEventListener('click', (e) => { e.preventDefault(); localStorage.clear(); window.location.href = 'index.html'; });
  if (user) el('userName').textContent = user.name.split(' ')[0];
}

function initializeTopbarButtons() {
    const notifBtn = el('notificationsBtn'), notifPopup = el('notificationsPopup');
    if (notifBtn && notifPopup) {
        const alertsContainer = el('popupAlerts');
        const badge = el('notificationBadge');
        const sampleAlerts = [
            {type:'warn', text:'Nuvens densas — geração pode cair 22%'},
            {type:'success', text:'Horário ideal para carregar o carro elétrico'},
            {type:'info', text:'Bateria com carga total em 45 minutos.'},
        ];
        if (alertsContainer) {
            alertsContainer.innerHTML = sampleAlerts.map(a => `
                <div class="row">
                    <span class="tag ${a.type}">${a.type === 'warn' ? 'Atenção' : a.type === 'success' ? 'Dica' : 'Info'}</span>
                    <div>${a.text}</div>
                </div>
            `).join('');
        }
        if(badge) {
            if (sampleAlerts.length > 0) { badge.textContent = sampleAlerts.length; badge.classList.remove('hide'); } 
            else { badge.classList.add('hide'); }
        }
        notifBtn.addEventListener('click', (e) => { e.stopPropagation(); notifPopup.classList.toggle('hide'); if(badge) badge.classList.add('hide'); });
        document.addEventListener('click', () => notifPopup.classList.add('hide'));
        notifPopup.addEventListener('click', e => e.stopPropagation());
    }
    const zenBtn = el('zenModeBtn'), zenOverlay = el('zenModeOverlay');
    if (zenBtn && zenOverlay) {
        zenBtn.addEventListener('click', () => zenOverlay.classList.remove('hide'));
        zenOverlay.addEventListener('click', () => zenOverlay.classList.add('hide'));
    }
}

// --- FUNÇÕES ESPECÍFICAS DE CADA PÁGINA ---
function loginInit() {
  const form = el('loginForm');
  if (!form) return;
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const emailInput = form.querySelector('[name=email]');
    const passInput = form.querySelector('[name=pass]');
    if (!emailInput.value || !passInput.value) { showToast('Por favor, preencha e-mail e senha.', 'error'); return; }
    showLoader();
    try {
      const response = await fetch('http://127.0.0.1:5000/api/login', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: emailInput.value, password: passInput.value }),
      });
      const result = await response.json();
      hideLoader();
      if (!response.ok) { throw new Error(result.error || 'Falha na autenticação.'); }
      localStorage.setItem('ge_user', JSON.stringify(result));
      showToast(`Bem-vindo de volta, ${result.name}!`, 'success');
      setTimeout(() => window.location.href = 'dashboard.html', 500);
    } catch (error) { hideLoader(); showToast(error.message, 'error'); }
  });
}

function registerInit() {
  const form = el('registerForm');
  if (!form) return;
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const nameInput = form.querySelector('[name=name]');
    const emailInput = form.querySelector('[name=email]');
    const passInput = form.querySelector('[name=pass]');
    if (!nameInput.value || !emailInput.value || !passInput.value) { showToast('Por favor, preencha todos os campos.', 'error'); return; }
    showLoader();
    try {
      const response = await fetch('http://127.0.0.1:5000/api/register', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: nameInput.value, email: emailInput.value, password: passInput.value }),
      });
      const result = await response.json();
      hideLoader();
      if (!response.ok) { throw new Error(result.error || 'Não foi possível criar a conta.'); }

      // --- A MÁGICA ACONTECE AQUI ---

      // 1. Salva o usuário no localStorage, realizando o "login"
      localStorage.setItem('ge_user', JSON.stringify(result));

      // 2. Mostra uma mensagem mais clara para o usuário
      showToast(`Cadastro realizado, ${result.name}! Redirecionando para o dashboard...`, 'success');

      // 3. Redireciona para o dashboard após um breve intervalo
      setTimeout(() => {
          window.location.href = 'dashboard.html';
      }, 1500); // Aumentamos para 1.5s para dar tempo de ler a mensagem

    } catch (error) { 
        hideLoader(); 
        showToast(error.message, 'error'); 
    }
  });
}

async function dashboardInit() {
    showLoader();
    fetchWeather();
    fetchBatteryData(); 
    try {
        const [kpisResponse, chartResponse] = await Promise.all([
            fetch(`http://127.0.0.1:5000/api/kpis?email=${user.email}`),
            fetch('http://127.0.0.1:5000/api/generation/history')
        ]);
        if (!kpisResponse.ok || !chartResponse.ok) { throw new Error('Falha ao buscar dados do dashboard do servidor.'); }
        const kpisData = await kpisResponse.json();
        const chartData = await chartResponse.json();

        const tariff = 0.95; 
        const todayGen = kpisData?.todayGenKwh ?? 0;
        const houseLoad = kpisData?.houseLoadKw ?? 0;
        
        el('kpiGen').textContent = `${todayGen.toFixed(1)} kWh`;
        el('kpiUse').textContent = `${houseLoad.toFixed(2)} kW`;
        el('kpiSaving').textContent = `R$ ${(todayGen * tariff).toFixed(2)}`;
        
        if (typeof Chart === 'undefined') { return console.error('A biblioteca Chart.js não foi carregada.'); }
        
        const simulatedConsumptionHistory = chartData.generation_kw.map(g => Math.max(0.2, g * (0.6 + Math.random() * 0.3))).map(v => +v.toFixed(2));
        Chart.defaults.color = document.body.dataset.colortheme === 'light' ? '#374151' : '#cdd7ee';
        Chart.defaults.borderColor = 'rgba(100,100,100,0.1)';
        const energyCtx = el('chartEnergy');
        if (energyCtx) {
            new Chart(energyCtx, {
                type: 'line', data: { labels: chartData.labels,
                    datasets: [
                        { label: 'Geração (kW)', data: chartData.generation_kw, fill: true, tension: 0.35, backgroundColor: 'rgba(0, 255, 0, 0.1)', borderColor: 'rgba(0, 255, 0)' },
                        { label: 'Consumo (kW)', data: simulatedConsumptionHistory, fill: true, tension: 0.35, backgroundColor: 'rgba(255, 0, 0, 0.1)', borderColor: 'rgba(255, 0, 0)' }
                    ]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }
    } catch (error) { 
        console.error("Erro detalhado no dashboardInit:", error);
        showToast(error.message, 'error'); 
    } finally { 
        hideLoader(); 
    }
}

async function devicesInit() {
    const tbody = el('deviceTable')?.querySelector('tbody');
    const modal = el('addDeviceModal');
    const addBtn = el('addDeviceBtn');
    const closeBtn = el('closeModalBtn');
    const form = el('addDeviceForm');
    if (!tbody || !modal || !addBtn || !closeBtn || !form) return;

    const render = (devices) => {
        tbody.innerHTML = devices.map(d => `
            <tr>
                <td>${d.name}<br><span class="tag" style="opacity:0.7">${d.room}</span></td>
                <td><span class="tag">${d.type}</span></td>
                <td>${d.on ? `<span class="tag success">Ligado</span>` : `<span class="tag fail">Desligado</span>`}</td>
                <td>${d.watts} W</td>
                <td class="right device-actions">
                    <button class="icon-btn" data-action="toggle" data-id="${d.id}" data-state="${d.on}">${d.on ? 'Desligar' : 'Ligar'}</button>
                    <button class="icon-btn" data-action="delete" data-id="${d.id}">Excluir</button>
                </td>
            </tr>
        `).join('');
    };

    const fetchAndRender = async () => {
        showLoader();
        try {
            const response = await fetch(`http://127.0.0.1:5000/api/devices?email=${user.email}`);
            if (!response.ok) throw new Error('Não foi possível carregar os dispositivos.');
            const devices = await response.json();
            render(devices);
        } catch (error) { showToast(error.message, 'error'); } finally { hideLoader(); }
    };
    
    tbody.addEventListener('click', async (e) => {
        const button = e.target.closest('button');
        if (!button) return;
        const action = button.dataset.action;
        const id = button.dataset.id;
        if (action === 'toggle') {
            const currentState = button.dataset.state === 'true';
            try {
                await fetch(`http://127.0.0.1:5000/api/devices/${id}`, {
                    method: 'PUT', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: user.email, on: !currentState })
                });
                fetchAndRender();
            } catch (error) { showToast('Erro ao atualizar dispositivo.', 'error'); }
        }
        if (action === 'delete') {
            if (confirm('Tem certeza que deseja excluir este dispositivo?')) {
                try {
                    await fetch(`http://127.0.0.1:5000/api/devices/${id}?email=${user.email}`, { method: 'DELETE' });
                    fetchAndRender();
                } catch (error) { showToast('Erro ao excluir dispositivo.', 'error'); }
            }
        }
    });

    addBtn.addEventListener('click', () => modal.classList.remove('hide'));
    closeBtn.addEventListener('click', () => modal.classList.add('hide'));
    modal.addEventListener('click', (e) => { if (e.target === modal) modal.classList.add('hide'); });
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const newDevice = {
            email: user.email,
            name: form.querySelector('[name=name]').value,
            room: form.querySelector('[name=room]').value,
            type: form.querySelector('[name=type]').value,
        };
        try {
            const response = await fetch('http://127.0.0.1:5000/api/devices', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newDevice)
            });
            if (!response.ok) throw new Error('Não foi possível adicionar o dispositivo.');
            form.reset();
            modal.classList.add('hide');
            fetchAndRender();
        } catch (error) { showToast(error.message, 'error'); }
    });
    fetchAndRender();
}

function reportsInit() {
    let reportChartInstance;
    const generateReportChart = async () => {
        if (typeof Chart === 'undefined') { console.error('A biblioteca Chart.js não foi carregada.'); return; }
        showLoader();
        try {
            const response = await fetch('http://127.0.0.1:5000/api/reports/monthly');
            if (!response.ok) throw new Error("Não foi possível carregar os dados do relatório.");
            const reportData = await response.json();
            const labels = reportData.map(item => item.date);
            const data = reportData.map(item => item.generation);
            const ctx = el('reportChart');
            if(!ctx) return;
            if (reportChartInstance) reportChartInstance.destroy();
            reportChartInstance = new Chart(ctx, {
                type: 'bar', data: { labels: labels,
                    datasets: [{
                        label: 'Geração Mensal (kWh)', data: data,
                        backgroundColor: 'rgba(59, 130, 246, 0.5)', borderColor: '#3b82f6'
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        } catch (error) { showToast(error.message, 'error'); } finally { hideLoader(); }
    };
    generateReportChart();
}

function settingsInit() {
    const themeSwitcher = el('themeSwitcher');
    if (themeSwitcher) {
        themeSwitcher.addEventListener('click', (e) => {
            const button = e.target.closest('button');
            if (button) {
                const theme = button.dataset.theme;
                applyTheme(theme);
                saveThemePreference(theme, undefined);
            }
        });
    }
    const colorThemeSwitcher = el('colorThemeSwitcher');
    if (colorThemeSwitcher) {
      colorThemeSwitcher.addEventListener('click', (e) => {
        const button = e.target.closest('button');
        if (button) {
          const colorTheme = button.dataset.colortheme;
          applyColorTheme(colorTheme);
          saveThemePreference(undefined, colorTheme);
        }
      });
    }
}

// SUBSTITUA a função 'populateUser' por esta nova função 'userPageInit'

function userPageInit() {
    // Parte 1: Preencher os dados do formulário do usuário (lógica que já existia)
    if (!user) return;
    const uName = el('uName'), uEmail = el('uEmail'), planTag = el('planTag');
    if (uName) uName.value = user.name;
    if (uEmail) uEmail.value = user.email;
    if (planTag) planTag.textContent = user.plan;

    // Parte 2: Lógica para a exclusão da conta
    const deleteBtn = el('deleteAccountBtn');
    const confirmBox = el('deleteConfirmBox');
    const cancelBtn = el('deleteCancelBtn');
    const confirmBtn = el('deleteConfirmBtn');
    const passwordInput = el('deletePasswordInput');
    const errorMsg = el('deleteErrorMsg');
    
    // Verifica se todos os elementos existem antes de adicionar os eventos
    if (!deleteBtn || !confirmBox || !cancelBtn || !confirmBtn || !passwordInput || !errorMsg) {
        return; 
    }

    // Evento para mostrar a caixa de confirmação
    deleteBtn.addEventListener('click', () => {
        deleteBtn.classList.add('hide');
        confirmBox.classList.remove('hide');
    });

    // Evento para cancelar e esconder a caixa
    cancelBtn.addEventListener('click', () => {
        confirmBox.classList.add('hide');
        deleteBtn.classList.remove('hide');
        passwordInput.value = '';
        errorMsg.classList.add('hide');
    });

    // Evento para confirmar e executar a exclusão
    confirmBtn.addEventListener('click', async () => {
        const password = passwordInput.value;
        if (!password) {
            errorMsg.textContent = "Por favor, digite sua senha para confirmar.";
            errorMsg.classList.remove('hide');
            return;
        }

        errorMsg.classList.add('hide');
        confirmBtn.disabled = true;
        confirmBtn.textContent = 'Excluindo...';
        showLoader();

        try {
            const response = await fetch('http://127.0.0.1:5000/api/user', {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email: user.email,
                    password: password
                })
            });

            const result = await response.json();
            if (!response.ok) {
                throw new Error(result.error || 'Não foi possível excluir a conta.');
            }

            localStorage.clear(); // Limpa todos os dados do usuário
            showToast('Sua conta foi removida com sucesso.', 'success');
            setTimeout(() => { window.location.href = 'login.html'; }, 1500);

        } catch (err) {
            hideLoader();
            showToast(err.message, 'error');
            errorMsg.textContent = err.message;
            errorMsg.classList.remove('hide');
            confirmBtn.disabled = false;
            confirmBtn.textContent = 'Confirmar Exclusão';
        }
    });
}

document.addEventListener('DOMContentLoaded', ()=>{
  loadThemes();
  const activePage = document.body.dataset.active;
  if(user) {
    mountSidebar(activePage);
    initializeTopbarButtons();
  }
  
  const pageInitializers = {
    dashboard: dashboardInit,
    devices: devicesInit,
    login: loginInit,
    register: registerInit,
    reports: reportsInit,
    settings: settingsInit,
    user: userPageInit 
};
  if(pageInitializers[activePage]) {
    pageInitializers[activePage]();
  }
});


// FUNÇÕES DA BATERIA (podem ficar fora do DOMContentLoaded)

async function fetchBatteryData() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/battery/status');
        if (!response.ok) {
            throw new Error('Falha ao buscar dados da bateria');
        }
        const data = await response.json();
        createBatteryChart(data);
    } catch (error) {
        console.error("Erro:", error);
    }
}

function createBatteryChart(data) {
    const ctx = document.getElementById('batteryPieChart')?.getContext('2d');
    if (!ctx) return; // Se não encontrar o elemento, para a execução

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Status da Bateria',
                data: [data.charged_percentage, data.empty_percentage],
                backgroundColor: [
                    'rgba(0, 255, 0, 0.1)',
                    'rgba(255, 0, 0, 0.1)'
                ],
                borderColor: [
                    'rgba(0, 255, 0)',
                    'rgba(255, 0, 0)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            cutout: '55%',
            responsive: true,
            plugins: {
                legend: { position: 'top' },
                title: { display: true, text: 'Nível da Bateria' }
            }
        }
    });

    // ===== A LÓGICA FOI MOVIDA PARA CÁ (O LUGAR CORRETO) =====
    const statusTextEl = el('battery-status-text');
    const flowWattsEl = el('battery-flow-watts');

    if (statusTextEl && flowWattsEl) {
        statusTextEl.textContent = data.status_texto;
        flowWattsEl.textContent = `${data.fluxo_watts} W`;

        if (data.fluxo_watts > 0) {
            flowWattsEl.style.color = 'var(--success)';
        } else {
            flowWattsEl.style.color = 'var(--warning)';
        }
    }
}
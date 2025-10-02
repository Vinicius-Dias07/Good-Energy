// --- FUNÇÕES GLOBAIS E DE INICIALIZAÇÃO ---
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
    setTimeout(() => toast.remove(), 6000); 
}

function showConfirmDialog(title, message) {
    const modal = el('confirmModal');
    if (!modal) return Promise.resolve(false);

    el('confirmTitle').textContent = title;
    el('confirmMessage').textContent = message;
    modal.classList.remove('hide');

    return new Promise((resolve) => {
        const confirmBtn = el('confirmBtn');
        const cancelBtn = el('cancelBtn');

        const onConfirm = () => {
            modal.classList.add('hide');
            resolve(true);
        };
        const onCancel = () => {
            modal.classList.add('hide');
            resolve(false);
        };

        confirmBtn.addEventListener('click', onConfirm, { once: true });
        cancelBtn.addEventListener('click', onCancel, { once: true });
    });
}

async function fetchWeather() {
    const apiKey = '288e9288c597f70a80a921fd488da25a'; 
    const lat = -23.5614; const lon = -46.6565;
    const apiUrl = `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&appid=${apiKey}&units=metric&lang=pt_br`;
    try {
        const response = await fetch(apiUrl);
        if (!response.ok) throw new Error('Não foi possível obter a previsão do tempo.');
        const data = await response.json();
        el('weather-icon').src = `https://openweathermap.org/img/wn/${data.weather[0].icon}@2x.png`;
        el('weather-temp').textContent = `${Math.round(data.main.temp)}°C`;
        el('weather-desc').textContent = data.weather[0].description;
        el('weather-location-name').textContent = data.name;
        el('weather-humidity').textContent = `${data.main.humidity} %`;
        el('weather-wind').textContent = `${Math.round(data.wind.speed * 3.6)} km/h`;
        el('weather-clouds').textContent = `${data.clouds.all} %`;

        const forecastEl = el('generationForecast');
        if (forecastEl) {
            const cloudiness = data.clouds.all;
            if (cloudiness < 25) {
                forecastEl.innerHTML = 'Alta ☀️';
            } else if (cloudiness < 60) {
                forecastEl.innerHTML = 'Moderada 🌥️';
            } else {
                forecastEl.innerHTML = 'Baixa ☁️';
            }
        }
    } catch (error) {
        console.error("Erro ao buscar dados do clima:", error);
    }
}

// --- LÓGICA DE TEMAS ---
async function saveThemePreference(theme, colorTheme) {
    if (!user) return;
    try {
        const payload = { email: user.email };
        const updatedUser = { ...JSON.parse(localStorage.getItem('ge_user')) };
        if (theme !== undefined) { payload.theme = theme; updatedUser.theme = theme; }
        if (colorTheme !== undefined) { payload.colorTheme = colorTheme; updatedUser.colorTheme = colorTheme; }
        localStorage.setItem('ge_user', JSON.stringify(updatedUser));
        await fetch('http://127.0.0.1:5000/api/user/theme', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
        showToast('Preferência de tema salva!', 'success');
    } catch (error) { console.error("Não foi possível salvar a preferência de tema:", error); }
}

function applyColorTheme(colorTheme) {
    document.body.dataset.colortheme = colorTheme;
    el('colorThemeSwitcher')?.querySelectorAll('button').forEach(btn => btn.classList.toggle('active', btn.dataset.colortheme === colorTheme));
}

function applyTheme(theme) {
    document.body.dataset.theme = theme;
    el('themeSwitcher')?.querySelectorAll('button').forEach(btn => btn.classList.toggle('active', btn.dataset.theme === theme));
}

function loadThemes() {
    const currentUser = JSON.parse(localStorage.getItem('ge_user'));
    applyColorTheme(currentUser?.colorTheme || 'dark');
    applyTheme(currentUser?.theme || 'padrão');
}

// --- MONTAGEM DA INTERFACE (SIDEBAR, TOPBAR) ---
function mountSidebar(active = 'dashboard') {
    const nav = document.querySelector('.nav');
    if (!nav) return;
    const icons = { dashboard: `<svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>`, devices: `<svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M5 12h14M12 5l7 7-7 7"></path></svg>`, reports: `<svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V7a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>`, user: `<svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>`, help: `<svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`, settings: `<svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>`, logout: `<svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path></svg>` };
    const navItems = [['dashboard.html', 'dashboard', 'Dashboard'], ['devices.html', 'devices', 'Dispositivos'], ['reports.html', 'reports', 'Relatórios'], ['user.html', 'user', 'Usuário'], ['help.html', 'help', 'Ajuda & FAQ'], ['settings.html', 'settings', 'Configurações']];
    nav.innerHTML = navItems.map(([href, id, label]) => `<a href="${href}" class="${active === id ? 'active' : ''}" title="${label}">${icons[id] || ''}<span>${label}</span></a>`).join('');
    const logoutButton = document.createElement('a');
    logoutButton.href = "#";
    logoutButton.id = "logoutBtn";
    logoutButton.title = "Sair";
    logoutButton.innerHTML = `${icons.logout}<span>Sair</span>`;
    nav.appendChild(logoutButton);
    logoutButton.addEventListener('click', async (e) => {
        e.preventDefault();
        const confirmed = await showConfirmDialog('Sair da Sessão', 'Tem certeza que deseja sair da sua conta?');
        if (confirmed) {
            localStorage.clear();
            window.location.href = 'index.html';
        }
    });
    if (user) el('userName').textContent = user.name.split(' ')[0];
}

function initializeTopbarButtons() {
    const notifBtn = el('notificationsBtn'), notifPopup = el('notificationsPopup');
    if (notifBtn && notifPopup) {
        const alertsContainer = el('popupAlerts'), badge = el('notificationBadge');
        const allPossibleAlerts = [{ type: 'warn', text: 'Detecção de consumo anômalo na madrugada.' }, { type: 'success', text: 'Produção solar 20% acima da média hoje!' }, { type: 'info', text: 'Lembrete: Limpeza dos painéis recomendada.' }];
        
        const updateNotifications = () => {
            if (user?.notifications === 'disabled') {
                if(alertsContainer) alertsContainer.innerHTML = '<div class="row info"><div>As notificações estão silenciadas.</div></div>';
                if(badge) badge.classList.add('hide');
                return;
            }
            const alertsToShow = allPossibleAlerts.sort(() => 0.5 - Math.random()).slice(0, Math.floor(Math.random() * 3) + 1);
            if (alertsContainer) alertsContainer.innerHTML = alertsToShow.map(a => `<div class="row ${a.type}"><span class="tag">${a.type === 'warn' ? 'Atenção' : a.type === 'success' ? 'Dica' : 'Info'}</span><div>${a.text}</div></div>`).join('');
            if (badge) {
                if (alertsToShow.length > 0) { badge.textContent = alertsToShow.length; if (notifPopup.classList.contains('hide')) badge.classList.remove('hide'); } else { badge.classList.add('hide'); }
            }
        };
        setInterval(updateNotifications, 30000);
        updateNotifications();

        notifBtn.addEventListener('click', (e) => { e.stopPropagation(); notifPopup.classList.toggle('hide'); if (badge) badge.classList.add('hide'); });
        document.addEventListener('click', () => notifPopup.classList.add('hide'));
        notifPopup.addEventListener('click', e => e.stopPropagation());
    }
}

// --- FUNÇÕES DE PÁGINAS ESPECÍFICAS ---

function loginInit() {
    const form = el('loginForm');
    if (!form) return;
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        showLoader();
        try {
            const response = await fetch('http://127.0.0.1:5000/api/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email: form.email.value, password: form.pass.value }), });
            const result = await response.json();
            if (!response.ok) throw new Error(result.error || 'Falha na autenticação.');
            localStorage.setItem('ge_user', JSON.stringify(result));
            showToast(`Bem-vindo de volta, ${result.name}!`, 'success');
            setTimeout(() => window.location.href = 'dashboard.html', 500);
        } catch (error) { showToast(error.message, 'error'); } finally { hideLoader(); }
    });
}

function registerInit() {
    const form = el('registerForm');
    if (!form) return;
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        showLoader();
        try {
            const response = await fetch('http://127.0.0.1:5000/api/register', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: form.name.value, email: form.email.value, password: form.pass.value }), });
            const result = await response.json();
            if (!response.ok) throw new Error(result.error || 'Não foi possível criar a conta.');
            localStorage.setItem('ge_user', JSON.stringify(result));
            showToast(`Cadastro realizado, ${result.name}! Redirecionando...`, 'success');
            setTimeout(() => window.location.href = 'dashboard.html', 1500);
        } catch (error) { showToast(error.message, 'error'); } finally { hideLoader(); }
    });
}

async function initializeAiSmartStack() {
    const container = el('aiSmartStackContainer');
    const slidesContainer = el('aiSmartStackSlides');
    const nextBtn = el('stackNextBtn');
    const prevBtn = el('stackPrevBtn');

    if (!container || !slidesContainer) return;

    try {
        const response = await fetch(`http://127.0.0.1:5000/api/dashboard-insights?email=${user.email}`);
        const insights = await response.json();

        if (!insights || insights.length === 0) return;

        slidesContainer.innerHTML = ''; // Limpa slides antigos

        // Cria os slides
        insights.forEach((insight) => {
            const slide = document.createElement('div');
            slide.className = 'smart-stack-slide';
            const emoji = insight.type === 'elogio' ? '🎉' : insight.type === 'alerta' ? '⚠️' : '💡';
            slide.innerHTML = `<strong>${emoji} ${insight.type.charAt(0).toUpperCase() + insight.type.slice(1)}</strong>${insight.text}`;
            slidesContainer.appendChild(slide);
        });

        container.style.display = 'flex'; // Mostra o container como flex

        let currentIndex = 0;
        const allSlides = slidesContainer.querySelectorAll('.smart-stack-slide');
        const totalSlides = allSlides.length;
        let autoRotateInterval;

        const showSlide = (index) => {
            allSlides.forEach(slide => slide.classList.remove('active'));
            currentIndex = (index + totalSlides) % totalSlides;
            allSlides[currentIndex].classList.add('active');
        };
        
        const startAutoRotate = () => {
            stopAutoRotate();
            autoRotateInterval = setInterval(() => {
                showSlide(currentIndex + 1);
            }, 8000); // Rotação a cada 8 segundos
        };

        const stopAutoRotate = () => {
            clearInterval(autoRotateInterval);
        };

        nextBtn.addEventListener('click', () => {
            showSlide(currentIndex + 1);
            startAutoRotate();
        });
        prevBtn.addEventListener('click', () => {
            showSlide(currentIndex - 1);
            startAutoRotate();
        });

        showSlide(0);
        startAutoRotate();

    } catch (error) {
        console.error("Erro ao inicializar o Smart Stack:", error);
    }
}

async function dashboardInit() {
    // --- LÓGICA PARA CARREGAR DISPOSITIVOS NO OTIMIZADOR ---
    const taskSelect = el('taskSelect');
    if (taskSelect) {
        try {
            const response = await fetch(`http://127.0.0.1:5000/api/devices?email=${user.email}`);
            const devices = await response.json();
            
            if (devices.length > 0) {
                taskSelect.innerHTML = devices.map(d => `<option value="${d.name}">${d.name}</option>`).join('');
            } else {
                taskSelect.innerHTML = '<option value="">Nenhum dispositivo cadastrado</option>';
                el('optimizeTaskBtn').disabled = true;
            }
        } catch (error) {
            console.error("Erro ao carregar dispositivos para o otimizador:", error);
            taskSelect.innerHTML = '<option value="">Erro ao carregar</option>';
        }
    }
    
    // Variáveis para guardar as instâncias dos gráficos
    let energyChartInstance = null;
    let savingsChartInstance = null;
    let batteryChartInstance = null;

    // Função que busca e atualiza todos os dados do dashboard
    const updateDashboardData = async () => {
        console.log("Atualizando dados do dashboard...");
        try {
            const [kpisResponse, chartResponse, batteryResponse] = await Promise.all([
                fetch(`http://127.0.0.1:5000/api/kpis?email=${user.email}`),
                fetch('http://127.0.0.1:5000/api/generation/history'),
                fetch('http://127.0.0.1:5000/api/battery/status')
            ]);

            if (!kpisResponse.ok || !chartResponse.ok || !batteryResponse.ok) return;

            const kpisData = await kpisResponse.json();
            const chartData = await chartResponse.json();
            const batteryData = await batteryResponse.json();

            // Atualiza KPIs
            const todayGen = kpisData?.todayGenKwh ?? 0;
            const userTariff = user.tariff || 0.95;
            el('kpiGen').textContent = `${todayGen.toFixed(1)} kWh`;
            el('kpiUse').textContent = `${(kpisData?.houseLoadKw ?? 0).toFixed(2)} kW`;
            el('kpiSaving').textContent = `R$ ${(todayGen * userTariff).toFixed(2)}`;

            // Atualiza Gráfico de Geração
            if (energyChartInstance) energyChartInstance.destroy();
            const energyCtx = el('chartEnergy')?.getContext('2d');
            if (energyCtx) {
                energyChartInstance = new Chart(energyCtx, {
                    type: 'line', data: { labels: chartData.labels,
                        datasets: [
                            { label: 'Geração (kW)', data: chartData.generation_kw, fill: true, tension: 0.35, backgroundColor: 'rgba(34, 197, 94, 0.2)', borderColor: 'rgba(34, 197, 94, 1)' },
                            { label: 'Consumo (kW)', data: chartData.generation_kw.map(g => Math.max(0.2, g * (0.6 + Math.random() * 0.3))).map(v => +v.toFixed(2)), fill: true, tension: 0.35, backgroundColor: 'rgba(239, 68, 68, 0.2)', borderColor: 'rgba(239, 68, 68, 1)' }
                        ]
                    }, options: { responsive: true, maintainAspectRatio: false }
                });
            }

            // Atualiza Gráfico da Bateria
            if (batteryChartInstance) batteryChartInstance.destroy();
            const batteryCtx = el('batteryPieChart')?.getContext('2d');
            if (batteryCtx) {
                batteryChartInstance = new Chart(batteryCtx, {
                    type: 'doughnut',
                    data: {
                        datasets: [{ data: [batteryData.charged_percentage, batteryData.empty_percentage], backgroundColor: ['rgba(34, 197, 94, 0.2)', 'rgba(239, 68, 68, 0.1)'], borderColor: ['rgba(34, 197, 94, 1)', 'rgba(239, 68, 68, 1)'], borderWidth: 1 }]
                    },
                    options: { cutout: '70%', responsive: true, plugins: { legend: { display: false }, title: { display: true, text: `Bateria: ${batteryData.charged_percentage}%` } } }
                });
            }
            el('battery-status-text').textContent = batteryData.status_texto;
            el('battery-flow-watts').textContent = `${batteryData.fluxo_watts} W`;

            // Atualiza Gráfico de Metas
            const savedAmount = kpisData.savingsThisMonth || 0;
            const goalAmount = user.savingsGoal || 500;
            if (savingsChartInstance) savingsChartInstance.destroy();
            const savingsCtx = el('savingsGoalChart')?.getContext('2d');
            if (savingsCtx) {
                savingsChartInstance = new Chart(savingsCtx, {
                    type: 'doughnut',
                    data: {
                        datasets: [{ data: [savedAmount, Math.max(0, goalAmount - savedAmount)], backgroundColor: ['rgba(59, 130, 246, 0.2)', 'rgba(55, 65, 81, 0.2)'], borderColor: ['rgba(59, 130, 246, 1)', 'rgba(55, 65, 81, 1)'], borderWidth: 1 }]
                    },
                    options: { cutout: '70%', responsive: true, plugins: { legend: { display: false }, title: { display: true, text: `Meta: ${((savedAmount / goalAmount) * 100).toFixed(0)}%` } } }
                });
            }
            el('goalValueText').innerText = `R$ ${goalAmount.toFixed(2)}`;
            el('currentSavingsText').innerText = `R$ ${savedAmount.toFixed(2)}`;
            el('goalAchieved').innerText = `${((savedAmount / goalAmount) * 100).toFixed(0)} %`;
            el('goalRemaining').innerText = `R$ ${(goalAmount - savedAmount).toFixed(2)}`;
            el('goalProjection').innerText = `R$ ${(savedAmount * 1.5).toFixed(2)}`;

        } catch (error) {
            console.error("Erro ao atualizar o dashboard:", error);
        }
    };
    
    // Roda as funções que só precisam ser executadas uma vez
    showLoader();
    fetchWeather();
    initializeAiSmartStack();
    updateDashboardData().finally(() => hideLoader());
    
    // Configura o intervalo para a atualização dos dados
    setInterval(updateDashboardData, 30000);

    // --- LÓGICA DO OTIMIZADOR DE TAREFAS (AGORA NO LUGAR CORRETO) ---
    const optimizeBtn = el('optimizeTaskBtn');
    const resultDiv = el('optimizerResult');
    const timeEl = el('recommendedTime');
    const reasonEl = el('recommendationReason');

    if (optimizeBtn && taskSelect) {
        optimizeBtn.addEventListener('click', async () => {
            const selectedTask = taskSelect.value;
            const originalBtnText = optimizeBtn.textContent;

            optimizeBtn.disabled = true;
            optimizeBtn.textContent = 'Analisando...';
            resultDiv.classList.add('hide');
            showLoader();

            try {
                const response = await fetch('http://127.0.0.1:5000/api/optimizer/suggest-time', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ task: selectedTask, email: user.email })
                });
                const data = await response.json();

                if (data.horario_recomendado) {
                    timeEl.textContent = data.horario_recomendado;
                    reasonEl.textContent = data.justificativa;
                    resultDiv.classList.remove('hide');
                } else {
                    showToast(data.error || 'Não foi possível gerar uma sugestão.', 'error');
                }

            } catch (error) {
                console.error("Erro no otimizador:", error);
                showToast('Erro ao se comunicar com o otimizador.', 'error');
            } finally {
                optimizeBtn.disabled = false;
                optimizeBtn.textContent = originalBtnText;
                hideLoader();
            }
        });
    }
}

function devicesInit() {
    const tbody = el('deviceTableBody'), modal = el('addDeviceModal'), addBtn = el('addDeviceBtn'), closeBtn = el('closeModalBtn'), form = el('addDeviceForm');
    if (!tbody || !modal || !addBtn || !closeBtn || !form) return;

    const render = (devices) => {
        tbody.innerHTML = devices.map(d => `
            <tr>
                <td>${d.name}</td>
                <td>${d.room}</td>
                <td>${d.watts} W</td>
                <td>${d.cost_per_hour}</td>
                <td><span class="tag ${d.on ? 'success' : 'fail'}">${d.on ? 'Ligado' : 'Desligado'}</span></td>
                <td class="device-actions">
                    <button class="icon-btn" data-action="toggle" data-id="${d.id}" data-state="${d.on}" title="${d.on ? 'Desligar' : 'Ligar'}"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M5.636 18.364a9 9 0 010-12.728m12.728 0a9 9 0 010 12.728m-9.9-2.829a5 5 0 010-7.07m7.072 0a5 5 0 010 7.07M12 6v6"></path></svg></button>
                    <button class="icon-btn" data-action="delete" data-id="${d.id}" title="Excluir"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg></button>
                </td>
            </tr>
        `).join('');
    };

    const fetchAndRender = async () => {
        showLoader();
        try {
            const response = await fetch(`http://127.0.0.1:5000/api/devices?email=${user.email}`);
            if (!response.ok) throw new Error('Não foi possível carregar os dispositivos.');
            render(await response.json());
        } catch (error) { showToast(error.message, 'error'); } 
        finally { hideLoader(); }
    };

    tbody.addEventListener('click', async (e) => {
        const button = e.target.closest('button');
        if (!button) return;
        const { action, id, state } = button.dataset;
        if (action === 'toggle') {
            try { await fetch(`http://127.0.0.1:5000/api/devices/${id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email: user.email, on: !(state === 'true') }) }); fetchAndRender(); } catch (error) { showToast('Erro ao atualizar dispositivo.', 'error'); }
        }
        if (action === 'delete') {
            const confirmed = await showConfirmDialog('Excluir Dispositivo', 'Esta ação é permanente. Tem certeza que deseja excluir este dispositivo?');
            if (confirmed) {
                try { 
                    await fetch(`http://127.0.0.1:5000/api/devices/${id}?email=${user.email}`, { method: 'DELETE' });
                    fetchAndRender(); 
                } catch (error) { 
                    showToast('Erro ao excluir dispositivo.', 'error'); 
                }
            }
        }
    });

    addBtn.addEventListener('click', () => modal.classList.remove('hide'));
    closeBtn.addEventListener('click', () => modal.classList.add('hide'));
    modal.addEventListener('click', (e) => { if (e.target === modal) modal.classList.add('hide'); });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.textContent = 'Adicionando...';
        try {
            const response = await fetch('http://127.0.0.1:5000/api/devices', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email: user.email, name: form.name.value, room: form.room.value, type: form.type.value, }) });
            if (!response.ok) throw new Error('Não foi possível adicionar o dispositivo.');
            form.reset();
            modal.classList.add('hide');
            showToast('Dispositivo adicionado!', 'success');
            fetchAndRender();
        } catch (error) { showToast(error.message, 'error'); } 
        finally { submitBtn.disabled = false; submitBtn.textContent = originalBtnText; }
    });
    fetchAndRender();
}

function reportsInit() {
    let reportChartInstance;

    // Função para gerar o gráfico (LÓGICA RESTAURADA)
    const generateReportChart = async () => {
        if (typeof Chart === 'undefined') return;
        showLoader();
        try {
            const response = await fetch('http://127.0.0.1:5000/api/reports/monthly');
            if (!response.ok) throw new Error("Não foi possível carregar o relatório.");
            const reportData = await response.json();
            const ctx = el('reportChart');
            if (!ctx) return;
            if (reportChartInstance) reportChartInstance.destroy();
            reportChartInstance = new Chart(ctx, { 
                type: 'bar', 
                data: { 
                    labels: reportData.map(item => item.date), 
                    datasets: [{ 
                        label: 'Geração Mensal (kWh)', 
                        data: reportData.map(item => item.generation), 
                        backgroundColor: 'rgba(59, 130, 246, 0.5)', 
                        borderColor: '#3b82f6' 
                    }] 
                }, 
                options: { responsive: true, maintainAspectRatio: false } 
            });
        } catch (error) { 
            showToast(error.message, 'error'); 
        } finally { 
            hideLoader(); 
        }
    };

    // Função para buscar os insights da IA (lógica que já adicionamos)
    const fetchInsights = async () => {
        const card = el('insightsCard');
        const textContainer = el('insightsText');
        if (!card || !textContainer) return;

        try {
            const response = await fetch(`http://127.0.0.1:5000/api/reports/insights?email=${user.email}`);
            const data = await response.json();

            if (data.insights) {
                textContainer.innerHTML = marked.parse(data.insights);
                card.style.display = 'block';
            } else {
                textContainer.innerHTML = `<p>${data.error || 'Não foi possível carregar a análise.'}</p>`;
                card.style.display = 'block';
            }
        } catch (error) {
            console.error("Erro ao buscar insights:", error);
            textContainer.innerHTML = `<p>Ocorreu um erro ao buscar a análise.</p>`;
            card.style.display = 'block';
        }
    };

    // Roda as duas funções ao carregar a página
    generateReportChart();
    fetchInsights();
}

function settingsInit() {
    const tariffInput = el('tariffInput');
    const savingsGoalInput = el('savingsGoalInput');
    const notificationsSelect = el('notificationsSelect');
    if (tariffInput && user.tariff !== undefined) tariffInput.value = user.tariff;
    if (savingsGoalInput && user.savingsGoal !== undefined) savingsGoalInput.value = user.savingsGoal;
    if (notificationsSelect && user.notifications) notificationsSelect.value = user.notifications;

    el('themeSwitcher')?.addEventListener('click', (e) => {
        e.preventDefault();
        const button = e.target.closest('button');
        if (button) {
            applyTheme(button.dataset.theme);
            saveThemePreference(button.dataset.theme, undefined);
        }
    });

    el('colorThemeSwitcher')?.addEventListener('click', (e) => {
        e.preventDefault();
        const button = e.target.closest('button');
        if (button) {
            applyColorTheme(button.dataset.colortheme);
            saveThemePreference(undefined, button.dataset.colortheme);
        }
    });

    const otherPreferences = document.querySelectorAll('#tariffInput, #savingsGoalInput, #notificationsSelect');
    
    const saveOtherPreferences = async () => {
        showLoader();
        try {
            const response = await fetch('http://127.0.0.1:5000/api/user/preferences', {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ 
                    email: user.email, 
                    tariff: el('tariffInput').value, 
                    savingsGoal: el('savingsGoalInput').value,
                    notifications: el('notificationsSelect').value
                })
            });
            const updatedUser = await response.json();
            if (!response.ok) throw new Error(updatedUser.error || "Falha ao salvar preferências.");
            
            localStorage.setItem('ge_user', JSON.stringify(updatedUser));
            showToast('Preferências salvas!', 'success');
        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            hideLoader();
        }
    };
    otherPreferences.forEach(input => {
        input.addEventListener('change', saveOtherPreferences);
    });
}

function userPageInit() {
    if (!user) return;
    const uName = el('uName'), uEmail = el('uEmail'), planTag = el('planTag');
    if (uName) uName.value = user.name;
    if (uEmail) uEmail.value = user.email;
    if (planTag) planTag.textContent = user.plan;

    const saveBtn = el('userSave');
    if(saveBtn) {
        saveBtn.addEventListener('click', async () => {
            const newName = uName.value;
            if (!newName.trim()) { showToast('O nome não pode estar vazio.', 'error'); return; }
            showLoader();
            try {
                const response = await fetch('http://127.0.0.1:5000/api/user/profile', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email: user.email, name: newName }) });
                const updatedUser = await response.json();
                if (!response.ok) throw new Error(updatedUser.error || 'Falha ao atualizar perfil.');
                localStorage.setItem('ge_user', JSON.stringify(updatedUser));
                el('userName').textContent = updatedUser.name.split(' ')[0];
                showToast('Perfil atualizado com sucesso!', 'success');
            } catch (error) { showToast(error.message, 'error'); } 
            finally { hideLoader(); }
        });
    }

    const deleteBtn = el('deleteAccountBtn'), confirmBox = el('deleteConfirmBox'), cancelBtn = el('deleteCancelBtn'), confirmBtn = el('deleteConfirmBtn'), passwordInput = el('deletePasswordInput'), errorMsg = el('deleteErrorMsg');
    if (!deleteBtn || !confirmBox || !cancelBtn || !confirmBtn) return;
    
    deleteBtn.addEventListener('click', () => { deleteBtn.classList.add('hide'); confirmBox.classList.remove('hide'); });
    cancelBtn.addEventListener('click', () => { confirmBox.classList.add('hide'); deleteBtn.classList.remove('hide'); passwordInput.value = ''; errorMsg.classList.add('hide'); });

    confirmBtn.addEventListener('click', async () => {
        const password = passwordInput.value;
        if (!password) { errorMsg.textContent = "Digite sua senha para confirmar."; errorMsg.classList.remove('hide'); return; }
        errorMsg.classList.add('hide');
        confirmBtn.disabled = true;
        confirmBtn.textContent = 'Excluindo...';
        showLoader();
        try {
            const response = await fetch('http://127.0.0.1:5000/api/user', { method: 'DELETE', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email: user.email, password: password }) });
            const result = await response.json();
            if (!response.ok) throw new Error(result.error || 'Não foi possível excluir a conta.');
            localStorage.clear();
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

// --- PONTO DE ENTRADA PRINCIPAL DO SCRIPT ---
document.addEventListener('DOMContentLoaded', () => {
    loadThemes();
    const activePage = document.body.dataset.active;
    if (user) {
        mountSidebar(activePage);
        initializeTopbarButtons();
    }
    const pageInitializers = { dashboard: dashboardInit, devices: devicesInit, login: loginInit, register: registerInit, reports: reportsInit, settings: settingsInit, user: userPageInit };
    if (pageInitializers[activePage]) {
        pageInitializers[activePage]();
    }
});
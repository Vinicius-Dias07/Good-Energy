const user = JSON.parse(localStorage.getItem('ge_user') || '{"name":"Davi","plan":"Starter","email":"davi@example.com"}');

let state = {
  solarNowKw: 4.2,
  houseLoadKw: 3.1,
  batteryPct: 67,
  gridImportKw: 0.0,
  todayGenKwh: 18.5,
  todayUseKwh: 15.7,
  savingsBRL: 12.35,
  co2SavedKg: 9.2,
  alerts: [
    {type:'warn', text:'Nuvens densas — geração caindo 22%'},
    {type:'success', text:'Horário ideal para carregar o carro nas próximas 2h'},
    {type:'info', text:'Bateria com carga total em 45 minutos.'},
  ],
  devices:[
    {id:1, name:'Ar-Condicionado Sala', room:'Sala', type:'climate', on:true, watts:900},
    {id:2, name:'Geladeira', room:'Cozinha', type:'appliance', on:true, watts:130},
    {id:3, name:'Aquecedor de Água', room:'Lavanderia', type:'water', on:false, watts:0},
    {id:4, name:'Luzes Jardim', room:'Externo', type:'light', on:false, watts:0},
    {id:5, name:'Tomada EV', room:'Garagem', type:'ev', on:false, watts:0},
  ],
  history: Array.from({length:24}, (_,h)=>({h, gen: Math.max(0, (Math.sin((h-6)/12*Math.PI)*5)+Math.random()*0.4), use: (2.2+Math.random()*0.9)}))
};

const el = id => document.getElementById(id);

/**
 * Simula uma chamada de API, retornando uma Promise após um delay.
 * @param {any} data - O dado a ser retornado em caso de sucesso.
 * @param {number} delay - O tempo em ms para a simulação.
 * @param {boolean} shouldFail - Se a chamada deve falhar.
 * @returns {Promise<any>}
 */
function simulateApiCall(data, delay = 700, shouldFail = false) {
    showLoader();
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            hideLoader();
            if (shouldFail) {
                reject(new Error("Falha na comunicação com o servidor."));
            } else {
                resolve(JSON.parse(JSON.stringify(data)));
            }
        }, delay);
    });
}

const showLoader = () => el('loader-overlay')?.classList.remove('hide');
const hideLoader = () => el('loader-overlay')?.classList.add('hide');

/**
 * 
 * @param {string} message 
 * @param {'success'|'error'} type 
 */
function showToast(message, type = 'success') {
    const container = el('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => {
        toast.remove();
    }, 4000); 
}

function applyTheme(theme) {
  document.body.dataset.theme = theme;
  localStorage.setItem('ge_theme', theme);
  document.querySelectorAll('.theme-switcher button').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.theme === theme);
  });
}

function loadTheme() {
  const savedTheme = localStorage.getItem('ge_theme') || 'padrão';
  applyTheme(savedTheme);
}

function mountSidebar(active='dashboard'){
  const nav = document.querySelector('.nav');
  if(!nav) return;

  const icons = {
    dashboard: `<svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>`,
    devices: `<svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M5 12h14M12 5l7 7-7 7"></path></svg>`,
    reports: `<svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V7a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>`,
    user: `<svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>`,
    help: `<svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`,
    settings: `<svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>`
  };
  const navItems = [
    ['dashboard.html','dashboard','Dashboard'], ['devices.html','devices','Dispositivos'], ['reports.html','reports','Relatórios'],
    ['user.html','user','Usuário'], ['help.html','help','Ajuda & FAQ'], ['settings.html','settings','Configurações'],
  ];
  nav.innerHTML = navItems.map(([href, id, label]) => `<a href="${href}" class="${active === id ? 'active' : ''}" title="${label}">${icons[id] || ''}<span>${label}</span></a>`).join('');
  el('userName') && (el('userName').textContent = user.name);
}

function kpiFill(data){
  el('kpiGen').textContent = `${data.todayGenKwh.toFixed(1)} kWh`;
  el('kpiUse').textContent = `${data.todayUseKwh.toFixed(1)} kWh`;
  el('kpiBatt').textContent = `${data.batteryPct.toFixed(0)}%`;
  el('kpiSaving').textContent = `R$ ${data.savingsBRL.toFixed(2)}`;
  const bar = document.querySelector('.progress > span'); if(bar) bar.style.width = data.batteryPct+'%';
}

function renderAlerts(target = 'alertList', data) {
    const alertList = el(target);
    if (!alertList) return;
    if (data.length === 0) {
        alertList.innerHTML = `<div class="row"><span>Nenhum alerta recente.</span></div>`;
        return;
    }
    alertList.innerHTML = data.map(a => `
        <div class="row">
            <span class="tag ${a.type}">${a.type === 'warn' ? 'Atenção' : a.type === 'success' ? 'Sucesso' : 'Info'}</span>
            <div class="right">${a.text}</div>
        </div>
    `).join('');
}

async function renderDevices() {
    const tbody = document.querySelector('#deviceTable tbody');
    if (!tbody) return;

    try {
        const devices = await simulateApiCall(state.devices);
        tbody.innerHTML = devices.map(d => `
            <tr>
                <td>${d.name}<br><span class="tag" style="opacity:0.7">${d.room}</span></td>
                <td>${d.type}</td>
                <td>${d.on ? '<span class="tag success">Ligado</span>' : '<span class="tag fail">Desligado</span>'}</td>
                <td>${d.watts} W</td>
                <td class="right">
                    <button class="icon-btn" data-tgl-id="${d.id}">${d.on ? 'Desligar' : 'Ligar'}</button>
                </td>
            </tr>
        `).join('');

        tbody.querySelectorAll('button[data-tgl-id]').forEach(btn => btn.addEventListener('click', async e => {
            const id = +e.target.dataset.tglId;
            const dev = state.devices.find(x => x.id === id);
            dev.on = !dev.on; 
            dev.watts = dev.on ? (dev.type === 'light' ? 30 : dev.type === 'ev' ? 2300 : dev.type === 'climate' ? 900 : 200) : 0;
            
            
            renderDevices(); 
            
            try {
                
                await simulateApiCall({ status: 'ok' }, 400); 
                showToast(`'${dev.name}' foi ${dev.on ? 'ligado' : 'desligado'}.`, 'success');
            } catch (error) {
                showToast(`Falha ao alterar status de '${dev.name}'.`, 'error');
                
                dev.on = !dev.on;
                renderDevices();
            }
        }));
    } catch (error) {
        showToast(error.message, 'error');
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding: 20px;">Não foi possível carregar os dispositivos.</td></tr>`;
    }
}

let energyChart, batteryChart;
function charts(history, battery) {
  if (typeof Chart === 'undefined') return;
  Chart.defaults.color = '#cdd7ee';
  Chart.defaults.borderColor = 'rgba(255,255,255,0.1)';

  const ctx = el('chartEnergy');
  if (ctx) {
    energyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: history.map(h => h.h + 'h'),
            datasets: [
                { label: 'Geração (kW)', data: history.map(h => Math.max(0, +h.gen.toFixed(2))), fill: true, tension: .35, backgroundColor: 'rgba(34, 197, 94, 0.2)', borderColor: '#22c55e' },
                { label: 'Consumo (kW)', data: history.map(h => +h.use.toFixed(2)), fill: true, tension: .35, backgroundColor: 'rgba(239, 68, 68, 0.2)', borderColor: '#ef4444' }
            ]
        },
        options: { responsive: true, maintainAspectRatio: true }
    });
  }
  const btx = el('chartBattery');
  if (btx) {
    batteryChart = new Chart(btx, {
        type: 'doughnut',
        data: {
            labels: ['Carga', 'Livre'],
            datasets: [{ data: [battery.batteryPct, 100 - battery.batteryPct], backgroundColor: ['#3b82f6', '#1f2937'], borderWidth: 0 }]
        },
        options: { cutout: '70%', plugins: { legend: { display: false } } }
    });
  }
}

function loginInit(){
  const form = el('loginForm');
  if (!form) return;
  
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const emailInput = form.querySelector('[name=email]');
    const passInput = form.querySelector('[name=pass]');
    let isValid = true;
    
    // Validação
    [emailInput, passInput].forEach(input => input.classList.remove('invalid'));
    if (!emailInput.value || !/^\S+@\S+\.\S+$/.test(emailInput.value)) {
      emailInput.classList.add('invalid');
      isValid = false;
    }
    if (!passInput.value) {
      passInput.classList.add('invalid');
      isValid = false;
    }
    
    if (!isValid) {
      showToast('Por favor, preencha os campos corretamente.', 'error');
      return;
    }

    try {
      const name = form.querySelector('[name=name]').value || 'Usuário';
      await simulateApiCall({ token: 'fake_jwt_token' }); 
      localStorage.setItem('ge_user', JSON.stringify({ name, email: emailInput.value, plan: 'Starter' }));
      showToast('Login bem-sucedido!', 'success');
      setTimeout(() => window.location.href = 'dashboard.html', 500);
    } catch (error) {
      showToast('Credenciais inválidas.', 'error');
    }
  });
}

async function populateUser() {
  const uName = el('uName'), uEmail = el('uEmail'), planTag = el('planTag');
  if (!uName) return;

  try {
    const userData = await simulateApiCall(user);
    uName.value = userData.name;
    uEmail.value = userData.email;
    planTag.textContent = userData.plan;

    el('userSave').addEventListener('click', async () => {
        uName.classList.remove('invalid');
        uEmail.classList.remove('invalid');
        if (!uName.value || !uEmail.value || !/^\S+@\S+\.\S+$/.test(uEmail.value)) {
          showToast('Por favor, preencha os campos corretamente.', 'error');
          if (!uName.value) uName.classList.add('invalid');
          if (!uEmail.value || !/^\S+@\S+\.\S+$/.test(uEmail.value)) uEmail.classList.add('invalid');
          return;
        }

        try {
            await simulateApiCall({ status: 'ok' });
            const nu = { ...userData, name: uName.value, email: uEmail.value };
            localStorage.setItem('ge_user', JSON.stringify(nu));
            showToast('Perfil atualizado com sucesso!', 'success');
            el('userName').textContent = nu.name; 
        } catch (error) {
            showToast('Não foi possível salvar o perfil.', 'error');
        }
    });
  } catch (error) {
    showToast('Não foi possível carregar os dados do usuário.', 'error');
  }
}

function reportsInit() {
  const periodSelect = el('reportPeriod'), typeSelect = el('reportType');
  if (!periodSelect) return;
  let reportChartInstance;

  const generateReportChart = async () => {
    try {
      let labels = [], values = [], labelText = "";
      const period = periodSelect.value;
      const type = typeSelect.value;

      // 🔹 Caso: Hoje e Últimos 7 dias → daily-generation
      if (period === "today" || period === "7d") {
        const resp = await fetch("http://127.0.0.1:5000/api/daily-generation");
        const json = await resp.json();
        if (!json.success) throw new Error(json.error || "Erro desconhecido");

        let allDays = json.data.daily_generation;

        if (period === "today") {
          const lastDay = allDays[allDays.length - 1];
          labels = [lastDay.date];
          if (type === "generation") {
            values = [lastDay.generation_kwh];
            labelText = "Geração (kWh)";
          } else if (type === "consumption") {
            values = [lastDay.consumption_kwh || 0];
            labelText = "Consumo (kWh)";
          } else if (type === "savings") {
            values = [lastDay.generation_kwh * 0.75];
            labelText = "Economia (R$)";
          }
        }

        if (period === "7d") {
          const last7 = allDays.slice(-7);
          labels = last7.map(d => d.date);
          if (type === "generation") {
            values = last7.map(d => d.generation_kwh);
            labelText = "Geração (kWh)";
          } else if (type === "consumption") {
            values = last7.map(d => d.consumption_kwh || 0);
            labelText = "Consumo (kWh)";
          } else if (type === "savings") {
            values = last7.map(d => d.generation_kwh * 0.75);
            labelText = "Economia (R$)";
          }
        }
      }

      // 🔹 Caso: Últimos 12 meses → monthly-generation
      if (period === "12m") {
        const resp = await fetch("http://127.0.0.1:5000/api/monthly-generation");
        const json = await resp.json();
        if (!json.success) throw new Error(json.error || "Erro desconhecido");

        let allMonths = json.data.monthly_generation;
        labels = allMonths.map(d => d.month);

        if (type === "generation") {
          values = allMonths.map(d => d.generation_kwh);
          labelText = "Geração (kWh)";
        } else if (type === "consumption") {
          values = allMonths.map(() => 0); // ⚠️ ainda não temos consumo mensal real
          labelText = "Consumo (kWh)";
        } else if (type === "savings") {
          values = allMonths.map(d => d.generation_kwh * 0.75);
          labelText = "Economia (R$)";
        }
      }

      // 🔄 Atualiza o gráfico
      const ctx = el('reportChart');
      if (reportChartInstance) reportChartInstance.destroy();

      reportChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: labelText,
            data: values,
            backgroundColor: 'rgba(59, 130, 246, 0.5)',
            borderColor: '#3b82f6'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              title: { display: true, text: labelText }
            }
          }
        }
      });

    } catch (error) {
      console.error("❌ Erro no relatório:", error);
      showToast('Não foi possível gerar o relatório.', 'error');
    }
  };

  periodSelect.addEventListener('change', generateReportChart);
  typeSelect.addEventListener('change', generateReportChart);
  generateReportChart();
}


async function dashboardInit() {
  console.log("🚀 dashboardInit iniciado");

  try {
    const resp = await fetch("http://127.0.0.1:5000/api/energy");
    console.log("📡 Fetch feito, status:", resp.status);

    const json = await resp.json();
    console.log("🔎 JSON recebido:", json);

    if (!json.success) throw new Error(json.error || "Erro desconhecido");

    const data = json.data;
    const lastDay = data[data.length - 1]; // último dia disponível (simula "hoje")

    const dashData = {
      todayGenKwh: lastDay.generation_kwh,
      todayUseKwh: lastDay.consumption_kwh,
      batteryPct: lastDay.battery_pct,
      savingsBRL: lastDay.generation_kwh * 0.75,
      alerts: [{ type: "success", text: "Dados do dashboard carregados da API!" }],
      history: data.map((d, i) => ({
        h: i,
        gen: d.generation_kwh,
        use: d.consumption_kwh
      }))
    };

    kpiFill(dashData);
    charts(dashData.history, { batteryPct: dashData.batteryPct });
    renderAlerts("alertList", dashData.alerts);
    renderAlerts("popupAlerts", dashData.alerts);

  } catch (error) {
    console.error("❌ Erro no dashboardInit:", error);
    showToast(error.message, "error");
    document.querySelector(".content").innerHTML = `
      <div class="card" style="text-align:center; padding: 40px; grid-column: 1 / -1;">
        <h3>Ops!</h3>
        <p>Não foi possível carregar os dados do dashboard.</p>
      </div>`;
  }
}

function settingsInit() {
    const themeSwitcher = el('themeSwitcher');
    if (themeSwitcher) {
        themeSwitcher.addEventListener('click', (e) => {
            if (e.target.tagName === 'BUTTON') {
                applyTheme(e.target.dataset.theme);
            }
        });
    }
    const saveBtn = document.querySelector('.icon-btn');
    if (saveBtn && saveBtn.textContent.includes('Salvar')) {
        saveBtn.addEventListener('click', async () => {
            try {
                await simulateApiCall({ status: 'ok' }, 500);
                showToast('Preferências salvas!', 'success');
            } catch (error) {
                showToast('Falha ao salvar as preferências.', 'error');
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', ()=>{
  loadTheme();
  const activePage = document.body.dataset.active;
  mountSidebar(activePage);
  
  if (activePage === 'dashboard') dashboardInit();
  if (activePage === 'devices') renderDevices();
  if (activePage === 'login') loginInit();
  if (activePage === 'user') populateUser();
  if (activePage === 'reports') reportsInit();
  if (activePage === 'settings') settingsInit();
});
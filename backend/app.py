# --- IMPORTAÇÕES DE BIBLIOTECAS ---
# Bibliotecas necessárias para o funcionamento do servidor.
from dotenv import load_dotenv  # Carrega variáveis de ambiente de um arquivo .env (como chaves de API)
from flask import Flask, request, jsonify  # O framework web para criar a API
from flask_cors import CORS  # Permite que o frontend (em outro domínio) acesse esta API
import random  # Usado para gerar dados simulados (ex: status da bateria)
import json  # Para manipular arquivos e dados no formato JSON
import os  # Para interagir com o sistema operacional (caminhos de arquivos, etc.)
import pandas as pd  # Biblioteca poderosa para manipulação e análise de dados (arquivos CSV)
from datetime import datetime, timedelta  # Para trabalhar com datas e horas
from werkzeug.security import generate_password_hash, check_password_hash # Para criptografar e verificar senhas de forma segura
import uuid  # Para gerar IDs únicos para os dispositivos
import google.generativeai as genai # SDK do Google para interagir com a API Gemini

# --- CONFIGURAÇÃO INICIAL ---

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configura o cliente da API do Google Gemini com a chave de API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Inicializa o modelo de IA que será usado na aplicação.
# 'gemini-2.0-flash' é um modelo rápido e eficiente para tarefas como chat e resumo.
model = genai.GenerativeModel('gemini-2.0-flash')

# Inicializa a aplicação Flask
app = Flask(__name__)
# Habilita o CORS para toda a aplicação, permitindo requisições do frontend.
CORS(app)

# --- GERENCIAMENTO DE ARQUIVOS E DIRETÓRIOS ---

# Define caminhos de diretório de forma robusta para funcionar em qualquer sistema operacional
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Diretório onde este script (app.py) está.
DATA_DIR = os.path.join(BASE_DIR, '..', 'data') # Aponta para a pasta 'data' que armazena os JSONs.

def find_file_by_pattern(directory, pattern):
    """
    Função auxiliar para encontrar um arquivo em um diretório que contenha um padrão específico no nome.
    Útil para encontrar arquivos de dados que podem ter datas ou outros identificadores no nome.
    Args:
        directory (str): O caminho do diretório onde procurar.
        pattern (str): O texto a ser encontrado no nome do arquivo.
    Returns:
        str: O caminho completo para o primeiro arquivo encontrado, ou None se nenhum for encontrado.
    """
    try:
        # Itera sobre todos os arquivos no diretório especificado
        for filename in os.listdir(directory):
            # Se o padrão for encontrado no nome do arquivo
            if pattern in filename:
                print(f"Arquivo encontrado para o padrão '{pattern}': {filename}")
                return os.path.join(directory, filename)
    except FileNotFoundError:
        print(f"ERRO: O diretório '{directory}' não foi encontrado.")
        return None
    # Se o loop terminar sem encontrar um arquivo
    print(f"AVISO: Nenhum arquivo encontrado para o padrão '{pattern}' em '{directory}'.")
    return None

# Encontra os caminhos dos arquivos de dados dinamicamente
HISTORICAL_DATA_FILE = find_file_by_pattern(BASE_DIR, 'Historical Data Export') # Dados históricos de geração
MONTHLY_DATA_FILE = find_file_by_pattern(BASE_DIR, '2025_Plant') # Relatório mensal de geração

# Define os caminhos para os arquivos JSON que funcionarão como nosso "banco de dados"
USERS_FILE = os.path.join(DATA_DIR, 'users.json') # Armazena dados dos usuários
DEVICES_FILE = os.path.join(DATA_DIR, 'dispositivos.json') # Armazena os dispositivos de cada usuário
CHAT_HISTORY_FILE = os.path.join(DATA_DIR, 'chat_history.json') # Armazena o histórico de chat com o agente

# --- FUNÇÕES AUXILIARES DE MANIPULAÇÃO DE DADOS ---

def read_json_file(filepath, default_data):
    """
    Lê um arquivo JSON de forma segura. Se o arquivo ou diretório não existir, ele os cria.
    Args:
        filepath (str): O caminho completo para o arquivo JSON.
        default_data: O dado padrão a ser escrito no arquivo se ele for criado (ex: {} ou []).
    Returns:
        dict or list: O conteúdo do arquivo JSON.
    """
    # Cria o diretório se ele não existir
    if not os.path.exists(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))
    # Cria o arquivo com o conteúdo padrão se ele não existir
    if not os.path.exists(filepath):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(default_data, f)
        return default_data
    # Se o arquivo já existe, apenas lê e retorna seu conteúdo
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_json_file(filepath, data):
    """
    Escreve dados em um arquivo JSON.
    Args:
        filepath (str): O caminho completo para o arquivo JSON.
        data (dict or list): Os dados a serem escritos no arquivo.
    """
    with open(filepath, 'w', encoding='utf--8') as f:
        # Escreve o JSON de forma formatada (indent=2) e garantindo a codificação correta (ensure_ascii=False)
        json.dump(data, f, indent=2, ensure_ascii=False)

# Variáveis para implementar um sistema de cache simples para os dados do inversor
inverter_data_cache = None # Armazena o dataframe do Pandas em memória
cache_time = None # Armazena o timestamp de quando o cache foi criado

def get_inverter_data():
    """
    Carrega e processa o arquivo CSV com os dados históricos do inversor.
    Implementa um cache de 10 minutos para evitar ler e processar o arquivo repetidamente,
    melhorando muito a performance.
    Returns:
        pandas.DataFrame: Um DataFrame com os dados processados, ou None em caso de erro.
    """
    global inverter_data_cache, cache_time
    # Se o cache existe e tem menos de 10 minutos, retorna os dados da memória
    if inverter_data_cache is not None and cache_time and (datetime.now() - cache_time < timedelta(minutes=10)):
        return inverter_data_cache
    
    # Se o arquivo de dados históricos não foi encontrado, retorna None
    if not HISTORICAL_DATA_FILE: return None

    try:
        # Lê o arquivo CSV. Parâmetros importantes:
        # delimiter=';': O separador de colunas é ponto e vírgula.
        # skiprows=2: Pula as duas primeiras linhas do arquivo (cabeçalhos desnecessários).
        # encoding='latin1': Define a codificação correta para caracteres especiais.
        df = pd.read_csv(HISTORICAL_DATA_FILE, delimiter=';', skiprows=2, encoding='latin1')
        
        # Converte a coluna 'Time' para o formato de data e hora do pandas.
        df['Time'] = pd.to_datetime(df['Time'], format='%d.%m.%Y %H:%M:%S')
        
        # Define as colunas que devem ser numéricas
        numeric_cols = ['Power(W)', 'Total Generation(kWh)']
        for col in numeric_cols:
            # Converte as colunas para número, substituindo vírgulas por pontos.
            # errors='coerce' transforma valores inválidos em NaN (Not a Number).
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
        
        # Remove quaisquer linhas que tenham valores nulos nas colunas numéricas
        df.dropna(subset=numeric_cols, inplace=True)
        
        # Atualiza o cache
        inverter_data_cache = df
        cache_time = datetime.now()
        print("Dados do inversor carregados e processados com sucesso.")
        return df
    except Exception as e:
        print(f"ERRO ao processar o arquivo CSV histórico: {e}")
        return None

# --- ROTAS DA API (ENDPOINTS) ---
# Cada função abaixo corresponde a uma URL da API (ex: /api/register)
# e define o que o servidor deve fazer quando essa URL é acessada.

@app.route('/api/register', methods=['POST'])
def register_user():
    """
    Endpoint para registrar um novo usuário.
    Recebe: JSON com name, email, password.
    Retorna: Os dados do usuário recém-criado ou uma mensagem de erro.
    """
    data = request.get_json()
    name, email, password = data.get('name'), data.get('email'), data.get('password')
    # Validação básica dos dados recebidos
    if not all([name, email, password]): return jsonify({"error": "Todos os campos são obrigatórios"}), 400
    
    users_db = read_json_file(USERS_FILE, {}) # Lê o banco de dados de usuários
    # Verifica se o e-mail já existe
    if email in users_db: return jsonify({"error": "Este e-mail já está cadastrado."}), 409
    
    # Adiciona o novo usuário com valores padrão e senha criptografada
    users_db[email] = {
        "name": name, "email": email, "password": generate_password_hash(password), 
        "plan": "Starter", "theme": "padrão", "colorTheme": "dark", 
        "tariff": 0.95, "savingsGoal": 500, "notifications": "enabled" 
    }
    write_json_file(USERS_FILE, users_db) # Salva as alterações no arquivo
    
    # Prepara os dados do usuário para retornar (sem a senha)
    user_data_to_return = users_db[email].copy()
    del user_data_to_return['password']
    
    return jsonify(user_data_to_return), 201 # 201 Created

@app.route('/api/login', methods=['POST'])
def login_user():
    """
    Endpoint para autenticar um usuário.
    Recebe: JSON com email e password.
    Retorna: Os dados do usuário (sem a senha) ou uma mensagem de erro.
    """
    data = request.get_json()
    email, password = data.get('email'), data.get('password')
    if not email or not password: return jsonify({"error": "E-mail e senha são obrigatórios"}), 400
    
    users_db = read_json_file(USERS_FILE, {})
    user = users_db.get(email)

    # Verifica se o usuário existe e se a senha está correta
    if not user or not user.get('password') or not check_password_hash(user.get('password'), password):
        return jsonify({"error": "Credenciais inválidas."}), 401 # 401 Unauthorized

    # Lógica para garantir que usuários antigos tenham os campos mais novos (compatibilidade)
    needs_update = False
    if 'tariff' not in user:
        user['tariff'] = 0.95
        needs_update = True
    if 'savingsGoal' not in user:
        user['savingsGoal'] = 500
        needs_update = True
    if 'notifications' not in user:
        user['notifications'] = 'enabled'
        needs_update = True

    if needs_update:
        users_db[email] = user
        write_json_file(USERS_FILE, users_db)

    # Prepara os dados para retorno sem a senha
    user_data_to_return = user.copy()
    del user_data_to_return['password']
    return jsonify(user_data_to_return)

@app.route('/api/user/theme', methods=['PUT'])
def save_theme():
    """
    Endpoint para salvar as preferências de tema do usuário.
    Recebe: JSON com email, e opcionalmente theme e colorTheme.
    Retorna: Mensagem de sucesso ou erro.
    """
    data = request.get_json()
    email, theme, colorTheme = data.get('email'), data.get('theme'), data.get('colorTheme')
    if not email or (theme is None and colorTheme is None):
        return jsonify({"error": "Faltam informações para salvar o tema."}), 400
    users_db = read_json_file(USERS_FILE, {})
    if email in users_db:
        if theme is not None: users_db[email]['theme'] = theme
        if colorTheme is not None: users_db[email]['colorTheme'] = colorTheme
        write_json_file(USERS_FILE, users_db)
        return jsonify({"message": "Tema salvo com sucesso!"})
    return jsonify({"error": "Usuário não encontrado."}), 404 # 404 Not Found

@app.route('/api/kpis', methods=['GET'])
def get_kpis():
    """
    Endpoint para obter os principais indicadores (KPIs) para o dashboard.
    Recebe: 'email' como parâmetro na URL (query parameter).
    Retorna: JSON com dados como geração de hoje, geração total, consumo da casa e economia do mês.
    """
    user_email = request.args.get('email')
    if not user_email: return jsonify({"error": "E-mail do usuário é necessário"}), 400

    df = get_inverter_data() # Carrega os dados (do cache, se disponível)
    if df is None or df.empty: return jsonify({"error": "Não foi possível carregar os dados do inversor"}), 500
    
    users_db = read_json_file(USERS_FILE, {})
    user_tariff = users_db.get(user_email, {}).get('tariff', 0.95) # Pega a tarifa do usuário ou usa um padrão

    # Calcula a geração de hoje
    latest_date_in_data = df['Time'].max().date() # Encontra a data mais recente nos dados
    today_data = df[df['Time'].dt.date == latest_date_in_data]
    generation_today = 0
    if not today_data.empty:
        # Geração do dia é a diferença entre o máximo e o mínimo da geração acumulada naquele dia
        generation_today = today_data['Total Generation(kWh)'].max() - today_data['Total Generation(kWh)'].min()
    
    # Geração total (acumulada desde o início)
    total_generation = df['Total Generation(kWh)'].max()
    # Consumo da casa é simulado com um valor aleatório para fins de demonstração
    house_load_kwh = 0.53

    # Calcula a economia do mês atual
    savings_this_month = 0
    now = datetime.now()
    month_data = df[(df['Time'].dt.month == now.month) & (df['Time'].dt.year == now.year)]
    if not month_data.empty:
        generation_this_month = month_data['Total Generation(kWh)'].max() - month_data['Total Generation(kWh)'].min()
        savings_this_month = generation_this_month * user_tariff

    return jsonify({
        "todayGenKwh": generation_today, 
        "totalGenKwh": total_generation,
        "houseLoadKwh": house_load_kwh,
        "savingsThisMonth": savings_this_month
    })

@app.route('/api/generation/history', methods=['GET'])
def get_generation_history():
    """
    Endpoint para o gráfico de histórico de geração do dia.
    Retorna: Dados de geração de energia (kW) por hora para o dia mais recente disponível nos dados.
    """
    df = get_inverter_data()
    if df is None or df.empty: 
        return jsonify({"error": "Não foi possível carregar os dados do inversor"}), 500

    # Pega os dados das últimas 24h a partir da data mais recente
    latest_date = df['Time'].max().date()
    start_time = datetime.combine(latest_date, datetime.min.time()).replace(hour=1)
    end_time = start_time + timedelta(hours=24)
    recent_data = df[(df['Time'] >= start_time) & (df['Time'] < end_time)].copy()
    
    recent_data.set_index('Time', inplace=True)
    # Reamostra os dados de potência (W) por hora, calculando a média
    hourly_generation = recent_data['Power(W)'].resample('h').mean().fillna(0)

    # Garante que temos 24 pontos no gráfico, um para cada hora, preenchendo com 0 se não houver dados
    full_period_index = pd.date_range(start=start_time, periods=24, freq='h')
    hourly_generation = hourly_generation.reindex(full_period_index, fill_value=0)

    return jsonify({
        "labels": hourly_generation.index.strftime('%Hh').tolist(), # Labels para o eixo X (ex: "01h", "02h")
        "generation_kw": (hourly_generation / 1000).round(2).tolist() # Dados para o eixo Y, convertidos para kW
    })

@app.route('/api/reports/monthly', methods=['GET'])
def get_monthly_report():
    """
    Endpoint para o relatório de geração mensal.
    Processa um arquivo CSV específico para relatórios mensais.
    Retorna: Uma lista de objetos, cada um com 'date' e 'generation'.
    """
    if not MONTHLY_DATA_FILE: return jsonify({"error": "Arquivo de relatório mensal não configurado."}), 500
    try:
        # Lê o arquivo de relatório, pulando cabeçalho e rodapé
        df = pd.read_csv(MONTHLY_DATA_FILE, delimiter=';', skiprows=20, encoding='latin1', skipfooter=1, engine='python')
        df.rename(columns={'Generation(kWh)': 'generation', 'Date': 'date'}, inplace=True)
        df['generation'] = pd.to_numeric(df['generation'].astype(str).str.replace(',', '.'), errors='coerce')
        df.dropna(subset=['date', 'generation'], inplace=True)
        report_data = df[['date', 'generation']].to_dict(orient='records')
        return jsonify(report_data)
    except Exception as e:
        return jsonify({"error": f"Erro ao processar arquivo de relatório: {e}"}), 500

@app.route('/api/devices', methods=['GET'])
def get_devices():
    """
    Endpoint para listar os dispositivos de um usuário.
    Recebe: 'email' como query parameter.
    Retorna: Lista de dispositivos do usuário, com o custo por hora já calculado.
    """
    user_email = request.args.get('email')
    if not user_email: return jsonify({"error": "E-mail do usuário é necessário"}), 400
    
    devices_db = read_json_file(DEVICES_FILE, {})
    users_db = read_json_file(USERS_FILE, {})
    user_devices = devices_db.get(user_email, [])
    user_tariff = users_db.get(user_email, {}).get('tariff', 0.95)
    
    # Calcula o custo por hora para cada dispositivo antes de enviar para o frontend
    for device in user_devices:
        cost_per_hour = (device.get('watts', 0) / 1000) * user_tariff
        device['cost_per_hour'] = f"R$ {cost_per_hour:.2f}"

    return jsonify(user_devices)

@app.route('/api/devices', methods=['POST'])
def add_device():
    """
    Endpoint para adicionar um novo dispositivo.
    Recebe: JSON com email, name, room, type.
    Retorna: O objeto do novo dispositivo criado.
    """
    data = request.get_json()
    user_email, name, room, type = data.get('email'), data.get('name'), data.get('room'), data.get('type')
    if not all([user_email, name, room, type]): return jsonify({"error": "Todos os campos são obrigatórios"}), 400
    devices_db = read_json_file(DEVICES_FILE, {})
    user_devices = devices_db.get(user_email, [])
    # Cria o novo dispositivo com um ID único
    new_device = {"id": str(uuid.uuid4()), "name": name, "room": room, "type": type, "on": False, "watts": 0}
    new_device['cost_per_hour'] = "R$ 0.00"
    user_devices.append(new_device)
    devices_db[user_email] = user_devices
    write_json_file(DEVICES_FILE, devices_db)
    return jsonify(new_device), 201

@app.route('/api/devices/<string:device_id>', methods=['PUT'])
def toggle_device(device_id):
    """
    Endpoint para ligar ou desligar um dispositivo.
    Recebe: 'device_id' na URL, e JSON com 'email' e 'on' (true/false).
    Retorna: Mensagem de sucesso ou erro.
    """
    data = request.get_json()
    user_email, new_state = data.get('email'), data.get('on')
    if not user_email or new_state is None: return jsonify({"error": "Faltam dados para atualizar o dispositivo"}), 400
    devices_db = read_json_file(DEVICES_FILE, {})
    user_devices = devices_db.get(user_email, [])
    device_found = False
    for device in user_devices:
        if device['id'] == device_id:
            device['on'] = new_state
            # Atribui uma potência (watts) simulada baseada no tipo e estado do dispositivo
            device['watts'] = device['on'] * (200 if device['type'] == 'appliance' else 900 if device['type'] == 'climate' else 60)
            device_found = True
            break
    if not device_found: return jsonify({"error": "Dispositivo não encontrado"}), 404
    devices_db[user_email] = user_devices
    write_json_file(DEVICES_FILE, devices_db)
    return jsonify({"message": "Dispositivo atualizado"})

@app.route('/api/devices/<string:device_id>', methods=['DELETE'])
def delete_device(device_id):
    """
    Endpoint para remover um dispositivo.
    Recebe: 'device_id' na URL e 'email' como query parameter.
    Retorna: Mensagem de sucesso ou erro.
    """
    user_email = request.args.get('email')
    if not user_email: return jsonify({"error": "E-mail do usuário é necessário"}), 400
    devices_db = read_json_file(DEVICES_FILE, {})
    user_devices = devices_db.get(user_email, [])
    initial_len = len(user_devices)
    # Recria a lista de dispositivos, excluindo aquele com o ID correspondente
    user_devices = [d for d in user_devices if d['id'] != device_id]
    if len(user_devices) == initial_len: return jsonify({"error": "Dispositivo não encontrado"}), 404
    devices_db[user_email] = user_devices
    write_json_file(DEVICES_FILE, devices_db)
    return jsonify({"message": "Dispositivo removido"})

@app.route('/api/user', methods=['DELETE'])
def delete_user():
    """
    Endpoint para excluir a conta de um usuário e todos os seus dados.
    Recebe: JSON com email e password para confirmação.
    Retorna: Mensagem de sucesso ou erro.
    """
    data = request.get_json()
    email, password = data.get('email'), data.get('password')
    if not email or not password:
        return jsonify({"error": "E-mail e senha são obrigatórios para exclusão"}), 400
    users_db = read_json_file(USERS_FILE, {})
    devices_db = read_json_file(DEVICES_FILE, {})
    user = users_db.get(email)
    # Confirma a senha antes de excluir
    if not user or not check_password_hash(user.get('password'), password):
        return jsonify({"error": "Credenciais inválidas."}), 401
    try:
        # Remove o usuário do 'banco de dados' de usuários
        del users_db[email]
        write_json_file(USERS_FILE, users_db)
        # Remove também todos os dispositivos associados a esse usuário
        if email in devices_db:
            del devices_db[email]
            write_json_file(DEVICES_FILE, devices_db)
        return jsonify({"message": "Usuário e todos os seus dados foram removidos com sucesso."}), 200
    except Exception as e:
        return jsonify({"error": f"Ocorreu um erro ao remover o usuário: {e}"}), 500

@app.route('/api/battery/status', methods=['GET'])
def get_battery_status():
    """
    Endpoint para obter o status da bateria (simulado).
    Retorna: Dados simulados como porcentagem de carga, fluxo de energia e status.
    """
    try:
        # Define valores fixos para o estado da bateria.
        charged_percentage = 37  # Porcentagem de carga fixa
        empty_percentage = 100.0 - charged_percentage
        fluxo_watts = 1250  # Fluxo de energia fixo em Watts (positivo = carregando)
        status_texto = "Carregando"  # Status fixo

        # Calcula a energia armazenada com base na capacidade total.
        capacidade_total_kwh = 13.5
        energia_armazenada_kwh = round((charged_percentage / 100) * capacidade_total_kwh, 1)

        # Monta o objeto de dados da bateria com os valores fixos.
        battery_data = {
            "charged_percentage": charged_percentage,
            "empty_percentage": empty_percentage,
            "labels": ["Carga", "Vazio"],
            "fluxo_watts": fluxo_watts,
            "status_texto": status_texto,
            'energia_kwh': energia_armazenada_kwh
        }
        return jsonify(battery_data)
    except Exception as e:
        return jsonify({"error": f"Erro ao obter dados da bateria: {e}"}), 500

@app.route('/api/ask-agent', methods=['POST'])
def ask_agent():
    """
    Endpoint principal de interação com o agente de IA (Gemini).
    Recebe: JSON com a 'question' e o 'email' do usuário.
    Processa a pergunta:
    - Se for um comando para controlar um dispositivo, a IA retorna um JSON específico.
      O backend executa o comando e retorna uma confirmação.
    - Se for qualquer outra pergunta, a IA responde em texto (Markdown), e o backend
      repassa essa resposta para o frontend.
    """
    try:
        data = request.get_json()
        question = data.get("question", "")
        user_email = data.get("email", "")
        if not question or not user_email:
            return jsonify({"error": "Pergunta e e-mail são obrigatórios"}), 400

        # Fornece à IA o contexto dos dispositivos que o usuário possui
        devices_db = read_json_file(DEVICES_FILE, {})
        user_devices = devices_db.get(user_email, [])
        device_names = [d['name'] for d in user_devices]
        
        # O "prompt" é a instrução que damos à IA.
        # Ele define o comportamento esperado e fornece os dados necessários.
        prompt = f"""Você é um assistente de casa inteligente. Analise o pedido do usuário. Os dispositivos disponíveis são: {', '.join(device_names)}.
                - Se o pedido for um comando para ligar, desligar, acender ou apagar um dispositivo, responda APENAS com um JSON no formato: {{"command": true, "device_name": "nome do dispositivo", "action": "on" ou "off"}}
                - Se for qualquer outra pergunta, responda normalmente em Markdown.

                Pedido do usuário: "{question}"
                """
        response = model.generate_content(prompt)
        # Limpa a resposta da IA para remover formatação indesejada
        response_text = response.text.strip().replace('```json', '').replace('```', '')

        try:
            # Tenta interpretar a resposta da IA como um JSON de comando
            potential_command = json.loads(response_text)
            if isinstance(potential_command, dict) and potential_command.get("command"):
                device_name = potential_command.get("device_name")
                action = potential_command.get("action")
                
                # Procura o dispositivo mencionado na lista de dispositivos do usuário
                target_device = next((d for d in user_devices if d['name'].lower() == device_name.lower()), None)

                if not target_device:
                    return jsonify({"answer": f"Não encontrei um dispositivo chamado '{device_name}'."})
                
                # Executa a ação (liga/desliga)
                new_state = (action == 'on')
                target_device['on'] = new_state
                target_device['watts'] = new_state * (200 if target_device['type'] == 'appliance' else 900 if target_device['type'] == 'climate' else 60)
                
                devices_db[user_email] = user_devices
                write_json_file(DEVICES_FILE, devices_db)

                action_text = "ligado" if new_state else "desligado"
                return jsonify({"answer": f"Ok, dispositivo '{target_device['name']}' foi {action_text}."})

        except (json.JSONDecodeError, TypeError):
            # Se a resposta não for um JSON de comando, a trata como uma resposta de texto normal.
            return jsonify({"answer": response_text})

    except Exception as e:
        print(f"\n--- ERRO DETALHADO DA API (GEMINI) --- \n{e}\n----------------------------------\n")
        return jsonify({"error": f"Erro do agente: {e}"}), 500

@app.route('/api/user/profile', methods=['PUT'])
def update_user_profile():
    """
    Endpoint para atualizar o nome do usuário.
    Recebe: JSON com email e o novo 'name'.
    Retorna: Os dados atualizados do usuário.
    """
    data = request.get_json()
    email, new_name = data.get('email'), data.get('name')
    if not email or not new_name:
        return jsonify({"error": "E-mail e novo nome são obrigatórios"}), 400
    users_db = read_json_file(USERS_FILE, {})
    if email in users_db:
        users_db[email]['name'] = new_name
        write_json_file(USERS_FILE, users_db)
        updated_user = users_db[email].copy()
        del updated_user['password'] # Nunca retorna a senha
        return jsonify(updated_user)
    return jsonify({"error": "Usuário não encontrado."}), 404

@app.route('/api/user/preferences', methods=['PUT'])
def save_preferences():
    """
    Endpoint para salvar as preferências do usuário (tarifa, meta de economia, etc.).
    Recebe: JSON com email e os campos a serem atualizados.
    Retorna: Os dados atualizados do usuário.
    """
    data = request.get_json()
    email = data.get('email')
    tariff = data.get('tariff')
    savings_goal = data.get('savingsGoal')
    notifications = data.get('notifications')

    if not email: return jsonify({"error": "Email é obrigatório"}), 400

    users_db = read_json_file(USERS_FILE, {})
    if email in users_db:
        try:
            # Atualiza apenas os campos que foram enviados
            if tariff is not None:
                users_db[email]['tariff'] = float(tariff)
            if savings_goal is not None:
                users_db[email]['savingsGoal'] = int(savings_goal)
            if notifications is not None:
                users_db[email]['notifications'] = notifications
            write_json_file(USERS_FILE, users_db)
            
            updated_user = users_db[email].copy()
            del updated_user['password']
            return jsonify(updated_user)
        except (ValueError, TypeError):
            return jsonify({"error": "Preferências devem ser válidas."}), 400
    
    return jsonify({"error": "Usuário não encontrado."}), 404

@app.route('/api/optimizer/suggest-time', methods=['POST'])
def suggest_optimal_time():
    """
    Endpoint do otimizador de tarefas. Usa IA para sugerir o melhor horário
    para executar uma tarefa de alto consumo.
    Combina dados de previsão do tempo (externo) e histórico de geração (interno)
    para tomar a decisão.
    Recebe: JSON com 'task' (descrição da tarefa) e 'email'.
    Retorna: JSON com 'horario_recomendado' e 'justificativa'.
    """
    data = request.get_json()
    task_info, user_email = data.get('task'), data.get('email')
    if not task_info or not user_email:
        return jsonify({"error": "Informações da tarefa e email são obrigatórios"}), 400
    try:
        # --- Parte 1: Coleta de dados externos (Previsão do Tempo) ---
        # NOTA: O ideal é não expor a chave de API no código. Aqui está para simplificar.
        import requests
        api_key, lat, lon = '2d1f3910b6139ba59b1385427c34b64e', -23.5614, -46.6565 # São Paulo
        forecast_url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=current,minutely,daily,alerts&appid={api_key}&units=metric"
        forecast_data = requests.get(forecast_url).json()
        
        # Formata a previsão de nebulosidade para ser fácil para a IA entender
        hourly_forecast = "".join([f"- {datetime.fromtimestamp(h['dt']).strftime('%H:%M')}: Nebulosidade de {h['clouds']}%\n" for h in forecast_data['hourly'][:24]])

        # --- Parte 2: Coleta de dados internos (Histórico de Geração) ---
        df = get_inverter_data()
        df.set_index('Time', inplace=True)
        # Calcula a média de geração de energia para cada hora do dia
        average_generation_by_hour = df['Power(W)'].groupby(df.index.hour).mean()
        historical_pattern = "".join([f"- {hour:02d}h: Média de {avg_power:.0f} W\n" for hour, avg_power in average_generation_by_hour.items()])

        # --- Parte 3: Envio para a IA ---
        # O prompt combina os dados coletados e instrui a IA sobre como analisar e o formato da resposta.
        prompt = f"""Você é um especialista em otimização de energia. Seu objetivo é encontrar a melhor janela de 2 horas nas próximas 24 horas para executar uma tarefa de alto consumo ('{task_info}').
Use os seguintes dados para tomar sua decisão:
1. PREVISÃO DE TEMPO (próximas 24h):
{hourly_forecast}
2. PADRÃO DE GERAÇÃO HISTÓRICO (média de geração por hora):
{historical_pattern}
Analise a previsão de nebulosidade e o histórico de geração. A melhor janela de tempo é aquela com a MENOR nebulosidade prevista e que coincide com o MAIOR pico de geração histórica.
Responda APENAS com um JSON no seguinte formato:
{{"horario_recomendado": "HH:00", "justificativa": "Uma frase curta explicando o porquê."}}"""

        response = model.generate_content(prompt)
        response_text = response.text.strip().replace('```json', '').replace('```', '')
        suggestion = json.loads(response_text)
        return jsonify(suggestion)

    except Exception as e:
        print(f"ERRO no otimizador: {e}")
        # Resposta de fallback caso a API ou a IA falhem
        return jsonify({"horario_recomendado": "13:00", "justificativa": "O período da tarde geralmente oferece a melhor geração solar."})

@app.route('/api/reports/insights', methods=['GET'])
def get_report_insights():
    """
    Endpoint que usa a IA para gerar um resumo amigável (insights)
    com base nos dados de geração do último mês do usuário.
    Recebe: 'email' como query parameter.
    Retorna: Um texto em Markdown com os insights.
    """
    user_email = request.args.get('email')
    if not user_email: return jsonify({"error": "Email do usuário é obrigatório"}), 400
    try:
        df = get_inverter_data()
        if df is None or df.empty: return jsonify({"insights": "Não há dados suficientes para gerar uma análise."})

        # Filtra os dados dos últimos 30 dias
        end_date = df['Time'].max()
        start_date = end_date - timedelta(days=30)
        last_month_data = df[(df['Time'] >= start_date) & (df['Time'] <= end_date)]
        if last_month_data.empty: return jsonify({"insights": "Não há dados do último mês para gerar uma análise."})

        # Calcula as métricas chave
        generation_last_month = last_month_data['Total Generation(kWh)'].max() - last_month_data['Total Generation(kWh)'].min()
        daily_generation = last_month_data.set_index('Time').resample('D')['Total Generation(kWh)'].apply(lambda x: x.max() - x.min())
        peak_day = daily_generation.idxmax().strftime('%d de %B')
        peak_day_generation = daily_generation.max()

        devices_db = read_json_file(DEVICES_FILE, {})
        user_devices = devices_db.get(user_email, [])
        top_consumer_device = user_devices[0]['name'] if user_devices else "Nenhum dispositivo" # Simulação simples

        # Cria o prompt com as métricas calculadas e a estrutura de resposta desejada
        prompt = f"""Você é um analista de dados especialista em energia solar. Com base nas seguintes métricas dos últimos 30 dias de um cliente, escreva um resumo em 3 bullets. Use tom amigável, emojis e negrito.
Métricas:
- Geração total: {generation_last_month:.2f} kWh
- Dia de pico: {peak_day}, com {peak_day_generation:.2f} kWh.
- Dispositivo usado: {top_consumer_device}
Estrutura:
- Bullet 1 (Elogio): Parabenize pela geração total e dia de pico.
- Bullet 2 (Atenção): Dê uma dica sobre o consumo do dispositivo.
- Bullet 3 (Recomendação): Recomendação geral para maximizar economia."""

        response = model.generate_content(prompt)
        return jsonify({"insights": response.text})

    except Exception as e:
        print(f"ERRO ao gerar insights: {e}")
        return jsonify({"error": "Não foi possível gerar a análise no momento."}), 500

@app.route('/api/dashboard-insights', methods=['GET'])
def get_dashboard_insights():
    """
    Endpoint que gera 3 insights rápidos (elogio, alerta, dica) para o dashboard principal.
    Usa dados em tempo real (KPIs, status da bateria) para gerar as dicas.
    Recebe: 'email' como query parameter.
    Retorna: Uma lista de objetos JSON, cada um representando um insight.
    """
    user_email = request.args.get('email')
    if not user_email: return jsonify([]), 400
    try:
        # Obtém os dados mais recentes chamando as próprias funções da API
        # NOTA: Isso pode ser otimizado para não fazer requisições internas,
        # mas para este escopo, simplifica a lógica.
        kpis_data = get_kpis().get_json()
        battery_data = get_battery_status().get_json()

        # O prompt instrui a IA a analisar os dados e retornar um JSON com uma estrutura exata.
        prompt = f"""Você é um analista de dados de energia. Analise os dados do usuário e gere uma lista de 3 insights (elogio, alerta, dica).
Dados:
- Geração hoje: {kpis_data.get('todayGenKwh', 0):.2f} kWh
- Consumo atual: {kpis_data.get('houseLoadKw', 0):.2f} kW
- Bateria: {battery_data.get('charged_percentage', 0)}% e {battery_data.get('status_texto')}
- Economia do mês: R$ {kpis_data.get('savingsThisMonth', 0):.2f}
Sua resposta DEVE SER APENAS um array JSON válido. Cada objeto deve ter as chaves "type" ("elogio", "alerta", "dica") e "text".
Exemplo de Resposta:
[
    {{"type": "elogio", "text": "🌞 Parabéns! Sua geração hoje está excelente!"}},
    {{"type": "alerta", "text": "⚠️ Atenção: seu consumo atual está um pouco alto."}},
    {{"type": "dica", "text": "💡 Dica: Com a bateria em {battery_data.get('charged_percentage', 0)}%, é um bom momento para usar aparelhos de alto consumo."}}
]"""
        
        response = model.generate_content(prompt)
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '')
        insights = json.loads(cleaned_response)
        return jsonify(insights)

    except Exception as e:
        print(f"ERRO ao gerar insights para o stack: {e}")
        # Fallback para garantir que o frontend sempre receba algo
        fallback_insights = [
            {"type": "dica", "text": "💡 Use seus aparelhos de maior consumo durante o dia para aproveitar a energia solar gratuita."},
            {"type": "elogio", "text": "🌞 Continue acompanhando seus dados para maximizar sua economia de energia!"},
            {"type": "alerta", "text": "⚠️ Lembre-se de verificar a limpeza dos seus painéis solares periodicamente."}
        ]
        return jsonify(fallback_insights)
    
@app.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    """
    Endpoint para carregar o histórico de conversas do usuário com o agente.
    Recebe: 'email' como query parameter.
    Retorna: O histórico de chat salvo para aquele usuário.
    """
    user_email = request.args.get('email')
    if not user_email:
        return jsonify({"error": "Email do usuário é obrigatório"}), 400
    all_histories = read_json_file(CHAT_HISTORY_FILE, {})
    user_history = all_histories.get(user_email, {})
    return jsonify(user_history)

@app.route('/api/chat/history', methods=['POST'])
def save_chat_history():
    """
    Endpoint para salvar o histórico de conversas do usuário.
    Recebe: JSON com 'email' e 'conversations'.
    Retorna: Mensagem de sucesso.
    """
    data = request.get_json()
    user_email = data.get('email')
    conversations = data.get('conversations')
    if not user_email or conversations is None:
        return jsonify({"error": "Email e histórico são obrigatórios"}), 400
    all_histories = read_json_file(CHAT_HISTORY_FILE, {})
    all_histories[user_email] = conversations
    write_json_file(CHAT_HISTORY_FILE, all_histories)
    return jsonify({"message": "Histórico salvo com sucesso."})

# --- EXECUÇÃO DA APLICAÇÃO ---

# Este bloco só será executado se o script `app.py` for rodado diretamente.
# Não será executado se for importado por outro script.
if __name__ == '__main__':
    # Inicia o servidor de desenvolvimento do Flask.
    # debug=True: Ativa o modo de depuração, que reinicia o servidor automaticamente
    #             a cada alteração no código e mostra erros detalhados no navegador.
    # port=5000: Define a porta em que o servidor irá rodar.
    app.run(debug=True, port=5000)
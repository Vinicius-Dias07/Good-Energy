# --- IMPORTAÇÃO DAS BIBLIOTECAS NECESSÁRIAS ---
# Importa as classes e funções principais do Flask para criar e gerenciar a aplicação web.
import google.generativeai as genai
from flask import Response
from dotenv import load_dotenv
from flask import Flask, request, jsonify
# Importa a extensão Flask-CORS para permitir que o frontend (em outra porta) acesse esta API.
from flask_cors import CORS
# Importa a biblioteca 'random' para gerar números aleatórios (usada para simular dados).
import random
# Importa a biblioteca 'json' para ler e escrever em arquivos no formato JSON.
import json
# Importa a biblioteca 'os' para interagir com o sistema operacional (manipular caminhos de arquivos).
import os
# Importa a biblioteca 'pandas' para análise e manipulação de dados, especialmente para ler arquivos CSV.
import pandas as pd
# Importa 'datetime' e 'timedelta' para trabalhar com datas e horas.
from datetime import datetime, timedelta
# Importa funções de segurança para criar e verificar hashes de senhas.
from werkzeug.security import generate_password_hash, check_password_hash
# Importa a biblioteca 'uuid' para gerar IDs únicos para os dispositivos.
import uuid

# Carrega as variáveis de ambiente do arquivo .env (como a chave da API do Gemini).
load_dotenv()
# Configura a biblioteca do Google AI com a chave da API carregada do .env.
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# --- CONFIGURAÇÃO INICIAL DA APLICAÇÃO ---
# Cria a instância principal da aplicação Flask.
app = Flask(__name__)
# Habilita o CORS para toda a aplicação, permitindo requisições de outras origens.
CORS(app)

# --- CAMINHOS PARA OS ARQUIVOS DE DADOS ---
# Define o diretório base como o local onde este script (app.py) está.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Define o diretório de dados (assumindo que está um nível acima da pasta do backend).
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')

# Função para encontrar arquivos de dados dinamicamente, buscando por um padrão no nome.
def find_file_by_pattern(directory, pattern):
    try:
        # Percorre todos os arquivos no diretório especificado.
        for filename in os.listdir(directory):
            # Se o padrão de texto for encontrado no nome do arquivo...
            if pattern in filename:
                # ...imprime para depuração e retorna o caminho completo.
                print(f"Arquivo encontrado para o padrão '{pattern}': {filename}")
                return os.path.join(directory, filename)
    # Trata o erro caso o diretório não exista.
    except FileNotFoundError:
        print(f"ERRO: O diretório '{directory}' não foi encontrado.")
        return None
    # Avisa se nenhum arquivo com o padrão foi encontrado.
    print(f"AVISO: Nenhum arquivo encontrado para o padrão '{pattern}' em '{directory}'.")
    return None

# Caminhos completos para os arquivos que serão usados como "banco de dados".
HISTORICAL_DATA_FILE = find_file_by_pattern(BASE_DIR, 'Historical Data Export')
MONTHLY_DATA_FILE = find_file_by_pattern(BASE_DIR, '2025_Plant')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
DEVICES_FILE = os.path.join(DATA_DIR, 'dispositivos.json')
CHAT_HISTORY_FILE = os.path.join(DATA_DIR, 'chat_history.json')

# --- FUNÇÕES AUXILIARES ---

# Lê um arquivo JSON de forma segura. Se o arquivo ou diretório não existir, ele os cria.
def read_json_file(filepath, default_data):
    # Se o diretório do arquivo não existe, cria o diretório.
    if not os.path.exists(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))
    # Se o arquivo não existe, cria-o com os dados padrão.
    if not os.path.exists(filepath):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(default_data, f)
        return default_data
    # Se o arquivo já existe, lê e retorna seu conteúdo.
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

# Escreve (ou sobrescreve) dados em um arquivo JSON de forma organizada e legível.
def write_json_file(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        # 'indent=2' formata o JSON para facilitar a leitura.
        json.dump(data, f, indent=2, ensure_ascii=False)

# Cache em memória para os dados do inversor, para evitar ler o CSV repetidamente.
inverter_data_cache = None
cache_time = None

# Função para carregar e processar os dados do inversor a partir do arquivo CSV.
def get_inverter_data():
    # Declara que vamos usar as variáveis globais de cache.
    global inverter_data_cache, cache_time
    # Se o cache for recente (menos de 10 min), usa os dados da memória para performance.
    if inverter_data_cache is not None and cache_time and (datetime.now() - cache_time < timedelta(minutes=10)):
        return inverter_data_cache
    # Se o arquivo de dados não foi encontrado, retorna None.
    if not HISTORICAL_DATA_FILE: return None
    try:
        # Usa a biblioteca pandas para ler e limpar o CSV.
        df = pd.read_csv(HISTORICAL_DATA_FILE, delimiter=';', skiprows=2, encoding='latin1')
        # Converte a coluna de tempo para um formato de data/hora utilizável.
        df['Time'] = pd.to_datetime(df['Time'], format='%d.%m.%Y %H:%M:%S')
        # Define quais colunas devem ser numéricas.
        numeric_cols = ['Power(W)', 'Total Generation(kWh)']
        # Converte as colunas para o formato numérico, trocando vírgula por ponto.
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
        # Remove linhas com dados inválidos.
        df.dropna(subset=numeric_cols, inplace=True)
        # Atualiza o cache com os dados limpos e o horário da atualização.
        inverter_data_cache = df
        cache_time = datetime.now()
        print("Dados do inversor carregados e processados com sucesso.")
        return df
    except Exception as e:
        print(f"ERRO ao processar o arquivo CSV histórico: {e}")
        return None

# --- ROTAS DE API (ENDPOINTS) ---

# Rota para registrar um novo usuário. Aceita apenas requisições POST.
@app.route('/api/register', methods=['POST'])
def register_user():
    # Pega os dados JSON enviados pelo frontend.
    data = request.get_json()
    # Extrai os campos do JSON.
    name, email, password = data.get('name'), data.get('email'), data.get('password')
    # Valida se todos os campos necessários foram enviados.
    if not all([name, email, password]): return jsonify({"error": "Todos os campos são obrigatórios"}), 400
    # Lê o "banco de dados" de usuários.
    users_db = read_json_file(USERS_FILE, {})
    # Verifica se o email já está em uso.
    if email in users_db: return jsonify({"error": "Este e-mail já está cadastrado."}), 409
    
    # Cria o novo usuário com todas as preferências padrão.
    users_db[email] = {
        "name": name, "email": email, "password": generate_password_hash(password), 
        "plan": "Starter", "theme": "padrão", "colorTheme": "dark", 
        "tariff": 0.95, "savingsGoal": 500, "notifications": "enabled" 
    }
    
    # Salva o banco de dados atualizado.
    write_json_file(USERS_FILE, users_db)
    # Prepara os dados do usuário para retornar (sem a senha).
    user_data_to_return = users_db[email].copy()
    del user_data_to_return['password']
    # Retorna o novo usuário criado com o status 201 (Created).
    return jsonify(user_data_to_return), 201

# Rota para autenticar (logar) um usuário.
@app.route('/api/login', methods=['POST'])
def login_user():
    # Pega os dados JSON da requisição.
    data = request.get_json()
    # Extrai email e senha.
    email, password = data.get('email'), data.get('password')
    # Valida os dados.
    if not email or not password: return jsonify({"error": "E-mail e senha são obrigatórios"}), 400
    
    # Lê o banco de dados.
    users_db = read_json_file(USERS_FILE, {})
    # Busca o usuário pelo email.
    user = users_db.get(email)

    # Verifica se o usuário existe e se a senha está correta, comparando o hash.
    if not user or not user.get('password') or not check_password_hash(user.get('password'), password):
        return jsonify({"error": "Credenciais inválidas."}), 401

    # LÓGICA DE MIGRAÇÃO: Atualiza perfis de usuários antigos que não têm as novas chaves.
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

    # Se alguma chave foi adicionada, salva o arquivo de volta.
    if needs_update:
        users_db[email] = user
        write_json_file(USERS_FILE, users_db)

    # Prepara os dados para retornar (sem a senha).
    user_data_to_return = user.copy()
    del user_data_to_return['password']
    # Retorna os dados do usuário logado.
    return jsonify(user_data_to_return)

# Rota para salvar as preferências de tema (cores e modo claro/escuro).
@app.route('/api/user/theme', methods=['PUT'])
def save_theme():
    # Pega os dados da requisição.
    data = request.get_json()
    email, theme, colorTheme = data.get('email'), data.get('theme'), data.get('colorTheme')
    # Valida se os dados necessários foram enviados.
    if not email or (theme is None and colorTheme is None):
        return jsonify({"error": "Faltam informações para salvar o tema."}), 400
    # Lê o banco de dados.
    users_db = read_json_file(USERS_FILE, {})
    # Se o usuário existir, atualiza suas preferências de tema.
    if email in users_db:
        if theme is not None: users_db[email]['theme'] = theme
        if colorTheme is not None: users_db[email]['colorTheme'] = colorTheme
        # Salva as alterações.
        write_json_file(USERS_FILE, users_db)
        return jsonify({"message": "Tema salvo com sucesso!"})
    # Retorna erro se o usuário não for encontrado.
    return jsonify({"error": "Usuário não encontrado."}), 404

# Rota para obter os KPIs (Key Performance Indicators) do dashboard.
@app.route('/api/kpis', methods=['GET'])
def get_kpis():
    user_email = request.args.get('email')
    if not user_email: return jsonify({"error": "E-mail do usuário é necessário"}), 400

    df = get_inverter_data()
    if df is None or df.empty: return jsonify({"error": "Não foi possível carregar os dados do inversor"}), 500
    
    users_db = read_json_file(USERS_FILE, {})
    user_tariff = users_db.get(user_email, {}).get('tariff', 0.95)

    # --- LÓGICA CORRIGIDA PARA USAR A ÚLTIMA DATA DO ARQUIVO ---
    # Encontra a data mais recente presente no arquivo de dados.
    latest_date_in_data = df['Time'].max().date()

    # Filtra o DataFrame para obter apenas os dados desse último dia.
    today_data = df[df['Time'].dt.date == latest_date_in_data]
    # --- FIM DA LÓGICA CORRIGIDA ---

    # Calcula a geração de "hoje" (baseado no último dia de dados).
    generation_today = 0
    if not today_data.empty:
        generation_today = today_data['Total Generation(kWh)'].max() - today_data['Total Generation(kWh)'].min()
    
    # Lógica existente
    total_generation = df['Total Generation(kWh)'].max()
    house_load_kw = random.uniform(0.3, 2.5)
    
    savings_this_month = 0
    now = datetime.now()
    month_data = df[(df['Time'].dt.month == now.month) & (df['Time'].dt.year == now.year)]
    if not month_data.empty:
        generation_this_month = month_data['Total Generation(kWh)'].max() - month_data['Total Generation(kWh)'].min()
        savings_this_month = generation_this_month * user_tariff

    return jsonify({
        "todayGenKwh": generation_today, 
        "totalGenKwh": total_generation,
        "houseLoadKw": house_load_kw,
        "savingsThisMonth": savings_this_month
    })

# Rota para o histórico de geração das últimas 24h (usado no gráfico de linha).
@app.route('/api/generation/history', methods=['GET'])
def get_generation_history():
    # Pega os dados do inversor.
    df = get_inverter_data()
    if df is None or df.empty: 
        return jsonify({"error": "Não foi possível carregar os dados do inversor"}), 500

    # --- LÓGICA ALTERADA PARA INICIAR À 1H DA MANHÃ ---
    # Encontra a data do registro mais recente no DataFrame.
    latest_date = df['Time'].max().date()

    # Define o horário de início como 1 da manhã (01:00) dessa data.
    start_time = datetime.combine(latest_date, datetime.min.time()).replace(hour=1)
    
    # Define o horário final como 24 horas depois do início, para pegar o ciclo completo.
    end_time = start_time + timedelta(hours=24)
    # --- FIM DA LÓGICA ALTERADA ---

    # Filtra o DataFrame para o novo período (das 1h de hoje até 1h de amanhã).
    recent_data = df[(df['Time'] >= start_time) & (df['Time'] < end_time)].copy()
    
    # Agrupa os dados por hora e calcula a média.
    recent_data.set_index('Time', inplace=True)
    hourly_generation = recent_data['Power(W)'].resample('h').mean().fillna(0)

    # Garante que o eixo X tenha todas as 24h, mesmo que não haja dados.
    full_period_index = pd.date_range(start=start_time, periods=24, freq='h')
    hourly_generation = hourly_generation.reindex(full_period_index, fill_value=0)

    # Retorna os dados formatados para o gráfico.
    return jsonify({
        "labels": hourly_generation.index.strftime('%Hh').tolist(), 
        "generation_kw": (hourly_generation / 1000).round(2).tolist()
    })

# Rota para o relatório de geração mensal (usado na página de Relatórios).
@app.route('/api/reports/monthly', methods=['GET'])
def get_monthly_report():
    # Valida se o arquivo de relatório foi encontrado.
    if not MONTHLY_DATA_FILE: return jsonify({"error": "Arquivo de relatório mensal não configurado."}), 500
    try:
        # Lê e processa o arquivo CSV do relatório mensal.
        df = pd.read_csv(MONTHLY_DATA_FILE, delimiter=';', skiprows=20, encoding='latin1', skipfooter=1, engine='python')
        df.rename(columns={'Generation(kWh)': 'generation', 'Date': 'date'}, inplace=True)
        df['generation'] = pd.to_numeric(df['generation'].astype(str).str.replace(',', '.'), errors='coerce')
        df.dropna(subset=['date', 'generation'], inplace=True)
        # Converte os dados para um formato JSON e retorna.
        report_data = df[['date', 'generation']].to_dict(orient='records')
        return jsonify(report_data)
    except Exception as e:
        return jsonify({"error": f"Erro ao processar arquivo de relatório: {e}"}), 500

# Rota para listar os dispositivos de um usuário.
@app.route('/api/devices', methods=['GET'])
def get_devices():
    # Pega o email do usuário da URL.
    user_email = request.args.get('email')
    if not user_email: return jsonify({"error": "E-mail do usuário é necessário"}), 400
    
    # Lê os bancos de dados.
    devices_db = read_json_file(DEVICES_FILE, {})
    users_db = read_json_file(USERS_FILE, {})
    # Pega os dispositivos do usuário.
    user_devices = devices_db.get(user_email, [])
    
    # Usa a tarifa salva no perfil do usuário para o cálculo de custo.
    user_tariff = users_db.get(user_email, {}).get('tariff', 0.95)
    
    # Adiciona o custo por hora a cada dispositivo antes de retornar.
    for device in user_devices:
        cost_per_hour = (device.get('watts', 0) / 1000) * user_tariff
        device['cost_per_hour'] = f"R$ {cost_per_hour:.2f}"

    return jsonify(user_devices)

# Rota para adicionar um novo dispositivo.
@app.route('/api/devices', methods=['POST'])
def add_device():
    # Pega os dados do novo dispositivo.
    data = request.get_json()
    user_email, name, room, type = data.get('email'), data.get('name'), data.get('room'), data.get('type')
    if not all([user_email, name, room, type]): return jsonify({"error": "Todos os campos são obrigatórios"}), 400
    # Lê o banco de dados.
    devices_db = read_json_file(DEVICES_FILE, {})
    user_devices = devices_db.get(user_email, [])
    # Cria o novo dispositivo com um ID único.
    new_device = {"id": str(uuid.uuid4()), "name": name, "room": room, "type": type, "on": False, "watts": 0}
    # Adiciona um custo padrão para consistência de dados.
    new_device['cost_per_hour'] = "R$ 0.00"
    # Adiciona e salva o dispositivo.
    user_devices.append(new_device)
    devices_db[user_email] = user_devices
    write_json_file(DEVICES_FILE, devices_db)
    # Retorna o dispositivo criado.
    return jsonify(new_device), 201

# Rota para atualizar o estado de um dispositivo (ligar/desligar).
@app.route('/api/devices/<string:device_id>', methods=['PUT'])
def toggle_device(device_id):
    # Pega os dados da requisição.
    data = request.get_json()
    user_email, new_state = data.get('email'), data.get('on')
    if not user_email or new_state is None: return jsonify({"error": "Faltam dados para atualizar o dispositivo"}), 400
    # Lê o banco de dados.
    devices_db = read_json_file(DEVICES_FILE, {})
    user_devices = devices_db.get(user_email, [])
    # Procura pelo dispositivo com o ID correspondente.
    device_found = False
    for device in user_devices:
        if device['id'] == device_id:
            # Atualiza o estado (ligado/desligado).
            device['on'] = new_state
            # Simula o consumo em Watts baseado no tipo de dispositivo.
            device['watts'] = device['on'] * (200 if device['type'] == 'appliance' else 900 if device['type'] == 'climate' else 60)
            device_found = True
            break
    # Se não encontrar, retorna erro.
    if not device_found: return jsonify({"error": "Dispositivo não encontrado"}), 404
    # Salva as alterações.
    devices_db[user_email] = user_devices
    write_json_file(DEVICES_FILE, devices_db)
    return jsonify({"message": "Dispositivo atualizado"})

# Rota para excluir um dispositivo.
@app.route('/api/devices/<string:device_id>', methods=['DELETE'])
def delete_device(device_id):
    # Pega o email da URL.
    user_email = request.args.get('email')
    if not user_email: return jsonify({"error": "E-mail do usuário é necessário"}), 400
    # Lê o banco de dados.
    devices_db = read_json_file(DEVICES_FILE, {})
    user_devices = devices_db.get(user_email, [])
    # Remove o dispositivo da lista.
    initial_len = len(user_devices)
    user_devices = [d for d in user_devices if d['id'] != device_id]
    # Verifica se o dispositivo foi realmente removido.
    if len(user_devices) == initial_len: return jsonify({"error": "Dispositivo não encontrado"}), 404
    # Salva a lista atualizada.
    devices_db[user_email] = user_devices
    write_json_file(DEVICES_FILE, devices_db)
    return jsonify({"message": "Dispositivo removido"})

# Rota para excluir a conta de um usuário.
@app.route('/api/user', methods=['DELETE'])
def delete_user():
    # Pega os dados para confirmação.
    data = request.get_json()
    email, password = data.get('email'), data.get('password')
    if not email or not password:
        return jsonify({"error": "E-mail e senha são obrigatórios para exclusão"}), 400
    # Lê os bancos de dados.
    users_db = read_json_file(USERS_FILE, {})
    devices_db = read_json_file(DEVICES_FILE, {})
    user = users_db.get(email)
    # Confirma a senha antes de excluir.
    if not user or not check_password_hash(user.get('password'), password):
        return jsonify({"error": "Credenciais inválidas."}), 401
    try:
        # Remove o usuário e também seus dispositivos associados.
        del users_db[email]
        write_json_file(USERS_FILE, users_db)
        if email in devices_db:
            del devices_db[email]
            write_json_file(DEVICES_FILE, devices_db)
        return jsonify({"message": "Usuário e todos os seus dados foram removidos com sucesso."}), 200
    except Exception as e:
        return jsonify({"error": f"Ocorreu um erro ao remover o usuário: {e}"}), 500

# Rota para o status da bateria (simulado).
@app.route('/api/battery/status', methods=['GET'])
def get_battery_status():
    try:
        # Gera valores aleatórios para simular o estado da bateria.
        charged_percentage = random.randint(1, 100)
        empty_percentage = 100.0 - charged_percentage
        now = datetime.now()
        # Simula carregamento durante o dia e descarregamento à noite.
        is_charging = 9 <= now.hour < 16
        if is_charging:
            fluxo_watts = random.randint(500, 2500)
            status_texto = "Carregando"
        else:
            fluxo_watts = random.randint(-1500, -300) 
            status_texto = "Descarregando"
        
        # Calcula a energia armazenada com base na capacidade total.
        capacidade_total_kwh = 13.5
        energia_armazenada_kwh = round((charged_percentage / 100) * capacidade_total_kwh, 1)

        # Monta o objeto de dados da bateria.
        battery_data = {
            "charged_percentage": charged_percentage, "empty_percentage": empty_percentage,
            "labels": ["Carga", "Vazio"], "fluxo_watts": fluxo_watts,
            "status_texto": status_texto, 'energia_kwh': energia_armazenada_kwh
        }
        # Retorna os dados em JSON.
        return jsonify(battery_data)
    except Exception as e:
        return jsonify({"error": f"Erro ao obter dados da bateria: {e}"}), 500

# Rota para o chatbot de IA, que também lida com comandos de voz.
@app.route('/api/ask-agent', methods=['POST'])
def ask_agent():
    try:
        # Pega a pergunta e o email do usuário.
        data = request.get_json()
        question = data.get("question", "")
        user_email = data.get("email", "")

        if not question or not user_email:
            return jsonify({"error": "Pergunta e e-mail são obrigatórios"}), 400

        # Pega a lista de dispositivos do usuário para dar contexto à IA.
        devices_db = read_json_file(DEVICES_FILE, {})
        user_devices = devices_db.get(user_email, [])
        device_names = [d['name'] for d in user_devices]
        
        # Monta o prompt para o Gemini, ensinando-o a identificar comandos e responder em JSON.
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            f"""
            Você é um assistente de casa inteligente. Analise o pedido do usuário.
            Os dispositivos disponíveis são: {', '.join(device_names)}.

            - Se o pedido for um comando para ligar, desligar, acender ou apagar um dispositivo, responda APENAS com um JSON no formato:
            {{"command": true, "device_name": "nome do dispositivo", "action": "on" ou "off"}}
            
            - Se for qualquer outra pergunta, responda normalmente em Markdown.

            Pedido do usuário: "{question}"
            """
        )

        # Tenta interpretar a resposta da IA como um comando JSON.
        try:
            potential_command = json.loads(response.text)
            # Se for um comando válido, executa a ação no dispositivo.
            if isinstance(potential_command, dict) and potential_command.get("command"):
                device_name = potential_command.get("device_name")
                action = potential_command.get("action")
                
                # Procura o dispositivo pelo nome, ignorando maiúsculas/minúsculas.
                target_device = next((d for d in user_devices if d['name'].lower() == device_name.lower()), None)

                if not target_device:
                    return jsonify({"answer": f"Não encontrei um dispositivo chamado '{device_name}'."})
                
                # Define o novo estado e atualiza o dispositivo.
                new_state = (action == 'on')
                target_device['on'] = new_state
                target_device['watts'] = new_state * (200 if target_device['type'] == 'appliance' else 900 if target_device['type'] == 'climate' else 60)
                
                # Salva o estado atualizado dos dispositivos.
                devices_db[user_email] = user_devices
                write_json_file(DEVICES_FILE, devices_db)

                # Retorna uma mensagem de confirmação para o usuário.
                action_text = "ligado" if new_state else "desligado"
                return jsonify({"answer": f"Ok, dispositivo '{target_device['name']}' foi {action_text}."})

        # Se a resposta da IA não for um JSON, trata como uma resposta de texto normal.
        except (json.JSONDecodeError, TypeError):
            return jsonify({"answer": response.text})

    except Exception as e:
        return jsonify({"error": f"Erro do agente: {e}"}), 500

# Rota para atualizar o nome do usuário no perfil.
@app.route('/api/user/profile', methods=['PUT'])
def update_user_profile():
    # Pega os dados da requisição.
    data = request.get_json()
    email, new_name = data.get('email'), data.get('name')
    if not email or not new_name:
        return jsonify({"error": "E-mail e novo nome são obrigatórios"}), 400
    # Lê, atualiza e salva o nome do usuário.
    users_db = read_json_file(USERS_FILE, {})
    if email in users_db:
        users_db[email]['name'] = new_name
        write_json_file(USERS_FILE, users_db)
        updated_user = users_db[email].copy()
        del updated_user['password']
        return jsonify(updated_user)
    return jsonify({"error": "Usuário não encontrado."}), 404

# Rota para salvar as preferências do usuário (tarifa, meta, notificações).
@app.route('/api/user/preferences', methods=['PUT'])
def save_preferences():
    # Pega os dados da requisição.
    data = request.get_json()
    email = data.get('email')
    tariff = data.get('tariff')
    savings_goal = data.get('savingsGoal')
    notifications = data.get('notifications')

    if not email: return jsonify({"error": "Email é obrigatório"}), 400

    # Lê o banco de dados.
    users_db = read_json_file(USERS_FILE, {})
    if email in users_db:
        try:
            # Atualiza cada preferência se ela foi enviada na requisição.
            if tariff is not None:
                users_db[email]['tariff'] = float(tariff)
            if savings_goal is not None:
                users_db[email]['savingsGoal'] = int(savings_goal)
            if notifications is not None:
                users_db[email]['notifications'] = notifications

            # Salva o arquivo de usuários.
            write_json_file(USERS_FILE, users_db)
            
            # Retorna os dados do usuário atualizado para o frontend.
            updated_user = users_db[email].copy()
            del updated_user['password']
            return jsonify(updated_user)
        # Trata o erro caso a tarifa ou meta não sejam números válidos.
        except (ValueError, TypeError):
            return jsonify({"error": "Preferências devem ser válidas."}), 400
    
    return jsonify({"error": "Usuário não encontrado."}), 404

@app.route('/api/optimizer/suggest-time', methods=['POST'])
def suggest_optimal_time():
    # Pega os dados enviados pelo frontend
    data = request.get_json()
    task_info = data.get('task') # Ex: "Lavar Roupa"
    user_email = data.get('email')

    if not task_info or not user_email:
        return jsonify({"error": "Informações da tarefa e email são obrigatórios"}), 400

    try:
        # --- Passo 1: Buscar a Previsão do Tempo (FUTURO) ---
        # Usaremos a API One Call da OpenWeatherMap, que fornece previsão horária
        api_key = '2d1f3910b6139ba59b1385427c34b64e' # Sua chave
        lat, lon = -23.5614, -46.6565
        # Excluímos 'current', 'minutely', 'daily' para pegar apenas os dados horários ('hourly')
        forecast_url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=current,minutely,daily,alerts&appid={api_key}&units=metric"
        
        # A biblioteca 'requests' é mais recomendada para chamadas de API externas
        import requests
        forecast_response = requests.get(forecast_url)
        forecast_data = forecast_response.json()
        
        # Formata a previsão horária para as próximas 24h em um texto simples
        hourly_forecast = ""
        for i in range(24):
            hour_data = forecast_data['hourly'][i]
            dt_object = datetime.fromtimestamp(hour_data['dt'])
            clouds = hour_data['clouds'] # Nebulosidade em %
            hourly_forecast += f"- {dt_object.strftime('%H:%M')}: Nebulosidade de {clouds}%\n"

        # --- Passo 2: Analisar Dados Históricos de Geração (PASSADO) ---
        df = get_inverter_data()
        df.set_index('Time', inplace=True)
        # Calcula a média de geração de energia para cada hora do dia
        average_generation_by_hour = df['Power(W)'].groupby(df.index.hour).mean()
        historical_pattern = ""
        for hour, avg_power in average_generation_by_hour.items():
            historical_pattern += f"- {hour:02d}h: Média de {avg_power:.0f} W\n"

        # --- Passo 3: Montar o Prompt e Consultar a IA ---
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""
        Você é um especialista em otimização de energia. Seu objetivo é encontrar a melhor janela de 2 horas nas próximas 24 horas para executar uma tarefa de alto consumo ('{task_info}').

        Use os seguintes dados para tomar sua decisão:

        1. PREVISÃO DE TEMPO (próximas 24h):
        {hourly_forecast}

        2. PADRÃO DE GERAÇÃO HISTÓRICO (média de geração por hora):
        {historical_pattern}

        Analise a previsão de nebulosidade e o histórico de geração. A melhor janela de tempo é aquela com a MENOR nebulosidade prevista e que coincide com o MAIOR pico de geração histórica.

        Responda APENAS com um JSON no seguinte formato:
        {{"horario_recomendado": "HH:00", "justificativa": "Uma frase curta explicando o porquê."}}
        """
        
        response = model.generate_content(prompt)
        
        # Tenta converter a resposta da IA em JSON
        suggestion = json.loads(response.text)
        
        return jsonify(suggestion)

    except Exception as e:
        print(f"ERRO no otimizador: {e}")
        # Retorna uma resposta padrão em caso de erro na API ou na IA
        return jsonify({
            "horario_recomendado": "13:00",
            "justificativa": "O período da tarde geralmente oferece a melhor geração solar."
        })

@app.route('/api/reports/insights', methods=['GET'])
def get_report_insights():
    user_email = request.args.get('email')
    if not user_email:
        return jsonify({"error": "Email do usuário é obrigatório"}), 400

    try:
        df = get_inverter_data()
        if df is None or df.empty:
            return jsonify({"insights": "Não há dados suficientes para gerar uma análise."})

        # --- Passo 1: Calcular as métricas do último mês ---
        
        # Define o período do "último mês" (últimos 30 dias a partir do último registro)
        end_date = df['Time'].max()
        start_date = end_date - timedelta(days=30)
        
        last_month_data = df[(df['Time'] >= start_date) & (df['Time'] <= end_date)]

        if last_month_data.empty:
            return jsonify({"insights": "Não há dados suficientes do último mês para gerar uma análise."})

        # Métrica 1: Geração total no período
        generation_last_month = last_month_data['Total Generation(kWh)'].max() - last_month_data['Total Generation(kWh)'].min()

        # Métrica 2: Dia de pico de geração
        daily_generation = last_month_data.set_index('Time').resample('D')['Total Generation(kWh)'].apply(lambda x: x.max() - x.min())
        peak_day = daily_generation.idxmax().strftime('%d de %B') # Ex: "15 de Setembro"
        peak_day_generation = daily_generation.max()

        # Métrica 3: Dispositivo de maior consumo (simulado para exemplo)
        devices_db = read_json_file(DEVICES_FILE, {})
        user_devices = devices_db.get(user_email, [])
        top_consumer_device = "Nenhum dispositivo cadastrado"
        if user_devices:
            # Simplesmente pega o primeiro dispositivo como exemplo de "maior consumidor"
            top_consumer_device = user_devices[0]['name']

        # --- Passo 2: Montar o prompt e consultar a IA ---
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""
        Você é um analista de dados especialista em energia solar. Com base nas seguintes métricas de performance dos últimos 30 dias de um cliente, escreva um resumo em 3 bullets.
        
        Use um tom amigável e informativo. Use emojis e negrito para destacar informações.

        Métricas do Cliente:
        - Geração total nos últimos 30 dias: {generation_last_month:.2f} kWh
        - Dia de maior geração: {peak_day}, com {peak_day_generation:.2f} kWh gerados.
        - Dispositivo frequentemente usado: {top_consumer_device}

        Estrutura da resposta:
        - Bullet 1 (Elogio): Parabenize o cliente pela geração total, mencionando o dia de pico.
        - Bullet 2 (Ponto de Atenção): Crie um ponto de atenção genérico sobre o consumo do dispositivo mencionado, sugerindo otimização.
        - Bullet 3 (Recomendação): Dê uma recomendação geral para maximizar a economia, como usar aparelhos de alto consumo durante o dia.
        """

        response = model.generate_content(prompt)
        
        # Retorna o texto gerado pela IA
        return jsonify({"insights": response.text})

    except Exception as e:
        print(f"ERRO ao gerar insights: {e}")
        return jsonify({"error": "Não foi possível gerar a análise no momento."}), 500

@app.route('/api/dashboard-insights', methods=['GET'])
def get_dashboard_insights():
    user_email = request.args.get('email')
    if not user_email: return jsonify([]), 400

    try:
        # --- Passo 1: Coletar Métricas para a IA ---
        kpis_response = get_kpis()
        kpis_data = kpis_response.get_json()
        battery_response = get_battery_status()
        battery_data = battery_response.get_json()

        # --- Passo 2: Montar o Prompt Avançado ---
        # Instruímos a IA a gerar uma lista de insights em formato JSON
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""
        Você é um analista de dados de energia. Analise os dados do usuário abaixo e gere uma lista de 3 insights curtos e úteis.
        Os insights devem ser de tipos diferentes: um elogio, um alerta e uma dica de otimização.

        Dados do Usuário:
        - Geração de hoje: {kpis_data.get('todayGenKwh', 0):.2f} kWh
        - Consumo atual: {kpis_data.get('houseLoadKw', 0):.2f} kW
        - Status da bateria: {battery_data.get('charged_percentage', 0)}% e {battery_data.get('status_texto')}
        - Economia do mês: R$ {kpis_data.get('savingsThisMonth', 0):.2f}

        Sua resposta DEVE SER APENAS um array JSON válido, sem nenhum texto antes ou depois.
        Cada objeto no array deve ter as chaves "type" e "text".
        Tipos válidos: "elogio", "alerta", "dica".

        Exemplo de resposta:
        [
            {{"type": "elogio", "text": "🌞 Parabéns! Sua geração hoje está excelente e você já economizou R$ {kpis_data.get('savingsThisMonth', 0):.2f} este mês!"}},
            {{"type": "alerta", "text": "⚠️ Atenção: seu consumo atual está um pouco alto. Considere desligar aparelhos que não estão em uso."}},
            {{"type": "dica", "text": "💡 Dica: Com a bateria em {battery_data.get('charged_percentage', 0)}%, este é um bom momento para usar aparelhos de alto consumo."}}
        ]
        """
        
        response = model.generate_content(prompt)
        # Limpa a resposta para garantir que seja um JSON válido
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '')
        insights = json.loads(cleaned_response)
        
        return jsonify(insights)

    except Exception as e:
        print(f"ERRO ao gerar insights para o stack: {e}")
        # Retorna uma lista de sugestões padrão em caso de erro, para não quebrar o frontend
        fallback_insights = [
            {"type": "dica", "text": "💡 Use seus aparelhos de maior consumo durante o dia para aproveitar a energia solar gratuita."},
            {"type": "elogio", "text": "🌞 Continue acompanhando seus dados para maximizar sua economia de energia!"},
            {"type": "alerta", "text": "⚠️ Lembre-se de verificar a limpeza dos seus painéis solares periodicamente."}
        ]
        return jsonify(fallback_insights)
    
# Rota para BUSCAR o histórico de conversas de um usuário
@app.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    user_email = request.args.get('email')
    if not user_email:
        return jsonify({"error": "Email do usuário é obrigatório"}), 400

    all_histories = read_json_file(CHAT_HISTORY_FILE, {})
    user_history = all_histories.get(user_email, {})

    return jsonify(user_history)

# Rota para SALVAR o histórico de conversas de um usuário
@app.route('/api/chat/history', methods=['POST'])
def save_chat_history():
    data = request.get_json()
    user_email = data.get('email')
    conversations = data.get('conversations')

    if not user_email or conversations is None:
        return jsonify({"error": "Email e histórico são obrigatórios"}), 400

    all_histories = read_json_file(CHAT_HISTORY_FILE, {})
    all_histories[user_email] = conversations
    write_json_file(CHAT_HISTORY_FILE, all_histories)

    return jsonify({"message": "Histórico salvo com sucesso."})

# --- INICIALIZAÇÃO DO SERVIDOR ---
# Este bloco garante que o servidor só rode quando o script for executado diretamente.
if __name__ == '__main__':
    # 'debug=True' reinicia o servidor automaticamente quando você salva o arquivo.
    app.run(debug=True, port=5000)
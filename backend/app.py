from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import pandas as pd
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

# --- CONFIGURAÇÃO INICIAL DA APLICAÇÃO ---
app = Flask(__name__)
CORS(app)

# --- CAMINHOS PARA OS ARQUIVOS DE DADOS (VERSÃO CORRIGIDA FINAL) ---
# O script agora procura os arquivos na sua própria pasta (backend)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')

def find_file_by_pattern(directory, pattern):
    try:
        for filename in os.listdir(directory):
            if pattern in filename:
                print(f"Arquivo encontrado para o padrão '{pattern}': {filename}")
                return os.path.join(directory, filename)
    except FileNotFoundError:
        print(f"ERRO: O diretório '{directory}' não foi encontrado.")
        return None
    print(f"AVISO: Nenhum arquivo encontrado para o padrão '{pattern}' em '{directory}'.")
    return None

# Procura os arquivos CSV na mesma pasta do app.py (backend)
HISTORICAL_DATA_FILE = find_file_by_pattern(BASE_DIR, 'Historical Data Export')
MONTHLY_DATA_FILE = find_file_by_pattern(BASE_DIR, '2025_Plant')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
DEVICES_FILE = os.path.join(DATA_DIR, 'dispositivos.json')


# (O resto do código permanece exatamente igual...)

# --- FUNÇÕES AUXILIARES ---
def read_json_file(filepath, default_data):
    if not os.path.exists(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))
    if not os.path.exists(filepath):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(default_data, f)
        return default_data
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_json_file(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

inverter_data_cache = None
cache_time = None

def get_inverter_data():
    global inverter_data_cache, cache_time
    if inverter_data_cache is not None and cache_time and (datetime.now() - cache_time < timedelta(minutes=10)):
        return inverter_data_cache
    if not HISTORICAL_DATA_FILE: return None
    try:
        df = pd.read_csv(HISTORICAL_DATA_FILE, delimiter=';', skiprows=2, encoding='latin1')
        df['Time'] = pd.to_datetime(df['Time'], format='%d.%m.%Y %H:%M:%S')
        numeric_cols = ['Power(W)', 'Total Generation(kWh)']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
        df.dropna(subset=numeric_cols, inplace=True)
        inverter_data_cache = df
        cache_time = datetime.now()
        print("Dados do inversor carregados e processados com sucesso.")
        return df
    except Exception as e:
        print(f"ERRO ao processar o arquivo CSV histórico: {e}")
        return None


# --- ROTAS DE API ---
@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()
    name, email, password = data.get('name'), data.get('email'), data.get('password')
    if not all([name, email, password]): return jsonify({"error": "Todos os campos são obrigatórios"}), 400
    users_db = read_json_file(USERS_FILE, {})
    if email in users_db: return jsonify({"error": "Este e-mail já está cadastrado."}), 409
    users_db[email] = {"name": name, "email": email, "password": generate_password_hash(password), "plan": "Starter", "theme": "padrão", "colorTheme": "dark"}
    write_json_file(USERS_FILE, users_db)
    user_data_to_return = users_db[email].copy()
    del user_data_to_return['password']
    return jsonify(user_data_to_return), 201

@app.route('/api/login', methods=['POST'])
def login_user():
    data = request.get_json()
    email, password = data.get('email'), data.get('password')
    if not email or not password: return jsonify({"error": "E-mail e senha são obrigatórios"}), 400
    users_db = read_json_file(USERS_FILE, {})
    user = users_db.get(email)
    if not user or not user.get('password') or not check_password_hash(user.get('password'), password):
        return jsonify({"error": "Credenciais inválidas."}), 401
    user_data_to_return = user.copy()
    del user_data_to_return['password']
    return jsonify(user_data_to_return)

@app.route('/api/user/theme', methods=['PUT'])
def save_theme():
    data = request.get_json()
    email, theme, colorTheme = data.get('email'), data.get('theme'), data.get('colorTheme')
    if not email or (theme is None and colorTheme is None):
        return jsonify({"error": "Faltam informações para salvar o tema."}), 400
    users_db = read_json_file(USERS_FILE, {})
    if email in users_db:
        if theme is not None:
            users_db[email]['theme'] = theme
        if colorTheme is not None:
            users_db[email]['colorTheme'] = colorTheme
        write_json_file(USERS_FILE, users_db)
        return jsonify({"message": "Tema salvo com sucesso!"})
    return jsonify({"error": "Usuário não encontrado."}), 404

@app.route('/api/kpis', methods=['GET'])
def get_kpis():
    df = get_inverter_data()
    if df is None or df.empty: return jsonify({"error": "Não foi possível carregar os dados do inversor"}), 500
    total_generation = df['Total Generation(kWh)'].max()
    today = datetime.now().date()
    start_of_today = datetime.combine(today, datetime.min.time())
    today_data = df[df['Time'] >= start_of_today]
    generation_today = 0
    if not today_data.empty:
        generation_today = today_data['Total Generation(kWh)'].max() - today_data['Total Generation(kWh)'].min()
    return jsonify({"todayGenKwh": generation_today, "totalGenKwh": total_generation})

@app.route('/api/generation/history', methods=['GET'])
def get_generation_history():
    df = get_inverter_data()
    if df is None or df.empty: return jsonify({"error": "Não foi possível carregar os dados do inversor"}), 500
    end_time = df['Time'].max()
    start_time = end_time - timedelta(hours=24)
    recent_data = df[(df['Time'] >= start_time) & (df['Time'] <= end_time)].copy()
    recent_data.set_index('Time', inplace=True)
    hourly_generation = recent_data['Power(W)'].resample('h').mean().fillna(0)
    return jsonify({"labels": hourly_generation.index.strftime('%Hh').tolist(), "generation_kw": (hourly_generation / 1000).round(2).tolist()})

@app.route('/api/reports/monthly', methods=['GET'])
def get_monthly_report():
    if not MONTHLY_DATA_FILE: return jsonify({"error": "Arquivo de relatório mensal não configurado ou não encontrado."}), 500
    try:
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
    user_email = request.args.get('email')
    if not user_email: return jsonify({"error": "E-mail do usuário é necessário"}), 400
    devices_db = read_json_file(DEVICES_FILE, {})
    user_devices = devices_db.get(user_email, [])
    return jsonify(user_devices)

@app.route('/api/devices', methods=['POST'])
def add_device():
    data = request.get_json()
    user_email, name, room, type = data.get('email'), data.get('name'), data.get('room'), data.get('type')
    if not all([user_email, name, room, type]): return jsonify({"error": "Todos os campos são obrigatórios"}), 400
    devices_db = read_json_file(DEVICES_FILE, {})
    user_devices = devices_db.get(user_email, [])
    new_device = {"id": str(uuid.uuid4()), "name": name, "room": room, "type": type, "on": False, "watts": 0}
    user_devices.append(new_device)
    devices_db[user_email] = user_devices
    write_json_file(DEVICES_FILE, devices_db)
    return jsonify(new_device), 201

@app.route('/api/devices/<string:device_id>', methods=['PUT'])
def toggle_device(device_id):
    data = request.get_json()
    user_email, new_state = data.get('email'), data.get('on')
    if not user_email or new_state is None: return jsonify({"error": "Faltam dados para atualizar o dispositivo"}), 400
    devices_db = read_json_file(DEVICES_FILE, {})
    user_devices = devices_db.get(user_email, [])
    device_found = False
    for device in user_devices:
        if device['id'] == device_id:
            device['on'] = new_state
            device['watts'] = device['on'] * (200 if device['type'] == 'appliance' else 900 if device['type'] == 'climate' else 60)
            device_found = True
            break
    if not device_found: return jsonify({"error": "Dispositivo não encontrado"}), 404
    devices_db[user_email] = user_devices
    write_json_file(DEVICES_FILE, devices_db)
    return jsonify({"message": "Dispositivo atualizado"})

@app.route('/api/devices/<string:device_id>', methods=['DELETE'])
def delete_device(device_id):
    user_email = request.args.get('email')
    if not user_email: return jsonify({"error": "E-mail do usuário é necessário"}), 400
    devices_db = read_json_file(DEVICES_FILE, {})
    user_devices = devices_db.get(user_email, [])
    initial_len = len(user_devices)
    user_devices = [d for d in user_devices if d['id'] != device_id]
    if len(user_devices) == initial_len: return jsonify({"error": "Dispositivo não encontrado"}), 404
    devices_db[user_email] = user_devices
    write_json_file(DEVICES_FILE, devices_db)
    return jsonify({"message": "Dispositivo removido"})

@app.route('/api/user', methods=['DELETE'])
def delete_user():
    # 1. Obter os dados (e-mail e senha para confirmação)
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "E-mail e senha são obrigatórios para exclusão"}), 400

    # 2. Ler os bancos de dados de usuários e dispositivos
    users_db = read_json_file(USERS_FILE, {})
    devices_db = read_json_file(DEVICES_FILE, {})

    user = users_db.get(email)

    # 3. VERIFICAÇÃO DE SEGURANÇA: Checar se o usuário existe e se a senha está correta
    if not user or not check_password_hash(user.get('password'), password):
        # Usamos a mesma mensagem de erro do login para não informar se o erro foi no e-mail ou na senha
        return jsonify({"error": "Credenciais inválidas."}), 401

    # 4. Se a senha estiver correta, proceder com a exclusão
    try:
        # Remover o usuário de users.json
        del users_db[email]
        write_json_file(USERS_FILE, users_db)

        # Remover os dispositivos associados ao usuário em dispositivos.json (se existirem)
        if email in devices_db:
            del devices_db[email]
            write_json_file(DEVICES_FILE, devices_db)

        return jsonify({"message": "Usuário e todos os seus dados foram removidos com sucesso."}), 200

    except Exception as e:
        # Em caso de um erro inesperado durante a escrita dos arquivos
        return jsonify({"error": f"Ocorreu um erro ao remover o usuário: {e}"}), 500


# --- INICIALIZAÇÃO DO SERVIDOR ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)
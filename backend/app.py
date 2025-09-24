# --- IMPORTAÇÃO DAS BIBLIOTECAS NECESSÁRIAS ---

# Importa as classes principais do Flask:
# - Flask: A classe principal para criar a aplicação web.
# - request: Um objeto que contém os dados de uma requisição HTTP recebida (ex: dados de um formulário).
# - jsonify: Uma função que converte dicionários Python para o formato JSON, para ser enviado como resposta da API.
import google.generativeai as genai
from flask import Response
from dotenv import load_dotenv
from flask import Flask, request, jsonify
# Importa a extensão Flask-CORS para lidar com Cross-Origin Resource Sharing.
# Isso permite que o seu frontend (rodando em um domínio/porta diferente) possa fazer requisições para este backend.
from flask_cors import CORS

#sabe o que é importa random né nao preciso detalhar
import random

# Importa a biblioteca 'json' para trabalhar com arquivos JSON (ler e escrever).
import json

# Importa a biblioteca 'os' para interagir com o sistema operacional, principalmente para manipular caminhos de arquivos.
import os

# Importa a biblioteca 'pandas' (com o apelido 'pd'), uma ferramenta poderosa para análise e manipulação de dados, usada aqui para ler e processar os arquivos CSV.
import pandas as pd

# Importa 'datetime' e 'timedelta' para trabalhar com datas e horas (ex: para filtrar dados por data ou implementar um cache).
from datetime import datetime, timedelta

# Importa funções de segurança da biblioteca 'werkzeug' (que é uma dependência do Flask).
# - generate_password_hash: Cria um "hash" seguro de uma senha (nunca se deve salvar senhas em texto puro).
# - check_password_hash: Compara uma senha fornecida pelo usuário com o hash salvo no banco de dados.
from werkzeug.security import generate_password_hash, check_password_hash

# Importa a biblioteca 'uuid' para gerar identificadores únicos universais, usados aqui para criar IDs únicos para cada dispositivo.
import uuid
# Carrega variáveis do .env
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Cria o cliente com a chave


# --- CONFIGURAÇÃO INICIAL DA APLICAÇÃO ---

# Cria uma instância da aplicação Flask. '__name__' é uma variável especial do Python que ajuda o Flask a saber onde procurar recursos como templates e arquivos estáticos.
app = Flask(__name__)

# Habilita o CORS para toda a aplicação 'app'. Isso adiciona os cabeçalhos HTTP necessários para permitir requisições de outras origens.
CORS(app)

# --- CAMINHOS PARA OS ARQUIVOS DE DADOS (VERSÃO CORRIGIDA FINAL) ---

# Define o diretório base como o diretório onde este script (app.py) está localizado.
# os.path.abspath(__file__) pega o caminho absoluto do script atual.
# os.path.dirname(...) pega o nome do diretório a partir desse caminho.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define o diretório de dados como uma pasta chamada 'data' que está um nível acima do diretório do script.
# '..' representa o diretório pai. Ex: se o script está em /projeto/backend/, DATA_DIR será /projeto/data/.
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')

# Define uma função para encontrar um arquivo em um diretório com base em um padrão no nome.
def find_file_by_pattern(directory, pattern):
    # Inicia um bloco 'try' para lidar com possíveis erros, como o diretório não existir.
    try:
        # Itera sobre cada nome de arquivo no diretório especificado.
        for filename in os.listdir(directory):
            # Verifica se o padrão de texto (ex: 'Historical Data Export') está contido no nome do arquivo.
            if pattern in filename:
                # Se encontrar, imprime uma mensagem de sucesso no console para depuração.
                print(f"Arquivo encontrado para o padrão '{pattern}': {filename}")
                # Retorna o caminho completo para o arquivo encontrado.
                return os.path.join(directory, filename)
    # Se um erro 'FileNotFoundError' ocorrer (o diretório não existe), este bloco é executado.
    except FileNotFoundError:
        # Imprime uma mensagem de erro clara no console.
        print(f"ERRO: O diretório '{directory}' não foi encontrado.")
        # Retorna 'None' para indicar que o arquivo não foi encontrado.
        return None
    # Se o loop terminar sem encontrar um arquivo, esta parte é executada.
    print(f"AVISO: Nenhum arquivo encontrado para o padrão '{pattern}' em '{directory}'.")
    # Retorna 'None' para indicar que nenhum arquivo correspondente foi encontrado.
    return None

# Procura o arquivo de dados históricos na mesma pasta do script (BASE_DIR) usando o padrão 'Historical Data Export'.
HISTORICAL_DATA_FILE = find_file_by_pattern(BASE_DIR, 'Historical Data Export')
# Procura o arquivo de dados mensais na mesma pasta do script (BASE_DIR) usando o padrão '2025_Plant'.
MONTHLY_DATA_FILE = find_file_by_pattern(BASE_DIR, '2025_Plant')
# Constrói o caminho completo para o arquivo 'users.json' dentro do diretório de dados.
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
# Constrói o caminho completo para o arquivo 'dispositivos.json' dentro do diretório de dados.
DEVICES_FILE = os.path.join(DATA_DIR, 'dispositivos.json')


# --- FUNÇÕES AUXILIARES ---

# Define uma função para ler um arquivo JSON de forma segura.
# Ela recebe o caminho do arquivo e um dicionário/lista com dados padrão.
def read_json_file(filepath, default_data):
    # Verifica se o diretório onde o arquivo deveria estar não existe.
    if not os.path.exists(os.path.dirname(filepath)):
        # Se não existir, cria o diretório.
        os.makedirs(os.path.dirname(filepath))
    # Verifica se o arquivo em si não existe.
    if not os.path.exists(filepath):
        # Se não existir, cria o arquivo no modo de escrita ('w') com codificação UTF-8.
        with open(filepath, 'w', encoding='utf-8') as f:
            # Escreve os dados padrão (default_data) no novo arquivo.
            json.dump(default_data, f)
        # Retorna os dados padrão, pois o arquivo acabou de ser criado com eles.
        return default_data
    # Se o arquivo já existe, abre-o no modo de leitura ('r') com codificação UTF-8.
    with open(filepath, 'r', encoding='utf-8') as f:
        # Carrega o conteúdo JSON do arquivo e o retorna como um objeto Python (dicionário ou lista).
        return json.load(f)

# Define uma função para escrever dados em um arquivo JSON.
def write_json_file(filepath, data):
    # Abre o arquivo especificado no modo de escrita ('w') com codificação UTF-8.
    with open(filepath, 'w', encoding='utf-8') as f:
        # Escreve o objeto Python 'data' no arquivo em formato JSON.
        # 'indent=2' formata o arquivo com 2 espaços de indentação para ser mais legível.
        # 'ensure_ascii=False' permite que caracteres especiais (como acentos) sejam salvos corretamente.
        json.dump(data, f, indent=2, ensure_ascii=False)

# Variável para armazenar os dados do inversor em cache na memória. Começa como 'None'.
inverter_data_cache = None
# Variável para armazenar o horário em que o cache foi criado. Começa como 'None'.
cache_time = None

# Define uma função para obter os dados do inversor, usando um sistema de cache.
def get_inverter_data():
    # Declara que vamos modificar as variáveis globais 'inverter_data_cache' e 'cache_time'.
    global inverter_data_cache, cache_time
    # Verifica se o cache existe e se foi criado há menos de 10 minutos.
    if inverter_data_cache is not None and cache_time and (datetime.now() - cache_time < timedelta(minutes=10)):
        # Se o cache for válido, retorna os dados cacheados sem precisar ler o arquivo novamente.
        return inverter_data_cache
    # Se o caminho para o arquivo histórico não foi encontrado, retorna 'None'.
    if not HISTORICAL_DATA_FILE: return None
    # Inicia um bloco 'try' para capturar erros durante a leitura e processamento do arquivo.
    try:
        # Lê o arquivo CSV usando pandas.
        # - delimiter=';': informa que as colunas são separadas por ponto e vírgula.
        # - skiprows=2: ignora as 2 primeiras linhas do arquivo (geralmente cabeçalhos ou metadados).
        # - encoding='latin1': especifica a codificação de caracteres do arquivo, comum em arquivos gerados no Windows.
        df = pd.read_csv(HISTORICAL_DATA_FILE, delimiter=';', skiprows=2, encoding='latin1')
        # Converte a coluna 'Time' para o formato de data e hora do pandas, especificando o formato original.
        df['Time'] = pd.to_datetime(df['Time'], format='%d.%m.%Y %H:%M:%S')
        # Define uma lista com os nomes das colunas que devem ser numéricas.
        numeric_cols = ['Power(W)', 'Total Generation(kWh)']
        # Itera sobre cada nome de coluna na lista acima.
        for col in numeric_cols:
            # Converte a coluna para texto, substitui vírgulas por pontos (para decimais) e depois converte para número.
            # 'errors='coerce'' transforma qualquer valor que não puder ser convertido em 'NaN' (Not a Number).
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
        # Remove quaisquer linhas que tenham valores 'NaN' nas colunas numéricas especificadas.
        df.dropna(subset=numeric_cols, inplace=True)
        # Atualiza o cache global com o DataFrame processado.
        inverter_data_cache = df
        # Atualiza o tempo do cache para o horário atual.
        cache_time = datetime.now()
        # Imprime uma mensagem de sucesso no console para depuração.
        print("Dados do inversor carregados e processados com sucesso.")
        # Retorna o DataFrame processado.
        return df
    # Se ocorrer qualquer exceção (erro) no bloco 'try', este bloco é executado.
    except Exception as e:
        # Imprime uma mensagem de erro detalhada no console.
        print(f"ERRO ao processar o arquivo CSV histórico: {e}")
        # Retorna 'None' para indicar que houve uma falha.
        return None


# --- ROTAS DE API ---

# Define a rota '/api/register' que aceita requisições do tipo POST.
@app.route('/api/register', methods=['POST'])
def register_user():
    # Obtém os dados JSON enviados na requisição.
    data = request.get_json()
    # Extrai os campos 'name', 'email' e 'password' dos dados recebidos.
    name, email, password = data.get('name'), data.get('email'), data.get('password')
    # Verifica se algum dos campos essenciais está faltando.
    if not all([name, email, password]): return jsonify({"error": "Todos os campos são obrigatórios"}), 400
    # Lê o arquivo de usuários ou cria um dicionário vazio se ele não existir.
    users_db = read_json_file(USERS_FILE, {})
    # Verifica se o e-mail fornecido já existe como uma chave no banco de dados de usuários.
    if email in users_db: return jsonify({"error": "Este e-mail já está cadastrado."}), 409
    # Adiciona o novo usuário ao dicionário, usando o e-mail como chave. A senha é armazenada como um hash.
    users_db[email] = {"name": name, "email": email, "password": generate_password_hash(password), "plan": "Starter", "theme": "padrão", "colorTheme": "dark"}
    # Salva o dicionário de usuários atualizado de volta no arquivo JSON.
    write_json_file(USERS_FILE, users_db)
    # Cria uma cópia dos dados do novo usuário para retornar na resposta.
    user_data_to_return = users_db[email].copy()
    # Remove a chave 'password' da cópia para não enviar o hash da senha de volta ao cliente.
    del user_data_to_return['password']
    # Retorna os dados do usuário recém-criado com o status HTTP 201 (Created).
    return jsonify(user_data_to_return), 201

# Define a rota '/api/login' que aceita requisições do tipo POST.
@app.route('/api/login', methods=['POST'])
def login_user():
    # Obtém os dados JSON enviados na requisição.
    data = request.get_json()
    # Extrai o e-mail e a senha dos dados.
    email, password = data.get('email'), data.get('password')
    # Verifica se o e-mail ou a senha não foram fornecidos.
    if not email or not password: return jsonify({"error": "E-mail e senha são obrigatórios"}), 400
    # Lê o banco de dados de usuários.
    users_db = read_json_file(USERS_FILE, {})
    # Tenta obter os dados do usuário correspondente ao e-mail fornecido.
    user = users_db.get(email)
    # Verifica se o usuário não foi encontrado OU se o hash da senha não existe OU se a senha fornecida não corresponde ao hash salvo.
    if not user or not user.get('password') or not check_password_hash(user.get('password'), password):
        # Se qualquer uma das verificações falhar, retorna um erro de credenciais inválidas.
        return jsonify({"error": "Credenciais inválidas."}), 401
    # Cria uma cópia dos dados do usuário para retornar na resposta.
    user_data_to_return = user.copy()
    # Remove a chave 'password' da cópia por segurança.
    del user_data_to_return['password']
    # Retorna os dados do usuário logado com sucesso.
    return jsonify(user_data_to_return)

# Define a rota '/api/user/theme' que aceita requisições do tipo PUT (usado para atualizar dados existentes).
@app.route('/api/user/theme', methods=['PUT'])
def save_theme():
    # Obtém os dados JSON da requisição.
    data = request.get_json()
    # Extrai o e-mail, o tema e o tema de cor dos dados.
    email, theme, colorTheme = data.get('email'), data.get('theme'), data.get('colorTheme')
    # Verifica se o e-mail foi fornecido e se pelo menos um dos temas (theme ou colorTheme) foi enviado.
    if not email or (theme is None and colorTheme is None):
        # Se não, retorna um erro.
        return jsonify({"error": "Faltam informações para salvar o tema."}), 400
    # Lê o banco de dados de usuários.
    users_db = read_json_file(USERS_FILE, {})
    # Verifica se o usuário (e-mail) existe no banco de dados.
    if email in users_db:
        # Se um novo 'theme' foi fornecido, atualiza o tema do usuário.
        if theme is not None:
            users_db[email]['theme'] = theme
        # Se um novo 'colorTheme' foi fornecido, atualiza o tema de cor do usuário.
        if colorTheme is not None:
            users_db[email]['colorTheme'] = colorTheme
        # Salva as alterações no arquivo JSON.
        write_json_file(USERS_FILE, users_db)
        # Retorna uma mensagem de sucesso.
        return jsonify({"message": "Tema salvo com sucesso!"})
    # Se o usuário não foi encontrado, retorna um erro 404 (Not Found).
    return jsonify({"error": "Usuário não encontrado."}), 404

# Define a rota '/api/kpis' que aceita requisições do tipo GET (para buscar dados).
@app.route('/api/kpis', methods=['GET'])
def get_kpis():
    # Obtém os dados do inversor (do cache ou do arquivo).
    df = get_inverter_data()
    # Se os dados não puderam ser carregados ou o DataFrame está vazio, retorna um erro.
    if df is None or df.empty: return jsonify({"error": "Não foi possível carregar os dados do inversor"}), 500
    # Calcula a geração total encontrando o valor máximo na coluna 'Total Generation(kWh)'.
    total_generation = df['Total Generation(kWh)'].max()
    # Pega a data de hoje.
    today = datetime.now().date()
    # Cria um objeto datetime para o início do dia de hoje (meia-noite).
    start_of_today = datetime.combine(today, datetime.min.time())
    # Filtra o DataFrame para obter apenas os dados de hoje.
    today_data = df[df['Time'] >= start_of_today]
    # Inicializa a variável de geração de hoje como zero.
    generation_today = 0
    # Verifica se há dados para o dia de hoje.
    if not today_data.empty:
        # A geração de hoje é a diferença entre o maior e o menor valor de 'Total Generation(kWh)' no período de hoje.
        generation_today = today_data['Total Generation(kWh)'].max() - today_data['Total Generation(kWh)'].min()
        # --- NOVA LINHA: Simula o consumo atual da casa ---
    house_load_kw = random.uniform(0.3, 2.5) # Simula um consumo entre 300W e 2.5kW
    # Retorna os KPIs, AGORA INCLUINDO o consumo da casa.
    return jsonify({
        "todayGenKwh": generation_today, 
        "totalGenKwh": total_generation,
        "houseLoadKw": house_load_kw  
    })

# Define a rota '/api/generation/history' que aceita requisições GET.
@app.route('/api/generation/history', methods=['GET'])
def get_generation_history():
    # Obtém os dados do inversor.
    df = get_inverter_data()
    # Se os dados não puderam ser carregados, retorna um erro.
    if df is None or df.empty: return jsonify({"error": "Não foi possível carregar os dados do inversor"}), 500
    # Encontra o registro de tempo mais recente no DataFrame.
    end_time = df['Time'].max()
    # Calcula o tempo de início como 24 horas antes do tempo final.
    start_time = end_time - timedelta(hours=24)
    # Filtra o DataFrame para incluir apenas os dados das últimas 24 horas. '.copy()' evita avisos do pandas.
    recent_data = df[(df['Time'] >= start_time) & (df['Time'] <= end_time)].copy()
    # Define a coluna 'Time' como o índice do DataFrame, o que é necessário para reamostragem de tempo.
    recent_data.set_index('Time', inplace=True)
    # Reamostra os dados de 'Power(W)' em intervalos de 1 hora ('h'), calculando a média para cada hora.
    # '.fillna(0)' preenche quaisquer horas sem dados com o valor 0.
    hourly_generation = recent_data['Power(W)'].resample('h').mean().fillna(0)
    # Retorna os dados formatados para um gráfico:
    # - "labels": as horas do dia (ex: '09h', '10h').
    # - "generation_kw": a lista de valores de geração em kW (dividido por 1000) e arredondado para 2 casas decimais.
    return jsonify({"labels": hourly_generation.index.strftime('%Hh').tolist(), "generation_kw": (hourly_generation / 1000).round(2).tolist()})

# Define a rota '/api/reports/monthly' que aceita requisições GET.
@app.route('/api/reports/monthly', methods=['GET'])
def get_monthly_report():
    # Verifica se o caminho para o arquivo de relatório mensal foi encontrado.
    if not MONTHLY_DATA_FILE: return jsonify({"error": "Arquivo de relatório mensal não configurado ou não encontrado."}), 500
    # Inicia um bloco 'try' para lidar com erros de leitura do arquivo.
    try:
        # Lê o arquivo CSV do relatório mensal.
        # - skiprows=20: Pula as primeiras 20 linhas.
        # - skipfooter=1: Pula a última linha.
        # - engine='python': Usa o motor de parsing Python, que é mais flexível e suporta 'skipfooter'.
        df = pd.read_csv(MONTHLY_DATA_FILE, delimiter=';', skiprows=20, encoding='latin1', skipfooter=1, engine='python')
        # Renomeia as colunas para nomes mais simples e padronizados.
        df.rename(columns={'Generation(kWh)': 'generation', 'Date': 'date'}, inplace=True)
        # Converte a coluna 'generation' para um tipo numérico, substituindo vírgulas por pontos.
        df['generation'] = pd.to_numeric(df['generation'].astype(str).str.replace(',', '.'), errors='coerce')
        # Remove linhas onde 'date' ou 'generation' sejam nulos ou inválidos.
        df.dropna(subset=['date', 'generation'], inplace=True)
        # Seleciona apenas as colunas 'date' e 'generation' e as converte para uma lista de dicionários.
        report_data = df[['date', 'generation']].to_dict(orient='records')
        # Retorna os dados do relatório em formato JSON.
        return jsonify(report_data)
    # Captura qualquer exceção que ocorra durante o processo.
    except Exception as e:
        # Retorna uma mensagem de erro detalhada.
        return jsonify({"error": f"Erro ao processar arquivo de relatório: {e}"}), 500

# Define a rota '/api/devices' que aceita requisições GET (para listar dispositivos).
@app.route('/api/devices', methods=['GET'])
def get_devices():
    # Obtém o parâmetro 'email' da URL da requisição (ex: /api/devices?email=teste@email.com).
    user_email = request.args.get('email')
    # Se o e-mail não for fornecido, retorna um erro.
    if not user_email: return jsonify({"error": "E-mail do usuário é necessário"}), 400
    # Lê o banco de dados de dispositivos.
    devices_db = read_json_file(DEVICES_FILE, {})
    # Obtém a lista de dispositivos para o e-mail do usuário, ou uma lista vazia se o usuário não tiver dispositivos.
    user_devices = devices_db.get(user_email, [])
    # Retorna a lista de dispositivos do usuário em formato JSON.
    return jsonify(user_devices)

# Define a rota '/api/devices' que aceita requisições POST (para adicionar um novo dispositivo).
@app.route('/api/devices', methods=['POST'])
def add_device():
    # Obtém os dados JSON da requisição.
    data = request.get_json()
    # Extrai as informações do novo dispositivo.
    user_email, name, room, type = data.get('email'), data.get('name'), data.get('room'), data.get('type')
    # Verifica se todos os campos necessários foram fornecidos.
    if not all([user_email, name, room, type]): return jsonify({"error": "Todos os campos são obrigatórios"}), 400
    # Lê o banco de dados de dispositivos.
    devices_db = read_json_file(DEVICES_FILE, {})
    # Obtém a lista de dispositivos existente para este usuário.
    user_devices = devices_db.get(user_email, [])
    # Cria um dicionário para o novo dispositivo com um ID único gerado por uuid4.
    new_device = {"id": str(uuid.uuid4()), "name": name, "room": room, "type": type, "on": False, "watts": 0}
    # Adiciona o novo dispositivo à lista de dispositivos do usuário.
    user_devices.append(new_device)
    # Atualiza o banco de dados com a nova lista de dispositivos para este usuário.
    devices_db[user_email] = user_devices
    # Salva as alterações no arquivo JSON.
    write_json_file(DEVICES_FILE, devices_db)
    # Retorna os dados do dispositivo recém-criado com o status 201 (Created).
    return jsonify(new_device), 201

# Define uma rota para um dispositivo específico usando seu ID, que aceita requisições PUT (para atualizar).
@app.route('/api/devices/<string:device_id>', methods=['PUT'])
def toggle_device(device_id):
    # Obtém os dados JSON da requisição.
    data = request.get_json()
    # Extrai o e-mail do usuário e o novo estado ('on') do dispositivo.
    user_email, new_state = data.get('email'), data.get('on')
    # Verifica se o e-mail ou o novo estado estão faltando.
    if not user_email or new_state is None: return jsonify({"error": "Faltam dados para atualizar o dispositivo"}), 400
    # Lê o banco de dados de dispositivos.
    devices_db = read_json_file(DEVICES_FILE, {})
    # Obtém a lista de dispositivos do usuário.
    user_devices = devices_db.get(user_email, [])
    # Inicializa uma flag para verificar se o dispositivo foi encontrado.
    device_found = False
    # Itera sobre a lista de dispositivos do usuário.
    for device in user_devices:
        # Verifica se o ID do dispositivo atual corresponde ao ID da URL.
        if device['id'] == device_id:
            # Atualiza o estado 'on' do dispositivo.
            device['on'] = new_state
            # Atualiza a potência ('watts') com base no novo estado e no tipo do dispositivo.
            device['watts'] = device['on'] * (200 if device['type'] == 'appliance' else 900 if device['type'] == 'climate' else 60)
            # Marca que o dispositivo foi encontrado.
            device_found = True
            # Interrompe o loop, pois o dispositivo já foi encontrado e atualizado.
            break
    # Se o loop terminar e o dispositivo não for encontrado, retorna um erro 404.
    if not device_found: return jsonify({"error": "Dispositivo não encontrado"}), 404
    # Atualiza o banco de dados com a lista de dispositivos modificada.
    devices_db[user_email] = user_devices
    # Salva as alterações no arquivo JSON.
    write_json_file(DEVICES_FILE, devices_db)
    # Retorna uma mensagem de sucesso.
    return jsonify({"message": "Dispositivo atualizado"})

# Define uma rota para um dispositivo específico usando seu ID, que aceita requisições DELETE.
@app.route('/api/devices/<string:device_id>', methods=['DELETE'])
def delete_device(device_id):
    # Obtém o e-mail do usuário dos parâmetros da URL.
    user_email = request.args.get('email')
    # Se o e-mail não for fornecido, retorna um erro.
    if not user_email: return jsonify({"error": "E-mail do usuário é necessário"}), 400
    # Lê o banco de dados de dispositivos.
    devices_db = read_json_file(DEVICES_FILE, {})
    # Obtém a lista de dispositivos do usuário.
    user_devices = devices_db.get(user_email, [])
    # Armazena o número inicial de dispositivos para verificar se algum foi removido.
    initial_len = len(user_devices)
    # Cria uma nova lista contendo todos os dispositivos, exceto aquele cujo ID corresponde ao fornecido.
    user_devices = [d for d in user_devices if d['id'] != device_id]
    # Se o comprimento da lista não mudou, significa que o dispositivo não foi encontrado.
    if len(user_devices) == initial_len: return jsonify({"error": "Dispositivo não encontrado"}), 404
    # Atualiza o banco de dados com a nova lista (sem o dispositivo removido).
    devices_db[user_email] = user_devices
    # Salva as alterações no arquivo JSON.
    write_json_file(DEVICES_FILE, devices_db)
    # Retorna uma mensagem de sucesso.
    return jsonify({"message": "Dispositivo removido"})

# Define a rota '/api/user' que aceita requisições DELETE (para excluir a conta de um usuário).
@app.route('/api/user', methods=['DELETE'])
def delete_user():
    # 1. Obter os dados (e-mail e senha para confirmação) da requisição.
    data = request.get_json()
    # Extrai o e-mail e a senha.
    email = data.get('email')
    password = data.get('password')

    # Verifica se e-mail e senha foram fornecidos.
    if not email or not password:
        # Retorna um erro se estiverem faltando.
        return jsonify({"error": "E-mail e senha são obrigatórios para exclusão"}), 400

    # 2. Ler os bancos de dados de usuários e dispositivos.
    users_db = read_json_file(USERS_FILE, {})
    devices_db = read_json_file(DEVICES_FILE, {})

    # Obtém os dados do usuário a ser excluído.
    user = users_db.get(email)

    # 3. VERIFICAÇÃO DE SEGURANÇA: Checa se o usuário existe e se a senha está correta.
    if not user or not check_password_hash(user.get('password'), password):
        # Usamos a mesma mensagem de erro do login para não informar qual campo estava errado.
        return jsonify({"error": "Credenciais inválidas."}), 401

    # 4. Se a senha estiver correta, proceder com a exclusão.
    try:
        # Remover a entrada do usuário do dicionário de usuários.
        del users_db[email]
        # Salvar o dicionário de usuários atualizado no arquivo.
        write_json_file(USERS_FILE, users_db)

        # Verificar se o usuário tinha dispositivos associados.
        if email in devices_db:
            # Se sim, remover a entrada de dispositivos desse usuário.
            del devices_db[email]
            # Salvar o dicionário de dispositivos atualizado no arquivo.
            write_json_file(DEVICES_FILE, devices_db)

        # Retorna uma mensagem de sucesso com o status HTTP 200 (OK).
        return jsonify({"message": "Usuário e todos os seus dados foram removidos com sucesso."}), 200

    # Captura qualquer erro inesperado que possa ocorrer durante a exclusão.
    except Exception as e:
        # Retorna uma mensagem de erro do servidor.
        return jsonify({"error": f"Ocorreu um erro ao remover o usuário: {e}"}), 500

#simula a carga da bateria para o grafico e o trquinho la em cima
bateria_simulada = random.randint(1,100)

@app.route('/api/battery/status', methods=['GET'])
def get_battery_status():
    """
    Endpoint para fornecer o status atual da bateria.
    Em um cenário real, este valor viria de um sensor ou da API do inversor/bateria.
    Para este exemplo, vamos simular um valor fixo.
    """
    try:
        # Simula a bateria
        charged_percentage = bateria_simulada
        
        # Calcula a porcentagem vazia.
        empty_percentage = 100.0 - charged_percentage

        now = datetime.now()
        is_charging = 9 <= now.hour < 16
        
        if is_charging:
            fluxo_watts = random.randint(500, 2500)
            status_texto = "Carregando"
        else:
            fluxo_watts = random.randint(-1500, -300) 
            status_texto = "Descarregando"


        battery_data = {
            "charged_percentage": charged_percentage,
            "empty_percentage": empty_percentage,
            "labels": ["Carga", "Vazio"],
            "fluxo_watts": fluxo_watts,
            "status_texto": status_texto
        }

        battery_data = {
            "charged_percentage": charged_percentage,
            "empty_percentage": empty_percentage,
            "labels": ["Carga", "Vazio"],
            "fluxo_watts": fluxo_watts,
            "status_texto": status_texto
        }

        capacidade_total_kwh = 13.5
        energia_armazenada_kwh = round((charged_percentage / 100) * capacidade_total_kwh, 1)

        # CORREÇÃO: Adicionando a nova chave ao dicionário
        battery_data['energia_kwh'] = energia_armazenada_kwh
        
        return jsonify(battery_data)
    except Exception as e:
        return jsonify({"error": f"Erro ao obter dados da bateria: {e}"}), 500
@app.route('/api/ask-agent', methods=['POST'])
def ask_agent():
    try:
        data = request.get_json()
        question = data.get("question", "")

        if not question:
            return jsonify({"error": "Você precisa enviar uma pergunta no campo 'question'"}), 400

        # Pega os dados de KPIs do endpoint
        kpis_response = get_kpis()
        if isinstance(kpis_response, Response):
            kpis = json.loads(kpis_response.get_data(as_text=True))
        else:
            kpis = kpis_response

        todayGen = kpis.get("todayGenKwh", 0)
        totalGen = kpis.get("totalGenKwh", 0)
        houseLoad = kpis.get("houseLoadKw", 0)

        # Contexto enviado pro Gemini
        contexto = (
            f"Dados de energia solar e consumo:\n"
            f"- Geração hoje: {todayGen:.2f} kWh\n"
            f"- Geração total: {totalGen:.2f} kWh\n"
            f"- Consumo atual da casa: {houseLoad:.2f} kW\n\n"
            f"Pergunta do usuário: {question}"
        )

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            f"""
            Você é um assistente de energia solar e IoT.
            Sempre responda em **Markdown bem formatado**:
            - Use negrito para valores importantes
            - Use listas com "•"
            - Adicione emojis quando fizer sentido (🌞 ⚡ 📉 📈)
            - Resuma em até 6 linhas para ficar fácil de ler

            {contexto}
            """
        )

        return jsonify({"answer": response.text})

    except Exception as e:
        return jsonify({"error": f"Erro do agente: {e}"}), 500


# --- INICIALIZAÇÃO DO SERVIDOR ---

# Este bloco de código só é executado quando o script é rodado diretamente (não quando é importado).
if __name__ == '__main__':
    # Inicia o servidor de desenvolvimento do Flask.
    # - debug=True: ativa o modo de depuração, que mostra erros detalhados no navegador e reinicia o servidor automaticamente quando o código é alterado.
    # - port=5000: especifica que o servidor deve rodar na porta 5000.
    app.run(debug=True, port=5000)
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Nome do arquivo de dados
DATA_FILE = 'data/dispositivos.json'

def ler_dispositivos():
    """Lê os dispositivos do arquivo JSON."""
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def salvar_dispositivos(dispositivos):
    """Salva os dispositivos no arquivo JSON."""
    with open(DATA_FILE, 'w') as f:
        json.dump(dispositivos, f, indent=4)

@app.route('/api/dispositivos', methods=['POST'])
def cadastrar_dispositivo():
    dados = request.get_json()
    dispositivos = ler_dispositivos()
    
    # Simplesmente usamos o tamanho da lista para gerar um ID
    novo_id = str(len(dispositivos) + 1)
    
    novo_dispositivo = {
        'id': novo_id,
        'nome': dados['nome'],
        'estado': 'desligado'
    }
    
    dispositivos.append(novo_dispositivo)
    salvar_dispositivos(dispositivos)
    
    return jsonify(novo_dispositivo), 201

@app.route('/api/dispositivos', methods=['GET'])
def listar_dispositivos():
    dispositivos = ler_dispositivos()
    return jsonify(dispositivos)

@app.route('/api/dispositivos/<id>', methods=['PUT'])
def alterar_estado_dispositivo(id):
    dados = request.get_json()
    dispositivos = ler_dispositivos()
    
    for dispositivo in dispositivos:
        if dispositivo['id'] == id:
            dispositivo['estado'] = dados['estado']
            salvar_dispositivos(dispositivos)
            return jsonify(dispositivo)
            
    return jsonify({'erro': 'Dispositivo não encontrado'}), 404

@app.route('/api/dispositivos/<id>', methods=['DELETE'])
def descadastrar_dispositivo(id):
    dispositivos = ler_dispositivos()
    dispositivos_atuais = [d for d in dispositivos if d['id'] != id]
    
    if len(dispositivos_atuais) == len(dispositivos):
        return jsonify({'erro': 'Dispositivo não encontrado'}), 404
        
    salvar_dispositivos(dispositivos_atuais)
    return jsonify({'mensagem': 'Dispositivo removido com sucesso'})

if __name__ == '__main__':
    app.run(debug=True)
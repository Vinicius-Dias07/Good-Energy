"""
Exemplo de como obter dados de inversores da API SEMS GoodWe

Este arquivo demonstra:
1. Como fazer login na API SEMS
2. Como obter dados de inversores de uma estação
3. Como processar e exibir os dados
4. Exemplo com dados simulados para demonstração
"""

import aiohttp
import asyncio
import json
from datetime import datetime
from sems_portal_api import login_to_sems, get_monitor_detail, set_region, is_authenticated

async def obter_dados_inversores(station_id: str):
    """
    Função principal para obter dados de inversores
    
    Args:
        station_id (str): ID da estação de energia
    
    Returns:
        dict: Dados dos inversores ou None se houver erro
    """
    
    print(f"🔌 Obtendo dados de inversores para estação: {station_id}")
    print("-" * 60)
    
    set_region('eu')
    
    async with aiohttp.ClientSession() as session:
        # 1. Login na API
        print("1️⃣ Fazendo login na API SEMS...")
        
        login_result = await login_to_sems(
            session, 
            "demo@goodwe.com", 
            "GoodweSems123!@#"
        )
        
        if not login_result.get('success'):
            print("❌ Falha no login")
            print(f"   Erro: {login_result.get('error', 'Erro desconhecido')}")
            return None
        
        print("✅ Login realizado com sucesso!")
        
        # 2. Obter dados de monitoramento da estação
        print(f"\n2️⃣ Obtendo dados da estação {station_id}...")
        
        monitor_result = await get_monitor_detail(session, station_id)
        
        if not monitor_result.get('success'):
            print("❌ Falha ao obter dados da estação")
            print(f"   Erro: {monitor_result.get('error', 'Erro desconhecido')}")
            return None
        
        print("✅ Dados obtidos com sucesso!")
        
        # 3. Processar dados dos inversores
        data = monitor_result.get('data', {})
        inverters = data.get('inverter', [])
        
        if not inverters:
            print("⚠️ Nenhum inversor encontrado nesta estação")
            return None
        
        print(f"📊 Encontrados {len(inverters)} inversores")
        
        # 4. Processar cada inversor
        inversores_processados = []
        
        for i, inverter in enumerate(inverters):
            print(f"\n🔌 Processando Inversor {i+1}...")
            
            inverter_data = inverter.get('d', {})
            
            # Extrair dados principais
            dados_inversor = {
                'id': inverter_data.get('id', f'inverter_{i+1}'),
                'modelo': inverter_data.get('model', 'N/A'),
                'status': inverter_data.get('warning', 'N/A'),
                'ultima_atualizacao': inverter_data.get('last_refresh_time', 'N/A'),
                
                # Dados de produção
                'producao_hoje_kwh': inverter_data.get('eDay', 0),
                'producao_total_kwh': inverter_data.get('eTotal', 0),
                'potencia_atual_w': inverter_data.get('pac', 0),
                
                # Dados técnicos DC
                'tensao_dc_v': inverter_data.get('vdc1', 0),
                'corrente_dc_a': inverter_data.get('idc1', 0),
                
                # Dados técnicos AC
                'tensao_ac_v': inverter_data.get('vac1', 0),
                'corrente_ac_a': inverter_data.get('iac1', 0),
                
                # Outros dados
                'temperatura_c': inverter_data.get('temp', 0),
                'frequencia_hz': inverter_data.get('fac', 0),
                'eficiencia_percent': inverter_data.get('efficiency', 0)
            }
            
            inversores_processados.append(dados_inversor)
            
            # Exibir dados do inversor
            print(f"   ID: {dados_inversor['id']}")
            print(f"   Modelo: {dados_inversor['modelo']}")
            print(f"   Status: {dados_inversor['status']}")
            print(f"   Produção hoje: {dados_inversor['producao_hoje_kwh']} kWh")
            print(f"   Potência atual: {dados_inversor['potencia_atual_w']} W")
            print(f"   Tensão DC: {dados_inversor['tensao_dc_v']} V")
            print(f"   Tensão AC: {dados_inversor['tensao_ac_v']} V")
            print(f"   Temperatura: {dados_inversor['temperatura_c']} °C")
        
        return {
            'estacao_id': station_id,
            'timestamp': datetime.now().isoformat(),
            'total_inversores': len(inversores_processados),
            'inversores': inversores_processados
        }

def exibir_resumo_dados(dados_inversores):
    """Exibe um resumo dos dados dos inversores"""
    
    if not dados_inversores:
        print("❌ Nenhum dado disponível")
        return
    
    print(f"\n📊 RESUMO DOS DADOS")
    print("=" * 50)
    print(f"Estação: {dados_inversores['estacao_id']}")
    print(f"Total de inversores: {dados_inversores['total_inversores']}")
    print(f"Timestamp: {dados_inversores['timestamp']}")
    
    # Calcular totais
    total_producao_hoje = sum(inv['producao_hoje_kwh'] for inv in dados_inversores['inversores'])
    total_producao_total = sum(inv['producao_total_kwh'] for inv in dados_inversores['inversores'])
    total_potencia_atual = sum(inv['potencia_atual_w'] for inv in dados_inversores['inversores'])
    
    print(f"\n⚡ PRODUÇÃO TOTAL:")
    print(f"   Hoje: {total_producao_hoje:.2f} kWh")
    print(f"   Total: {total_producao_total:.2f} kWh")
    print(f"   Potência atual: {total_potencia_atual:.0f} W")

def exemplo_com_dados_simulados():
    """Exemplo usando dados simulados para demonstração"""
    
    print("\n🎭 EXEMPLO COM DADOS SIMULADOS")
    print("=" * 50)
    
    # Dados simulados de inversores
    dados_simulados = {
        'estacao_id': 'demo-station-001',
        'timestamp': datetime.now().isoformat(),
        'total_inversores': 2,
        'inversores': [
            {
                'id': 'INV-001',
                'modelo': 'GW5000-NS',
                'status': 'Normal',
                'ultima_atualizacao': '2024-01-15 14:30:00',
                'producao_hoje_kwh': 25.5,
                'producao_total_kwh': 1250.8,
                'potencia_atual_w': 3200,
                'tensao_dc_v': 380.5,
                'corrente_dc_a': 8.4,
                'tensao_ac_v': 230.2,
                'corrente_ac_a': 13.9,
                'temperatura_c': 45.2,
                'frequencia_hz': 50.0,
                'eficiencia_percent': 96.8
            },
            {
                'id': 'INV-002',
                'modelo': 'GW5000-NS',
                'status': 'Normal',
                'ultima_atualizacao': '2024-01-15 14:30:00',
                'producao_hoje_kwh': 23.8,
                'producao_total_kwh': 1180.3,
                'potencia_atual_w': 2950,
                'tensao_dc_v': 375.8,
                'corrente_dc_a': 7.8,
                'tensao_ac_v': 229.8,
                'corrente_ac_a': 12.8,
                'temperatura_c': 43.1,
                'frequencia_hz': 50.0,
                'eficiencia_percent': 97.2
            }
        ]
    }
    
    # Exibir dados simulados
    for i, inverter in enumerate(dados_simulados['inversores']):
        print(f"\n🔌 Inversor {i+1}: {inverter['id']}")
        print(f"   Modelo: {inverter['modelo']}")
        print(f"   Status: {inverter['status']}")
        print(f"   Produção hoje: {inverter['producao_hoje_kwh']} kWh")
        print(f"   Potência atual: {inverter['potencia_atual_w']} W")
        print(f"   Tensão DC: {inverter['tensao_dc_v']} V")
        print(f"   Tensão AC: {inverter['tensao_ac_v']} V")
        print(f"   Temperatura: {inverter['temperatura_c']} °C")
        print(f"   Eficiência: {inverter['eficiencia_percent']}%")
    
    # Exibir resumo
    exibir_resumo_dados(dados_simulados)
    
    return dados_simulados

async def main():
    """Função principal de exemplo"""
    
    print("🔌 EXEMPLO DE OBTENÇÃO DE DADOS DE INVERSORES")
    print("=" * 60)
    
    # Exemplo 1: Tentar obter dados reais (pode falhar com conta demo)
    print("\n1️⃣ TENTANDO DADOS REAIS DA API:")
    station_id = "demo-station-001"  # Substitua pelo ID real da sua estação
    dados_reais = await obter_dados_inversores(station_id)
    
    if dados_reais:
        exibir_resumo_dados(dados_reais)
    else:
        print("⚠️ Não foi possível obter dados reais (normal com conta demo)")
    
    # Exemplo 2: Dados simulados para demonstração
    print("\n2️⃣ EXEMPLO COM DADOS SIMULADOS:")
    dados_simulados = exemplo_com_dados_simulados()
    
    # Exemplo 3: Como usar os dados
    print("\n3️⃣ COMO USAR OS DADOS:")
    print("""
# Exemplo de código para usar os dados dos inversores:

async def monitorar_inversores():
    # Obter dados
    dados = await obter_dados_inversores("SEU_STATION_ID")
    
    if dados:
        for inverter in dados['inversores']:
            # Verificar se a produção está boa
            if inverter['producao_hoje_kwh'] > 20:
                print(f"✅ {inverter['id']}: Produção boa ({inverter['producao_hoje_kwh']} kWh)")
            else:
                print(f"⚠️ {inverter['id']}: Produção baixa ({inverter['producao_hoje_kwh']} kWh)")
            
            # Verificar temperatura
            if inverter['temperatura_c'] > 50:
                print(f"🔥 {inverter['id']}: Temperatura alta ({inverter['temperatura_c']} °C)")
            
            # Verificar eficiência
            if inverter['eficiencia_percent'] < 95:
                print(f"📉 {inverter['id']}: Eficiência baixa ({inverter['eficiencia_percent']}%)")

# Executar monitoramento
asyncio.run(monitorar_inversores())
    """)

if __name__ == "__main__":
    print("🚀 Iniciando exemplo de dados de inversores...")
    asyncio.run(main())

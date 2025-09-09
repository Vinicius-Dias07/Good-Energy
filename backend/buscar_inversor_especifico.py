"""
Busca por um inversor específico usando dados da interface SEMS
Inversor: GW3000-DNS-30
SN: 53000DSC22CW0141
Checkcode: 056900
"""

import aiohttp
import asyncio
import json
from datetime import datetime
from sems_portal_api import login_to_sems, get_monitor_detail, set_region, is_authenticated

async def buscar_inversor_por_serial():
    """
    Busca o inversor específico usando diferentes estratégias
    """
    
    print("🔍 BUSCA POR INVERSOR ESPECÍFICO")
    print("=" * 60)
    print("Inversor: GW3000-DNS-30")
    print("SN: 53000DSC22CW0141")
    print("Checkcode: 056900")
    print("=" * 60)
    
    set_region('eu')
    
    async with aiohttp.ClientSession() as session:
        # 1. Login
        print("\n1️⃣ Fazendo login...")
        login_result = await login_to_sems(session, "demo@goodwe.com", "GoodweSems123!@#")
        
        if not login_result.get('success'):
            print("❌ Falha no login")
            return None
        
        print("✅ Login realizado com sucesso!")
        token = login_result['token']
        uid = login_result['data'].get('uid', '')
        timestamp = login_result['data'].get('timestamp', int(time.time() * 1000))
        
        # 2. Estratégias de busca
        estrategias = [
            # Estratégia 1: Usar o SN como station_id
            {
                'nome': 'SN como Station ID',
                'station_id': '53000DSC22CW0141',
                'descricao': 'Usando o número de série como ID da estação'
            },
            # Estratégia 2: Usar checkcode
            {
                'nome': 'Checkcode como Station ID',
                'station_id': '056900',
                'descricao': 'Usando o checkcode como ID da estação'
            },
            # Estratégia 3: Usar modelo
            {
                'nome': 'Modelo como Station ID',
                'station_id': 'GW3000-DNS-30',
                'descricao': 'Usando o modelo como ID da estação'
            },
            # Estratégia 4: Tentar diferentes combinações
            {
                'nome': 'SN com prefixo',
                'station_id': 'INV-53000DSC22CW0141',
                'descricao': 'SN com prefixo INV-'
            },
            {
                'nome': 'SN com sufixo',
                'station_id': '53000DSC22CW0141-INV',
                'descricao': 'SN com sufixo -INV'
            },
            # Estratégia 5: Tentar obter lista de estações primeiro
            {
                'nome': 'Buscar lista de estações',
                'station_id': 'LIST_STATIONS',
                'descricao': 'Tentar obter lista de estações disponíveis'
            }
        ]
        
        print(f"\n2️⃣ Testando {len(estrategias)} estratégias de busca...")
        
        for i, estrategia in enumerate(estrategias):
            print(f"\n🔍 Estratégia {i+1}: {estrategia['nome']}")
            print(f"   Descrição: {estrategia['descricao']}")
            print(f"   Station ID: {estrategia['station_id']}")
            print("-" * 40)
            
            if estrategia['station_id'] == 'LIST_STATIONS':
                # Tentar obter lista de estações
                await tentar_obter_lista_estacoes(session, token, uid, timestamp)
            else:
                # Tentar obter dados da estação
                await tentar_obter_dados_estacao(session, estrategia['station_id'])
        
        # 3. Tentar endpoints alternativos
        print(f"\n3️⃣ Testando endpoints alternativos...")
        await testar_endpoints_alternativos(session, token, uid, timestamp)

async def tentar_obter_lista_estacoes(session, token, uid, timestamp):
    """Tenta obter lista de estações disponíveis"""
    
    endpoints = [
        "/api/v1/Station/GetStationList",
        "/api/v1/PowerStation/GetStationList",
        "/api/v1/PowerStation/GetPowerStationList",
        "/api/v1/Station/GetList",
        "/api/v1/Inverter/GetInverterList",
        "/api/v1/Inverter/GetList"
    ]
    
    for endpoint in endpoints:
        print(f"   🔍 Testando: {endpoint}")
        
        url = f"https://eu.semsportal.com{endpoint}"
        token_header = {
            "version": "v2.1.0",
            "client": "web",
            "language": "en",
            "timestamp": timestamp,
            "uid": uid,
            "token": token
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Token': json.dumps(token_header),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            # Tenta GET
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if not data.get('hasError') and data.get('data'):
                        print(f"   ✅ Sucesso com GET!")
                        print(f"   📊 Dados: {json.dumps(data, indent=2)[:300]}...")
                        
                        # Procurar pelo SN específico nos dados
                        if '53000DSC22CW0141' in str(data):
                            print(f"   🎯 ENCONTRADO! SN encontrado nos dados!")
                            return data
                        break
            
            # Tenta POST
            async with session.post(url, json={}, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if not data.get('hasError') and data.get('data'):
                        print(f"   ✅ Sucesso com POST!")
                        print(f"   📊 Dados: {json.dumps(data, indent=2)[:300]}...")
                        
                        # Procurar pelo SN específico nos dados
                        if '53000DSC22CW0141' in str(data):
                            print(f"   🎯 ENCONTRADO! SN encontrado nos dados!")
                            return data
                        break
                        
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")

async def tentar_obter_dados_estacao(session, station_id):
    """Tenta obter dados de uma estação específica"""
    
    try:
        monitor_result = await get_monitor_detail(session, station_id)
        
        if monitor_result.get('success'):
            print("   ✅ Dados obtidos com sucesso!")
            data = monitor_result.get('data', {})
            
            # Procurar pelo inversor específico
            inverters = data.get('inverter', [])
            if inverters:
                print(f"   📊 Inversores encontrados: {len(inverters)}")
                
                for i, inverter in enumerate(inverters):
                    inverter_data = inverter.get('d', {})
                    
                    # Verificar se é o inversor que estamos procurando
                    sn = inverter_data.get('id', '')
                    model = inverter_data.get('model', '')
                    
                    print(f"   🔌 Inversor {i+1}:")
                    print(f"      ID/SN: {sn}")
                    print(f"      Modelo: {model}")
                    
                    # Verificar se é o inversor correto
                    if ('53000DSC22CW0141' in sn or 
                        'GW3000-DNS-30' in model or
                        '056900' in str(inverter_data)):
                        
                        print(f"   🎯 INVERSOR ENCONTRADO!")
                        print(f"      ✅ SN: {sn}")
                        print(f"      ✅ Modelo: {model}")
                        print(f"      ✅ Status: {inverter_data.get('warning', 'N/A')}")
                        print(f"      ✅ Produção hoje: {inverter_data.get('eDay', 0)} kWh")
                        print(f"      ✅ Produção total: {inverter_data.get('eTotal', 0)} kWh")
                        print(f"      ✅ Potência atual: {inverter_data.get('pac', 0)} W")
                        print(f"      ✅ Tensão AC: {inverter_data.get('vac1', 0)} V")
                        print(f"      ✅ Corrente AC: {inverter_data.get('iac1', 0)} A")
                        print(f"      ✅ Frequência: {inverter_data.get('fac', 0)} Hz")
                        print(f"      ✅ Temperatura: {inverter_data.get('temp', 0)} °C")
                        
                        return inverter_data
            else:
                print("   ⚠️ Nenhum inversor encontrado")
        else:
            error = monitor_result.get('error', 'Erro desconhecido')
            print(f"   ❌ Erro: {error}")
            
    except Exception as e:
        print(f"   ❌ Exceção: {str(e)}")

async def testar_endpoints_alternativos(session, token, uid, timestamp):
    """Testa endpoints alternativos para buscar inversores"""
    
    # Endpoints específicos para inversores
    inverter_endpoints = [
        "/api/v1/Inverter/GetInverterDetail",
        "/api/v1/Inverter/GetInverterInfo", 
        "/api/v1/Inverter/GetInverterData",
        "/api/v1/Inverter/GetInverterStatus",
        "/api/v1/Inverter/GetInverterMonitor",
        "/api/v1/Device/GetInverterList",
        "/api/v1/Device/GetInverterDetail"
    ]
    
    for endpoint in inverter_endpoints:
        print(f"   🔍 Testando: {endpoint}")
        
        url = f"https://eu.semsportal.com{endpoint}"
        token_header = {
            "version": "v2.1.0",
            "client": "web",
            "language": "en",
            "timestamp": timestamp,
            "uid": uid,
            "token": token
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Token': json.dumps(token_header),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Diferentes payloads para testar
        payloads = [
            {"serialNumber": "53000DSC22CW0141"},
            {"sn": "53000DSC22CW0141"},
            {"inverterId": "53000DSC22CW0141"},
            {"deviceId": "53000DSC22CW0141"},
            {"checkcode": "056900"},
            {"model": "GW3000-DNS-30"},
            {}
        ]
        
        for payload in payloads:
            try:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        if not data.get('hasError'):
                            print(f"   ✅ Sucesso com payload: {payload}")
                            print(f"   📊 Dados: {json.dumps(data, indent=2)[:300]}...")
                            
                            # Procurar pelo SN específico
                            if '53000DSC22CW0141' in str(data):
                                print(f"   🎯 ENCONTRADO! SN encontrado nos dados!")
                                return data
                        else:
                            print(f"   ⚠️ Erro na API: {data.get('msg', 'N/A')}")
                    else:
                        print(f"   ❌ HTTP {response.status}")
                        
            except Exception as e:
                print(f"   ❌ Exceção: {str(e)}")

async def main():
    """Função principal"""
    
    print("🚀 Iniciando busca pelo inversor específico...")
    print("📋 Dados do inversor:")
    print("   Modelo: GW3000-DNS-30")
    print("   SN: 53000DSC22CW0141") 
    print("   Checkcode: 056900")
    print("   Potência: 3 kW")
    print("   Produção total: 8170.5 kWh")
    
    resultado = await buscar_inversor_por_serial()
    
    if resultado:
        print("\n🎉 INVERSOR ENCONTRADO COM SUCESSO!")
        print("📊 Dados obtidos:")
        print(json.dumps(resultado, indent=2))
    else:
        print("\n⚠️ Inversor não encontrado")
        print("💡 Possíveis causas:")
        print("   - Conta demo não tem acesso a estações reais")
        print("   - Inversor não está associado à conta")
        print("   - IDs ou endpoints podem ter mudado")
        print("   - Necessário usar conta real com estações reais")

if __name__ == "__main__":
    import time
    asyncio.run(main())

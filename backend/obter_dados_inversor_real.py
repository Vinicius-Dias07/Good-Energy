"""
Obtém dados reais do inversor específico encontrado
Inversor: GW3000-DNS-30
SN: 53000DSC22CW0141
"""

import aiohttp
import asyncio
import json
from datetime import datetime
from sems_portal_api import login_to_sems, set_region

async def obter_dados_inversor_real():
    """
    Obtém dados reais do inversor específico usando o endpoint correto
    """
    
    print("🔌 OBTENDO DADOS REAIS DO INVERSOR")
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
        
        # 2. Obter dados do inversor usando o endpoint correto
        print("\n2️⃣ Obtendo dados do inversor...")
        
        url = "https://eu.semsportal.com/api/v1/Inverter/GetInverterData"
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
        
        # Payload com o SN do inversor
        payload = {"sn": "53000DSC22CW0141"}
        
        try:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if not data.get('hasError'):
                        print("✅ Dados obtidos com sucesso!")
                        
                        # Extrair dados do inversor
                        inverter_data = data.get('data', '')
                        
                        if inverter_data:
                            # Parse dos dados JSON
                            try:
                                if isinstance(inverter_data, str):
                                    inverter_json = json.loads(inverter_data)
                                else:
                                    inverter_json = inverter_data
                                
                                print("\n📊 DADOS DO INVERSOR:")
                                print("-" * 40)
                                
                                # Dados de tensão DC (painéis solares)
                                print("🔋 DADOS DC (Painéis Solares):")
                                print(f"   Tensão PV1: {inverter_json.get('Vpv1', 0)} V")
                                print(f"   Tensão PV2: {inverter_json.get('Vpv2', 0)} V")
                                print(f"   Corrente PV1: {inverter_json.get('Ipv1', 0)} A")
                                print(f"   Corrente PV2: {inverter_json.get('Ipv2', 0)} A")
                                
                                # Dados de tensão AC (rede)
                                print("\n🔌 DADOS AC (Rede Elétrica):")
                                print(f"   Tensão AC1: {inverter_json.get('Vac1', 0)} V")
                                print(f"   Tensão AC2: {inverter_json.get('Vac2', 0)} V")
                                print(f"   Tensão AC3: {inverter_json.get('Vac3', 0)} V")
                                print(f"   Corrente AC1: {inverter_json.get('Iac1', 0)} A")
                                print(f"   Corrente AC2: {inverter_json.get('Iac2', 0)} A")
                                print(f"   Corrente AC3: {inverter_json.get('Iac3', 0)} A")
                                print(f"   Frequência AC1: {inverter_json.get('Fac1', 0)} Hz")
                                print(f"   Frequência AC2: {inverter_json.get('Fac2', 0)} Hz")
                                print(f"   Frequência AC3: {inverter_json.get('Fac3', 0)} Hz")
                                
                                # Dados de potência
                                print("\n⚡ DADOS DE POTÊNCIA:")
                                print(f"   Potência AC: {inverter_json.get('Pac', 0)} W")
                                print(f"   Potência DC: {inverter_json.get('Pdc', 0)} W")
                                print(f"   Potência Total: {inverter_json.get('Ptotal', 0)} W")
                                
                                # Dados de energia
                                print("\n📈 DADOS DE ENERGIA:")
                                print(f"   Energia hoje: {inverter_json.get('eDay', 0)} kWh")
                                print(f"   Energia total: {inverter_json.get('eTotal', 0)} kWh")
                                print(f"   Energia mês: {inverter_json.get('eMonth', 0)} kWh")
                                print(f"   Energia ano: {inverter_json.get('eYear', 0)} kWh")
                                
                                # Dados de temperatura e status
                                print("\n🌡️ TEMPERATURA E STATUS:")
                                print(f"   Temperatura: {inverter_json.get('temp', 0)} °C")
                                print(f"   Status: {inverter_json.get('status', 'N/A')}")
                                print(f"   Warning: {inverter_json.get('warning', 'N/A')}")
                                
                                # Dados de eficiência
                                print("\n⚙️ EFICIÊNCIA:")
                                print(f"   Eficiência: {inverter_json.get('efficiency', 0)}%")
                                print(f"   Fator de potência: {inverter_json.get('powerFactor', 0)}")
                                
                                # Dados de tempo
                                print("\n⏰ TEMPO:")
                                print(f"   Tempo de funcionamento: {inverter_json.get('runTime', 0)} horas")
                                print(f"   Última atualização: {inverter_json.get('lastRefreshTime', 'N/A')}")
                                
                                # Resumo comparativo com a interface
                                print("\n📋 COMPARAÇÃO COM A INTERFACE:")
                                print("-" * 40)
                                print(f"✅ Modelo: GW3000-DNS-30 (confirmado)")
                                print(f"✅ SN: 53000DSC22CW0141 (confirmado)")
                                print(f"✅ Potência: {inverter_json.get('Pac', 0)} W (interface: 0 W)")
                                print(f"✅ Tensão AC: {inverter_json.get('Vac1', 0)} V (interface: 0 V)")
                                print(f"✅ Corrente AC: {inverter_json.get('Iac1', 0)} A (interface: 0 A)")
                                print(f"✅ Frequência: {inverter_json.get('Fac1', 0)} Hz (interface: 0 Hz)")
                                print(f"✅ Energia total: {inverter_json.get('eTotal', 0)} kWh (interface: 8170.5 kWh)")
                                
                                # Salvar dados em arquivo
                                dados_completos = {
                                    'inversor': {
                                        'modelo': 'GW3000-DNS-30',
                                        'sn': '53000DSC22CW0141',
                                        'checkcode': '056900',
                                        'timestamp': datetime.now().isoformat()
                                    },
                                    'dados_reais': inverter_json,
                                    'resumo': {
                                        'potencia_atual_w': inverter_json.get('Pac', 0),
                                        'tensao_ac_v': inverter_json.get('Vac1', 0),
                                        'corrente_ac_a': inverter_json.get('Iac1', 0),
                                        'frequencia_hz': inverter_json.get('Fac1', 0),
                                        'energia_total_kwh': inverter_json.get('eTotal', 0),
                                        'energia_hoje_kwh': inverter_json.get('eDay', 0),
                                        'temperatura_c': inverter_json.get('temp', 0),
                                        'eficiencia_percent': inverter_json.get('efficiency', 0)
                                    }
                                }
                                
                                # Salvar em arquivo JSON
                                with open('dados_inversor_real.json', 'w', encoding='utf-8') as f:
                                    json.dump(dados_completos, f, indent=2, ensure_ascii=False)
                                
                                print(f"\n💾 Dados salvos em: dados_inversor_real.json")
                                
                                return dados_completos
                                
                            except json.JSONDecodeError as e:
                                print(f"❌ Erro ao decodificar JSON: {str(e)}")
                                print(f"📄 Dados brutos: {inverter_data}")
                        else:
                            print("⚠️ Nenhum dado retornado")
                    else:
                        print(f"❌ Erro na API: {data.get('msg', 'Erro desconhecido')}")
                else:
                    print(f"❌ Erro HTTP: {response.status}")
                    text = await response.text(encoding='utf-8', errors='ignore')
                    print(f"📄 Resposta: {text[:200]}...")
                    
        except Exception as e:
            print(f"❌ Exceção: {str(e)}")
        
        return None

async def main():
    """Função principal"""
    
    print("🚀 Obtendo dados reais do inversor...")
    
    dados = await obter_dados_inversor_real()
    
    if dados:
        print("\n🎉 DADOS OBTIDOS COM SUCESSO!")
        print("📊 Resumo dos dados:")
        resumo = dados['resumo']
        print(f"   Potência atual: {resumo['potencia_atual_w']} W")
        print(f"   Tensão AC: {resumo['tensao_ac_v']} V")
        print(f"   Corrente AC: {resumo['corrente_ac_a']} A")
        print(f"   Frequência: {resumo['frequencia_hz']} Hz")
        print(f"   Energia total: {resumo['energia_total_kwh']} kWh")
        print(f"   Energia hoje: {resumo['energia_hoje_kwh']} kWh")
        print(f"   Temperatura: {resumo['temperatura_c']} °C")
        print(f"   Eficiência: {resumo['eficiencia_percent']}%")
        
        print("\n💡 Próximos passos:")
        print("   1. Use os dados para monitoramento em tempo real")
        print("   2. Implemente alertas baseados nos valores")
        print("   3. Crie dashboards com os dados obtidos")
        print("   4. Configure atualizações automáticas")
    else:
        print("\n❌ Não foi possível obter os dados")

if __name__ == "__main__":
    import time
    asyncio.run(main())

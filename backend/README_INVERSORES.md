# Dados de Inversores - API SEMS GoodWe

## 📋 Visão Geral

Este documento explica como obter dados de inversores da API SEMS da GoodWe usando o módulo `sems_portal_api.py`.

## 🔧 Funcionalidades Implementadas

### ✅ Autenticação
- Login automático na API SEMS
- Obtenção de token de autenticação
- Gerenciamento de sessão

### ✅ Obtenção de Dados
- Função `get_monitor_detail()` para obter dados de uma estação
- Processamento de dados de inversores
- Tratamento de erros e validações

## 📁 Arquivos Criados

### `exemplo_inversores.py`
Arquivo principal com exemplos completos de como:
- Fazer login na API
- Obter dados de inversores
- Processar e exibir os dados
- Usar dados simulados para demonstração

### `test_inverter_data.py`
Arquivo de teste que demonstra:
- Teste com múltiplos IDs de estações
- Validação de dados
- Tratamento de erros

### `test_inverter_complete.py`
Arquivo de teste completo que:
- Tenta obter lista de estações primeiro
- Testa diferentes endpoints
- Fornece diagnóstico detalhado

## 🚀 Como Usar

### 1. Exemplo Básico

```python
import aiohttp
import asyncio
from sems_portal_api import login_to_sems, get_monitor_detail, set_region

async def obter_dados_inversores():
    set_region('eu')
    
    async with aiohttp.ClientSession() as session:
        # Login
        login_result = await login_to_sems(session, "demo@goodwe.com", "GoodweSems123!@#")
        
        if login_result.get('success'):
            # Obter dados da estação
            station_id = "SEU_STATION_ID_AQUI"
            monitor_result = await get_monitor_detail(session, station_id)
            
            if monitor_result.get('success'):
                data = monitor_result['data']
                inverters = data.get('inverter', [])
                
                for inverter in inverters:
                    inv_data = inverter.get('d', {})
                    print(f"Inversor: {inv_data.get('id', 'N/A')}")
                    print(f"Produção hoje: {inv_data.get('eDay', 0)} kWh")
                    print(f"Potência atual: {inv_data.get('pac', 0)} W")

# Executar
asyncio.run(obter_dados_inversores())
```

### 2. Exemplo com Tratamento de Erros

```python
async def obter_dados_com_validacao():
    set_region('eu')
    
    async with aiohttp.ClientSession() as session:
        try:
            # Login
            login_result = await login_to_sems(session, "demo@goodwe.com", "GoodweSems123!@#")
            
            if not login_result.get('success'):
                print(f"❌ Erro no login: {login_result.get('error')}")
                return
            
            # Obter dados
            station_id = "SEU_STATION_ID"
            monitor_result = await get_monitor_detail(session, station_id)
            
            if not monitor_result.get('success'):
                print(f"❌ Erro ao obter dados: {monitor_result.get('error')}")
                return
            
            # Processar dados
            data = monitor_result['data']
            inverters = data.get('inverter', [])
            
            if not inverters:
                print("⚠️ Nenhum inversor encontrado")
                return
            
            # Exibir dados
            for i, inverter in enumerate(inverters):
                inv_data = inverter.get('d', {})
                print(f"\n🔌 Inversor {i+1}:")
                print(f"   ID: {inv_data.get('id', 'N/A')}")
                print(f"   Modelo: {inv_data.get('model', 'N/A')}")
                print(f"   Status: {inv_data.get('warning', 'N/A')}")
                print(f"   Produção hoje: {inv_data.get('eDay', 0)} kWh")
                print(f"   Potência atual: {inv_data.get('pac', 0)} W")
                print(f"   Tensão DC: {inv_data.get('vdc1', 0)} V")
                print(f"   Tensão AC: {inv_data.get('vac1', 0)} V")
                print(f"   Temperatura: {inv_data.get('temp', 0)} °C")
                
        except Exception as e:
            print(f"❌ Erro geral: {str(e)}")
```

## 📊 Dados Disponíveis dos Inversores

### Dados Básicos
- `id`: ID único do inversor
- `model`: Modelo do inversor
- `warning`: Status do inversor
- `last_refresh_time`: Última atualização

### Dados de Produção
- `eDay`: Produção de energia hoje (kWh)
- `eTotal`: Produção total de energia (kWh)
- `pac`: Potência atual (W)

### Dados Técnicos DC
- `vdc1`: Tensão DC (V)
- `idc1`: Corrente DC (A)

### Dados Técnicos AC
- `vac1`: Tensão AC (V)
- `iac1`: Corrente AC (A)
- `fac`: Frequência (Hz)

### Outros Dados
- `temp`: Temperatura (°C)
- `efficiency`: Eficiência (%)

## ⚠️ Limitações com Conta Demo

### Problemas Encontrados
1. **Erro 403 Forbidden**: A conta demo não tem acesso a estações reais
2. **IDs de Estações**: Precisam ser IDs válidos de estações reais
3. **Permissões**: Conta demo pode ter limitações de acesso

### Soluções
1. **Use uma conta real**: Registre-se no SEMS Portal com dados reais
2. **Obtenha IDs corretos**: Use os IDs das suas estações reais
3. **Dados simulados**: Use o exemplo com dados simulados para desenvolvimento

## 🔍 Diagnóstico de Problemas

### Erro 403 Forbidden
```
❌ Erro: HTTP 403: Forbidden
💡 Causa: Estação não existe ou sem permissão
```

### Erro "ver is not fund"
```
❌ Erro: ver is not fund
💡 Causa: Parâmetro 'ver' faltando no header
```

### Nenhum inversor encontrado
```
⚠️ Nenhum inversor encontrado nesta estação
💡 Causa: Estação não tem inversores ou dados não disponíveis
```

## 📝 Exemplo de Dados Simulados

Para desenvolvimento e testes, você pode usar dados simulados:

```python
dados_simulados = {
    'estacao_id': 'demo-station-001',
    'inversores': [
        {
            'id': 'INV-001',
            'modelo': 'GW5000-NS',
            'status': 'Normal',
            'producao_hoje_kwh': 25.5,
            'potencia_atual_w': 3200,
            'tensao_dc_v': 380.5,
            'tensao_ac_v': 230.2,
            'temperatura_c': 45.2,
            'eficiencia_percent': 96.8
        }
    ]
}
```

## 🎯 Próximos Passos

1. **Obter conta real**: Registre-se no SEMS Portal
2. **Configurar estações**: Adicione suas estações reais
3. **Obter IDs**: Use os IDs corretos das suas estações
4. **Implementar monitoramento**: Use os dados para monitoramento em tempo real
5. **Adicionar alertas**: Implemente alertas baseados nos dados

## 📚 Recursos Adicionais

- [Documentação oficial SEMS](https://www.semsportal.com)
- [API GoodWe](https://www.goodwe.com)
- [Exemplo completo](exemplo_inversores.py)
- [Testes](test_inverter_data.py)

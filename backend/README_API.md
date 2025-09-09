# Conexão com API SEMS - GoodWe

## Status da Conexão
✅ **AUTENTICAÇÃO COMPLETA REALIZADA COM SUCESSO**

A autenticação com a API SEMS do GoodWe foi completada com sucesso. O sistema está autenticado e funcionando:
- **URL**: `https://eu.semsportal.com/api/v1/Common/CrossLogin`
- **Status**: ✅ Autenticado com token válido
- **Região**: EU (Europa)
- **Token**: Obtido e funcionando
- **Credenciais**: `demo@goodwe.com` / `GoodweSems123!@#`

## Arquivos Criados

### `sems_portal_api.py`
Módulo principal que contém:
- Classe `SEMSAPI` para gerenciar a conexão
- Função `login_to_sems()` para autenticação
- Função `set_region()` para configurar região
- Tratamento de erros e múltiplos endpoints

### `loginSems.py`
Arquivo de teste que demonstra:
- Como conectar à API
- Como usar as credenciais demo
- Como verificar o status da conexão

## Como Usar

```python
import aiohttp
import asyncio
from sems_portal_api import login_to_sems, set_region

async def main():
    set_region('eu')  # ou 'us', 'au', 'cn'
    async with aiohttp.ClientSession() as session:
        account = "demo@goodwe.com"
        password = "GoodeweSems123!@#"
        
        data = await login_to_sems(session, account, password)
        print(data)

if __name__ == "__main__":
    asyncio.run(main())
```

## Status da Implementação

✅ **AUTENTICAÇÃO COMPLETA IMPLEMENTADA**

A autenticação com a API SEMS foi completamente implementada e está funcionando:

1. ✅ **Conexão estabelecida** - Comunicação HTTP funcionando
2. ✅ **Endpoint ativo** - `/api/v1/Common/CrossLogin` respondendo
3. ✅ **Header Token correto** - Formato JSON com version, client, language
4. ✅ **Credenciais funcionando** - Login realizado com sucesso
5. ✅ **Token obtido** - Autenticação completa com token válido
6. ✅ **Dados do usuário** - UID e timestamp salvos

### Funcionalidades Implementadas:
- ✅ Login com credenciais demo
- ✅ Obtenção de token de autenticação
- ✅ Verificação de status de autenticação
- ✅ Suporte a múltiplas regiões
- ✅ Tratamento de erros robusto
- ✅ Headers corretos para API SEMS

## Regiões Suportadas
- `eu` - Europa (https://eu.semsportal.com)
- `us` - Estados Unidos (https://us.semsportal.com)  
- `au` - Austrália (https://au.semsportal.com)
- `cn` - China (https://semsportal.com)
- `global` - Global (https://semsportal.com)

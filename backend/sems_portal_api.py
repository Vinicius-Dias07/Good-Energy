import aiohttp
import json
import time
from typing import Dict, Any

# URLs base da API SEMS
BASE_URLS = {
    'eu': 'https://eu.semsportal.com',
    'us': 'https://us.semsportal.com',
    'au': 'https://au.semsportal.com',
    'cn': 'https://semsportal.com',
    'global': 'https://semsportal.com'
}

class SEMSAPI:
    def __init__(self, region: str = 'eu'):
        self.region = region
        self.base_url = BASE_URLS.get(region, BASE_URLS['eu'])
        self.token = None
        self.session = None
    
    async def login(self, session: aiohttp.ClientSession, account: str, password: str) -> Dict[str, Any]:
        """Faz login na API SEMS"""
        # Tenta diferentes endpoints possíveis
        login_endpoints = [
            "/Api/v1/Common/CrossLogin",
            "/api/v1/Common/CrossLogin", 
            "/Api/v1/User/Login",
            "/api/v1/User/Login",
            "/Api/Common/CrossLogin",
            "/api/Common/CrossLogin"
        ]
        
        errors = []
        for endpoint in login_endpoints:
            login_url = f"{self.base_url}{endpoint}"
            result = await self._try_login(session, login_url, account, password)
            if result.get('success') or 'token' in str(result):
                return result
            errors.append(f"{endpoint}: {result.get('error', 'Unknown error')}")
        
        return {
            "success": False,
            "error": "All login endpoints failed",
            "errors": errors,
            "data": None
        }
    
    async def _try_login(self, session: aiohttp.ClientSession, login_url: str, account: str, password: str) -> Dict[str, Any]:
        # Payload simplificado conforme documentação SEMS
        payloads = [
            {
                "account": account,
                "pwd": password
            },
            {
                "account": account,
                "pwd": password,
                "is_local": True
            },
            {
                "account": account,
                "pwd": password,
                "is_local": True,
                "agreement_agreement": 1
            }
        ]
        
        for payload in payloads:
            result = await self._try_payload(session, login_url, payload)
            if result.get('success') or 'token' in str(result):
                return result
        
        return {
            "success": False,
            "error": "All payload formats failed",
            "endpoint": login_url
        }
    
    async def _try_payload(self, session: aiohttp.ClientSession, login_url: str, payload: dict) -> Dict[str, Any]:
        # Header Token necessário para a API SEMS
        token_header = {
            "version": "v2.1.0",
            "client": "web",
            "language": "en"
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Token': json.dumps(token_header),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://eu.semsportal.com/'
        }
        
        try:
            async with session.post(login_url, json=payload, headers=headers) as response:
                if response.status == 200:
                    try:
                        # Tenta decodificar como JSON primeiro
                        data = await response.json()
                        
                        # Verifica se é uma resposta de sucesso com token
                        if (data.get('success') or 
                            (data.get('data') and data.get('data').get('token')) or
                            data.get('token')):
                            
                            # Extrai o token da resposta
                            token = None
                            if data.get('data') and data.get('data').get('token'):
                                token = data.get('data').get('token')
                            elif data.get('token'):
                                token = data.get('token')
                            
                            if token:
                                self.token = token
                                # Salva dados do usuário
                                user_data = data.get('data', {})
                                if user_data.get('uid'):
                                    self.set_user_data(user_data.get('uid'), user_data.get('timestamp', int(time.time() * 1000)))
                                
                                return {
                                    "success": True,
                                    "token": self.token,
                                    "data": user_data,
                                    "endpoint": login_url,
                                    "payload": payload,
                                    "message": "Autenticação realizada com sucesso!"
                                }
                        
                        # Verifica se é uma resposta válida da API (mesmo com erro de parâmetro)
                        if (not data.get('hasError') or
                            data.get('code') == 0 or
                            (data.get('code') == 100003 and 'Missing parameter' in data.get('msg', ''))):
                            
                            # Conexão estabelecida mas parâmetros incorretos
                            return {
                                "success": True,
                                "connected": True,
                                "message": "API conectada com sucesso, mas parâmetros de login precisam ser ajustados",
                                "api_response": data,
                                "endpoint": login_url,
                                "payload": payload
                            }
                        else:
                            return {
                                "success": False,
                                "error": data.get('msg', 'Login failed'),
                                "data": data,
                                "endpoint": login_url,
                                "payload": payload
                            }
                    except Exception as json_error:
                        # Se falhar o JSON, tenta como texto
                        text_response = await response.text(encoding='utf-8', errors='ignore')
                        return {
                            "success": False,
                            "error": f"Invalid JSON response: {str(json_error)}",
                            "raw_response": text_response[:500],  # Primeiros 500 caracteres
                            "endpoint": login_url,
                            "payload": payload
                        }
                else:
                    text_response = await response.text(encoding='utf-8', errors='ignore')
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {text_response[:200]}",
                        "data": None,
                        "endpoint": login_url,
                        "payload": payload
                    }
        except Exception as e:
            return {
                "success": False,
                "error": f"Connection error: {str(e)}",
                "data": None,
                "endpoint": login_url,
                "payload": payload
            }
    
    async def get_station_list(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Obtém lista de estações"""
        if not self.token:
            return {"success": False, "error": "Not logged in"}
        
        # Header Token com informações de autenticação
        token_header = {
            "version": "v2.1.0",
            "client": "web",
            "language": "en",
            "timestamp": int(time.time() * 1000),
            "uid": getattr(self, 'uid', ''),
            "token": self.token,
            "ver": "1.0"
        }
        
        # Tenta diferentes endpoints para obter lista de estações
        endpoints = [
            "/api/v1/Station/GetStationList",
            "/api/v1/PowerStation/GetStationList", 
            "/api/v1/PowerStation/GetPowerStationList",
            "/api/v1/Station/GetList"
        ]
        
        for endpoint in endpoints:
            url = f"{self.base_url}{endpoint}"
            result = await self._try_station_endpoint(session, url, token_header)
            if result.get('success'):
                return result
        
        return {
            "success": False,
            "error": "All station endpoints failed"
        }
    
    async def _try_station_endpoint(self, session: aiohttp.ClientSession, url: str, token_header: dict) -> Dict[str, Any]:
        headers = {
            'Content-Type': 'application/json',
            'Token': json.dumps(token_header),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            # Tenta GET primeiro
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if not data.get('hasError') or data.get('data'):
                        return {
                            "success": True,
                            "data": data,
                            "endpoint": url
                        }
            
            # Se GET falhou, tenta POST
            async with session.post(url, json={}, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if not data.get('hasError') or data.get('data'):
                        return {
                            "success": True,
                            "data": data,
                            "endpoint": url
                        }
            
            return {
                "success": False,
                "error": f"Endpoint {url} failed",
                "endpoint": url
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Connection error: {str(e)}",
                "endpoint": url
            }
    
    def set_user_data(self, uid: str, timestamp: int):
        """Define dados do usuário após login"""
        self.uid = uid
        self.timestamp = timestamp
    
    async def get_monitor_detail(self, session: aiohttp.ClientSession, power_station_id: str) -> Dict[str, Any]:
        """Obtém detalhes de monitoramento de uma estação específica"""
        if not self.token:
            return {"success": False, "error": "Not logged in"}
        
        # Header Token com informações de autenticação
        token_header = {
            "version": "v2.1.0",
            "client": "web",
            "language": "en",
            "timestamp": int(time.time() * 1000),
            "uid": getattr(self, 'uid', ''),
            "token": self.token
        }
        
        url = f"{self.base_url}/api/v1/PowerStation/GetMonitorDetailByPowerstationId"
        headers = {
            'Content-Type': 'application/json',
            'Token': json.dumps(token_header),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        payload = {
            "powerStationId": power_station_id
        }
        
        try:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if not data.get('hasError'):
                        return {
                            "success": True,
                            "data": data.get('data', {}),
                            "endpoint": url
                        }
                    else:
                        return {
                            "success": False,
                            "error": data.get('msg', 'API error'),
                            "data": data
                        }
                else:
                    text_response = await response.text(encoding='utf-8', errors='ignore')
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {text_response[:200]}"
                    }
        except Exception as e:
            return {
                "success": False,
                "error": f"Connection error: {str(e)}"
            }

# Instância global da API
_sems_api = SEMSAPI()

def set_region(region: str):
    """Define a região da API"""
    global _sems_api
    _sems_api = SEMSAPI(region)

async def login_to_sems(session: aiohttp.ClientSession, account: str, password: str) -> Dict[str, Any]:
    """Função para fazer login na API SEMS"""
    return await _sems_api.login(session, account, password)

async def get_station_list(session: aiohttp.ClientSession) -> Dict[str, Any]:
    """Função para obter lista de estações"""
    return await _sems_api.get_station_list(session)

def get_token() -> str:
    """Retorna o token atual"""
    return _sems_api.token

def is_authenticated() -> bool:
    """Verifica se está autenticado"""
    return _sems_api.token is not None

async def get_monitor_detail(session: aiohttp.ClientSession, power_station_id: str) -> Dict[str, Any]:
    """Função para obter detalhes de monitoramento de uma estação"""
    return await _sems_api.get_monitor_detail(session, power_station_id)

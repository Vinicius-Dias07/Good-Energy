import aiohttp
import asyncio
from sems_portal_api import login_to_sems, set_region

async def main():
    set_region('eu')
    async with aiohttp.ClientSession() as session:
        account = "demo@goodwe.com"
        password = "GoodweSems123!@#"
        
        print("Tentando conectar à API SEMS...")
        print(f"Região: eu")
        print(f"Conta: {account}")
        print("-" * 50)
        
        data = await login_to_sems(session, account, password)
        print("Resposta da API:")
        print(data)
        print("-" * 50)

        if data.get("success") or data.get("token"):
            print("✅ Conectado à API com sucesso!")
            if data.get("token"):
                print(f"Token: {data['token'][:20]}...")
        else:
            print("❌ Falha ao conectar à API")
            if data.get("errors"):
                print("Detalhes dos erros:")
                for error in data["errors"]:
                    print(f"  - {error}")
# ...existing code...

if __name__ == "__main__":
    asyncio.run(main())
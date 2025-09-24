import os
from dotenv import load_dotenv
import google.generativeai as genai

# Carrega variáveis do .env
load_dotenv()

# Funcao para carregar a chave da api do gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class DataAgente:
    def __init__(self, model="gemini-1.5-flash"):
        self.model = model
        self.client = genai.GenerativeModel(self.model)

    def ask(self, question: str) -> str:
        response = self.client.generate_content(
            f"Você é um agente que ajuda em análise de dados de energia solar e IoT. Pergunta: {question}"
        )
        return response.text

from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import json
from datetime import datetime
import random

app = Flask(__name__)
CORS(app)

def calculate_daily_generation():
    """
    Calcula a geração diária de energia a partir do arquivo CSV
    """
    try:
        # Carrega os dados
        df = pd.read_csv("Historical Data Export-20250908015049.csv", skiprows=2,
                        encoding='latin1',
                        sep=';')

        # Converte a coluna 'Time' para datetime e define como índice
        df['Time'] = pd.to_datetime(df['Time'], format='%d.%m.%Y %H:%M:%S')
        df.set_index('Time', inplace=True)

        # Calcula a geração diária
        geracao_max_diaria = df['Total Generation(kWh)'].resample('D').max()
        geracao_min_diaria = df['Total Generation(kWh)'].resample('D').min()
        geracao_diaria = geracao_max_diaria - geracao_min_diaria
        geracao_diaria = geracao_diaria[geracao_diaria >= 0]

        return geracao_diaria
    except Exception as e:
        print(f"Erro ao calcular geração diária: {e}")
        return None
    
import random

#funçao enriquece a geração real da bateria para o front
def enrich_daily_data(geracao_diaria):
    """
    Enriquecer dados de geração com consumo simulado, bateria e importação da rede.
    """
    daily_data = []

    for date, generation in geracao_diaria.items():
        # Simula consumo (70% até 120% da geração)
        consumo_simulado = round(generation * random.uniform(0.7, 1.2), 2)

        # Simula bateria (40% até 100%)
        bateria_simulada = random.randint(40, 100)

        # Se consumo > geração, diferença vem da rede
        grid_import = max(0, round(consumo_simulado - generation, 2))

        # Monta o registro do dia
        daily_data.append({
            "date": date.strftime('%Y-%m-%d'),
            "generation_kwh": round(generation, 2),
            "consumption_kwh": consumo_simulado,
            "battery_pct": bateria_simulada,
            "grid_import_kwh": grid_import
        })

    return daily_data

def calculate_monthly_generation():
    # Carrega os dados para a variavel df
    try:
        df = pd.read_csv("2025_Plant_20250911213350.csv", skiprows=20,
                encoding='latin1',
                sep=';')

        df['Date'] = pd.to_datetime(df['Date'], format='%m.%Y', errors='coerce')

        monthly_generation = df[['Date', 'Generation(kWh)']]
        monthly_generation['Date'] = monthly_generation['Date'].dt.strftime('%m.%Y')

        return monthly_generation.to_dict(orient="records")



    except Exception as e:
        print(f"Erro ao calcular geração mensal: {e}")
        return None

@app.route('/api/daily-generation', methods=['GET'])
def get_daily_generation():
    """
    Retorna a geração diária de energia em formato JSON
    """
    try:
        geracao_diaria = calculate_daily_generation()
        
        if geracao_diaria is None:
            return jsonify({
                "success": False,
                "error": "Erro ao processar dados"
            }), 500

        # Converte para formato JSON estruturado
        daily_data = []
        for date, generation in geracao_diaria.items():
            daily_data.append({
                "date": date.strftime('%Y-%m-%d'),
                "generation_kwh": round(generation, 2),
                "day_of_week": date.strftime('%A'),
                "month": date.strftime('%B'),
                "year": date.year
            })

        # Calcula estatísticas
        stats = {
            "total_days": len(geracao_diaria),
            "total_generation": round(geracao_diaria.sum(), 2),
            "average_daily": round(geracao_diaria.mean(), 2),
            "max_daily": round(geracao_diaria.max(), 2),
            "min_daily": round(geracao_diaria.min(), 2),
            "std_deviation": round(geracao_diaria.std(), 2),
            "period_start": geracao_diaria.index.min().strftime('%Y-%m-%d'),
            "period_end": geracao_diaria.index.max().strftime('%Y-%m-%d')
        }

        # Encontra o melhor e pior dia
        best_day = geracao_diaria.idxmax()
        worst_day = geracao_diaria.idxmin()

        response = {
            "success": True,
            "data": {
                "daily_generation": daily_data,
                "statistics": stats,
                "best_day": {
                    "date": best_day.strftime('%Y-%m-%d'),
                    "generation_kwh": round(geracao_diaria.max(), 2)
                },
                "worst_day": {
                    "date": worst_day.strftime('%Y-%m-%d'),
                    "generation_kwh": round(geracao_diaria.min(), 2)
                }
            },
            "timestamp": datetime.now().isoformat()
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Erro interno: {str(e)}"
        }), 500

@app.route('/api/monthly-generation', methods=['GET'])
def get_monthly_generation():
    """
    Retorna a geração mensal de energia em formato JSON
    """
    try:
        monthly_generation = calculate_monthly_generation()  # lista de dicts: [{ 'Date': 'mm.YYYY', 'Generation(kWh)': ... }, ...]
        if monthly_generation is None:
            return jsonify({
                "success": False,
                "error": "Erro ao processar dados"
            }), 500
        
        monthly_data = []
        for item in monthly_generation:
            monthly_data.append({
                "month": item['Date'],
                "generation_kwh": item['Generation(kWh)']
            })
        

        response = {
            "success": True,
            "data": {
                "monthly_generation": monthly_data,
            },
            "timestamp": datetime.now().isoformat()
        }
        return jsonify(response)


    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Erro interno: {str(e)}"
        }), 500
    
@app.route('/api/energy', methods=['GET'])
def get_energy_data():
    """
    Retorna geração diária enriquecida com consumo, bateria e grid.
    """
    try:
        geracao_diaria = calculate_daily_generation()
        if geracao_diaria is None:
            return jsonify({"success": False, "error": "Erro ao processar dados"}), 500

        enriched = enrich_daily_data(geracao_diaria)

        response = {
            "success": True,
            "data": enriched,
            "timestamp": datetime.now().isoformat()
        }
        return jsonify(response)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500





app.run()
#aaaaaaaaaaaaaaaaaaaaa
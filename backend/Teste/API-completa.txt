from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import json
from datetime import datetime

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

@app.route('/api/daily-generation/summary', methods=['GET'])
def get_daily_generation_summary():
    """
    Retorna apenas um resumo da geração diária
    """
    try:
        geracao_diaria = calculate_daily_generation()
        
        if geracao_diaria is None:
            return jsonify({
                "success": False,
                "error": "Erro ao processar dados"
            }), 500

        # Últimos 7 dias
        last_7_days = geracao_diaria.tail(7)
        last_7_days_data = []
        for date, generation in last_7_days.items():
            last_7_days_data.append({
                "date": date.strftime('%Y-%m-%d'),
                "generation_kwh": round(generation, 2)
            })

        response = {
            "success": True,
            "data": {
                "last_7_days": last_7_days_data,
                "total_generation": round(geracao_diaria.sum(), 2),
                "average_daily": round(geracao_diaria.mean(), 2),
                "total_days": len(geracao_diaria)
            }
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Erro interno: {str(e)}"
        }), 500

@app.route('/api/load_data_week', methods=['GET'])
def load_data_week():
    """
    Endpoint legado - mantido para compatibilidade
    """
    try:
        geracao_diaria = calculate_daily_generation()
        
        if geracao_diaria is None:
            return jsonify({
                "success": False,
                "error": "Erro ao processar dados"
            }), 500

        # Formato simples para compatibilidade
        result = []
        for date, generation in geracao_diaria.items():
            result.append({
                "date": date.strftime('%Y-%m-%d'),
                "generation": round(generation, 2)
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Erro interno: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
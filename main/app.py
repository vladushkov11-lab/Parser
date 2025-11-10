from flask import Flask, render_template, request, jsonify
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from wb_api import extract_article_from_url, parser_wildbox, get_wb_price, spp
from database.dao import create_products
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/parse', methods=['POST'])
def parse():
    try:
        url = request.json.get('url')
        if not url:
            return jsonify({'error': 'URL не указан'}), 400
            
        # Извлекаем артикул
        art = extract_article_from_url(url)
        if not art:
            return jsonify({'error': 'Артикул не найден в URL'}), 400
        
        # Получаем цену с Wildbox (без СПП)
        price_no_spp_str = parser_wildbox(art)
        if isinstance(price_no_spp_str, dict) and 'error' in price_no_spp_str:
            return jsonify({'error': f'Ошибка Wildbox: {price_no_spp_str["error"]}'}), 500
            
        price_no_spp = int(float(price_no_spp_str))
        
        # Получаем цену с Wildberries (со СПП)
        price_data = get_wb_price(art)
        if not price_data:
            return jsonify({'error': 'Не удалось получить данные с Wildberries'}), 500
            
        price_spp = int(float(price_data["price_spp"]))
        name = price_data["name"]
        
        # Рассчитываем СПП
        percent_spp = spp(price_no_spp, price_spp)
        percent_spp = round(percent_spp, 2)
        percent_spp = float(percent_spp)
        result = {
            "price_spp": price_spp,
            "name": name,
            "price_no_spp": price_no_spp,
            "art": art,
            "percent_spp": f"{percent_spp}%",
            "url": url,
            "success": True
        }
        create_products(name=name, price_no_spp=price_no_spp, price_spp=price_spp, percent_spp=percent_spp)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
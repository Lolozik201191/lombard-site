import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
import ssl
import os

# === КОНФИГУРАЦИЯ ===
# Путь к файлу с ценами (автоматически определится)
PRICES_FILE = os.path.join(os.path.dirname(__file__), 'prices.json')

def get_cbr_rates():
    """Получает учетные цены на драгметаллы с сайта ЦБ РФ"""
    
    # Формируем дату вчерашнего дня
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%d/%m/%Y')
    
    # Список металлов
    metals = [
        {'code': '1', 'name': 'gold', 'title': 'Золото'},
        {'code': '2', 'name': 'silver', 'title': 'Серебро'},
        {'code': '3', 'name': 'platinum', 'title': 'Платина'},
        {'code': '4', 'name': 'palladium', 'title': 'Палладий'}
    ]
    
    prices = {}
    
    for metal in metals:
        url = f"https://www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx/GetDynamicData?fromDate={yesterday}&toDate={yesterday}&metCode={metal['code']}"
        
        try:
            context = ssl._create_unverified_context()
            
            with urllib.request.urlopen(url, context=context, timeout=30) as response:
                data = response.read().decode('utf-8')
                
                import xml.etree.ElementTree as ET
                root = ET.fromstring(data)
                
                for value_tag in root.findall('.//{http://web.cbr.ru/}Value'):
                    if value_tag.text:
                        price = float(value_tag.text)
                        prices[metal['name']] = price
                        print(f"{metal['title']}: {price} ₽")
                        break
                        
        except Exception as e:
            print(f"Ошибка получения {metal['title']}: {e}")
            continue
    
    if not prices:
        print("ОШИБКА: не удалось получить ни одной цены")
        return None
    
    return {
        'gold': prices.get('gold', 0),
        'silver': prices.get('silver', 0),
        'platinum': prices.get('platinum', 0),
        'palladium': prices.get('palladium', 0),
        'date': (datetime.now() - timedelta(days=1)).strftime('%d.%m.%Y')
    }

def save_prices():
    """Сохраняет цены в JSON файл"""
    print("Загружаем цены с сайта ЦБ РФ...")
    prices = get_cbr_rates()
    
    if prices is None:
        return False
    
    response = {
        'status': 'ok',
        'data': prices,
        'updated': datetime.now().isoformat()
    }
    
    try:
        with open(PRICES_FILE, 'w', encoding='utf-8') as f:
            json.dump(response, f, ensure_ascii=False, indent=2)
        print(f"✅ Цены сохранены в {PRICES_FILE}")
        print(f"📅 Дата: {prices['date']}")
        print(f"💰 Золото: {prices['gold']} ₽")
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")
        return False

if __name__ == "__main__":
    save_prices()
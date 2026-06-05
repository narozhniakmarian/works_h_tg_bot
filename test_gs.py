import os
from gs_client import GoogleSheetsClient
from datetime import datetime

def test():
    print("🔍 Перевірка зв'язку з Google Sheets...")
    JSON_KEY = "tgbotworkhours-f15c0ec0bb4d.json"
    SHEET_NAME = "tg_bot_work_hour"
    
    try:
        gs = GoogleSheetsClient(JSON_KEY, SHEET_NAME)
        print(f"✅ Зв'язок встановлено! Таблиця '{SHEET_NAME}' знайдена.")
        
        # Перевірка читання
        print("📂 Читання останніх записів...")
        data = gs.get_monthly_data(datetime.now().month, datetime.now().year)
        print(f"Знайдено записів за цей місяць: {len(data)}")
        
        # Тестовий запис
        print("✍️ Проба запису тестового рядка...")
        test_date = datetime.now().strftime("%d.%m.%Y")
        gs.add_record([test_date, "ТЕСТ", 0, 0, 0, "Тестове підключення"])
        print("✅ Тестовий запис додано! Перевірте таблицю в браузері.")
        
    except Exception as e:
        print(f"❌ Помилка: {e}")

if __name__ == "__main__":
    test()

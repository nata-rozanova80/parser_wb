import sqlite3
import os

DB_PATH = "product.db"


def view_database():
    """Просмотр содержимого базы данных"""

    if not os.path.exists(DB_PATH):
        print(f"❌ Файл {DB_PATH} не найден!")
        print("💡 Убедитесь, что parser_wb.py был запущен")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Получение списка таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        print("=" * 70)
        print("📊 СОДЕРЖИМОЕ БАЗЫ ДАННЫХ")
        print("=" * 70)
        print(f"\n📁 Файл: {DB_PATH}")
        print(f"📋 Таблицы: {[table[0] for table in tables]}\n")

        # Просмотр таблицы product_list
        cursor.execute("SELECT * FROM product_list")
        products = cursor.fetchall()

        if products:
            print("🛍️ ТАБЛИЦА: product_list")
            print("-" * 70)
            print(f"{'ID':<5} | {'Название':<40} | {'Путь к изображению':<20}")
            print("-" * 70)

            for product in products:
                product_id, name, image_path = product
                # Обрезаем длинные названия
                short_name = name[:37] + "..." if len(name) > 40 else name
                short_path = image_path[-17:] if len(image_path) > 20 else image_path
                print(f"{product_id:<5} | {short_name:<40} | {short_path:<20}")

            print("-" * 70)
            print(f"\n✅ Всего товаров: {len(products)}")
        else:
            print("⚠️ Таблица product_list пуста")
            print("💡 Запустите parser_wb.py для заполнения данными")

        conn.close()
        print("\n" + "=" * 70)

    except sqlite3.Error as e:
        print(f"❌ Ошибка базы данных: {e}")
    except Exception as e:
        print(f"❌ Непредвиденная ошибка: {e}")


if __name__ == "__main__":
    view_database()
    input("\n📌 Нажмите Enter для выхода...")

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import sqlite3
import os


def create_database():
    """Создание базы данных и таблицы"""
    conn = sqlite3.connect("product.db")


    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS product_list (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        image_path TEXT NOT NULL
    )
    ''')

    # Очистка старых данных
    cursor.execute("DELETE FROM product_list")
    conn.commit()
    conn.close()
    print("✅ База данных создана и очищена")


def setup_browser():
    """Настройка браузера Chrome"""
    chrome_options = Options()
    # Раскомментируйте следующую строку для работы в фоновом режиме
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    browser = webdriver.Chrome(options=chrome_options)
    browser.maximize_window()
    return browser


def parse_wildberries():
    """Основная функция парсинга"""
    # Создание папки для скриншотов
    if not os.path.exists("screen"):
        os.makedirs("screen")
        print("✅ Папка 'screen' создана")

    # Создание базы данных
    create_database()

    # Подключение к базе данных
    conn = sqlite3.connect("product.db")
    cursor = conn.cursor()

    # Настройка браузера
    browser = setup_browser()

    try:
        # URL для поиска товаров (можете изменить запрос)
        search_query = "ноутбук"  # Измените на нужный запрос
        url = f"https://www.wildberries.ru/catalog/0/search.aspx?search={search_query}"

        print(f"🔍 Открываю страницу: {url}")
        browser.get(url)

        # Ожидание загрузки страницы
        print("⏳ Ожидание загрузки товаров...")
        time.sleep(5)

        # Прокрутка страницы для загрузки товаров
        browser.execute_script("window.scrollTo(0, 1000);")
        time.sleep(2)

        # Поиск товаров
        # ВАЖНО: Селектор может измениться! Проверьте актуальность
        try:
            products = browser.find_elements(By.CSS_SELECTOR, "article.product-card")
        except:
            # Альтернативный селектор
            products = browser.find_elements(By.CLASS_NAME, "product-card")

        if not products:
            print("❌ Товары не найдены. Проверьте селекторы!")
            return

        print(f"✅ Найдено товаров: {len(products)}")

        # Ограничиваем количество товаров
        max_products = min(10, len(products))
        print(f"📦 Будет обработано: {max_products} товаров\n")

        i = 0
        for index in range(max_products):
            try:
                # Повторный поиск элемента (чтобы избежать stale element)
                products = browser.find_elements(By.CSS_SELECTOR, "article.product-card")
                product = products[index]

                # Прокрутка к товару
                browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", product)
                time.sleep(0.5)

                # Извлечение названия товара
                try:
                    name_element = product.find_element(By.CSS_SELECTOR, "h2.product-card__name")
                    name = name_element.text.strip()
                except:
                    try:
                        name_element = product.find_element(By.CLASS_NAME, "product-card__name")
                        name = name_element.text.strip()
                    except:
                        name = f"Товар {i + 1}"

                if not name:
                    name = f"Товар {i + 1}"

                # Путь для сохранения скриншота
                image_path = f"screen/product_{i + 1}.png"

                # Создание скриншота товара
                product.screenshot(image_path)

                # Сохранение в базу данных
                cursor.execute(
                    "INSERT INTO product_list (name, image_path) VALUES (?, ?)",
                    (name, image_path)
                )

                i += 1
                print(f"✅ {i}. {name[:50]}... - сохранено")

                time.sleep(0.5)

            except Exception as e:
                print(f"⚠️ Ошибка при обработке товара {index + 1}: {e}")
                continue

        # Сохранение изменений
        conn.commit()
        print(f"\n✅ Парсинг завершен! Обработано: {i} товаров")
        print(f"📁 Скриншоты сохранены в папке 'screen'")
        print(f"💾 Данные сохранены в базе 'product.db'")

    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")

    finally:
        # Закрытие соединений
        browser.quit()
        conn.close()
        print("\n🔒 Браузер закрыт, соединение с БД завершено")


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 ПАРСЕР WILDBERRIES С SELENIUM")
    print("=" * 60)
    print("\n⚠️ ВАЖНО:")
    print("1. Убедитесь, что Chrome установлен")
    print("2. Селекторы могут измениться - проверьте актуальность")
    print("3. Процесс может занять 1-2 минуты\n")

    input("📌 Нажмите Enter для начала парсинга...")

    parse_wildberries()

    print("\n" + "=" * 60)
    print("✅ РАБОТА ЗАВЕРШЕНА")
    print("=" * 60)

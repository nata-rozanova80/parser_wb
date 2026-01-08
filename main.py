import telebot
from telebot import apihelper
import sqlite3
import os

# ========== ИМПОРТ НАСТРОЕК ==========
try:
    from config import BOT_TOKEN, DB_PATH, CONNECT_TIMEOUT, READ_TIMEOUT
except ImportError:
    print("❌ ОШИБКА: Файл config.py не найден!")
    print("\n📝 Создайте файл config.py со следующим содержимым:")
    print("-" * 60)
    print("BOT_TOKEN = 'ваш_токен_от_BotFather'")
    print("DB_PATH = 'product.db'")
    print("CONNECT_TIMEOUT = 30")
    print("READ_TIMEOUT = 30")
    print("-" * 60)
    exit(1)

# Проверка наличия токена
if not BOT_TOKEN or BOT_TOKEN == 'ВАШ_ТОКЕН_ОТ_BOTFATHER':
    print("❌ ОШИБКА: Токен бота не настроен!")
    print("\n📝 Откройте файл config.py и замените BOT_TOKEN на реальный токен")
    print("💡 Получить токен можно у @BotFather в Telegram")
    exit(1)

# Настройка таймаутов для работы в России
apihelper.CONNECT_TIMEOUT = CONNECT_TIMEOUT
apihelper.READ_TIMEOUT = READ_TIMEOUT

# ========== ИНИЦИАЛИЗАЦИЯ БОТА ==========
bot = telebot.TeleBot(BOT_TOKEN)


# ========== КОМАНДЫ БОТА ==========

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Приветственное сообщение"""
    welcome_text = (
        "👋 Привет! Я бот для показа товаров с Wildberries!\n\n"
        "🛍️ Что я умею:\n"
        "• Показывать товары с фото и названиями\n"
        "• Выводить список всех товаров\n\n"
        "📋 Доступные команды:\n"
        "/product 1 - Показать товар №1\n"
        "/product 2 - Показать товар №2\n"
        "/list - Список всех товаров\n"
        "/help - Подробная справка\n\n"
        "💡 Попробуйте: /list"
    )
    bot.send_message(message.chat.id, welcome_text)


@bot.message_handler(commands=['help'])
def send_help(message):
    """Справка по использованию"""
    help_text = (
        "📖 СПРАВКА ПО ИСПОЛЬЗОВАНИЮ БОТА\n\n"
        "🔹 /start - Начать работу с ботом\n"
        "🔹 /list - Показать все доступные товары\n"
        "🔹 /product [номер] - Показать конкретный товар\n"
        "🔹 /help - Эта справка\n\n"
        "📝 ПРИМЕРЫ:\n"
        "• /product 1 - Первый товар\n"
        "• /product 5 - Пятый товар\n"
        "• /list - Все товары\n\n"
        "❓ Если товар не найден - попробуйте /list\n"
        "для просмотра доступных номеров"
    )
    bot.send_message(message.chat.id, help_text)


@bot.message_handler(commands=['list'])
def list_products(message):
    """Показать список всех товаров"""
    try:
        # Подключение к базе данных
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Получение всех товаров
        cursor.execute("SELECT id, name FROM product_list ORDER BY id")
        products = cursor.fetchall()

        if products:
            response = "📦 СПИСОК ДОСТУПНЫХ ТОВАРОВ:\n"
            response += "=" * 40 + "\n\n"

            for product_id, name in products:
                # Ограничиваем длину названия для читаемости
                short_name = name[:60] + "..." if len(name) > 60 else name
                response += f"🔹 {product_id}. {short_name}\n"

            response += "\n" + "=" * 40
            response += "\n\n💡 Используйте команду:\n/product [номер]\n\n"
            response += "Например: /product 1"

            bot.send_message(message.chat.id, response)
        else:
            bot.send_message(
                message.chat.id,
                "❌ Товары не найдены в базе данных!\n\n"
                "🔧 Возможные причины:\n"
                "1. Парсер еще не запускался\n"
                "2. База данных пуста\n\n"
                "💡 Запустите файл parser_wb.py"
            )

        conn.close()

    except sqlite3.Error as e:
        bot.send_message(
            message.chat.id,
            f"❌ Ошибка базы данных: {e}\n\n"
            "Убедитесь, что файл product.db существует"
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Непредвиденная ошибка: {e}"
        )


@bot.message_handler(commands=['product'])
def send_product(message):
    """Отправка товара по номеру"""
    try:
        # Извлечение ID товара из команды
        command_parts = message.text.split()

        if len(command_parts) < 2:
            bot.send_message(
                message.chat.id,
                "⚠️ Неправильный формат команды!\n\n"
                "📝 Правильно: /product [номер]\n"
                "📌 Пример: /product 1\n\n"
                "💡 Используйте /list для просмотра доступных товаров"
            )
            return

        # Проверка, что ID - это число
        try:
            product_id = int(command_parts[1])
        except ValueError:
            bot.send_message(
                message.chat.id,
                "⚠️ Номер товара должен быть числом!\n\n"
                "✅ Правильно: /product 1\n"
                "❌ Неправильно: /product abc"
            )
            return

        # Подключение к базе данных
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Запрос товара по ID
        cursor.execute(
            "SELECT name, image_path FROM product_list WHERE id = ?",
            (product_id,)
        )
        result = cursor.fetchone()

        if result:
            name, image_path = result

            # Проверка существования файла изображения
            if os.path.exists(image_path):
                # Отправка уведомления о загрузке
                loading_msg = bot.send_message(
                    message.chat.id,
                    "⏳ Загружаю товар..."
                )

                # Отправка фото с названием
                with open(image_path, "rb") as photo:
                    caption = f"🛍️ Товар #{product_id}\n\n{name}"
                    bot.send_photo(
                        message.chat.id,
                        photo,
                        caption=caption
                    )

                # Удаление сообщения о загрузке
                try:
                    bot.delete_message(message.chat.id, loading_msg.message_id)
                except:
                    pass
            else:
                # Если файл не найден, отправляем только название
                bot.send_message(
                    message.chat.id,
                    f"🛍️ Товар #{product_id}\n\n"
                    f"📦 Название: {name}\n\n"
                    f"⚠️ Изображение не найдено\n"
                    f"Путь: {image_path}"
                )
        else:
            # Товар не найден в базе
            bot.send_message(
                message.chat.id,
                f"❌ Товар с номером {product_id} не найден\n\n"
                f"💡 Используйте команду /list для просмотра\n"
                f"доступных товаров"
            )

        conn.close()

    except ValueError:
        bot.send_message(
            message.chat.id,
            "⚠️ Некорректный номер товара!\n\n"
            "Используйте целое число, например: /product 1"
        )
    except sqlite3.Error as e:
        bot.send_message(
            message.chat.id,
            f"❌ Ошибка базы данных: {e}"
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Произошла ошибка: {e}"
        )


@bot.message_handler(func=lambda message: True)
def handle_text(message):
    """Обработка произвольного текста"""
    bot.send_message(
        message.chat.id,
        "❓ Не понимаю эту команду.\n\n"
        "📋 Доступные команды:\n"
        "/start - Начать работу\n"
        "/list - Список товаров\n"
        "/product [номер] - Показать товар\n"
        "/help - Подробная справка"
    )


# ========== ЗАПУСК БОТА ==========
if __name__ == "__main__":
    print("=" * 60)
    print("🤖 TELEGRAM-БОТ ДЛЯ WILDBERRIES")
    print("=" * 60)
    print(f"\n✅ Токен загружен из config.py")
    print(f"📁 База данных: {DB_PATH}")
    print(f"⏱️ Таймауты: Connect={CONNECT_TIMEOUT}s, Read={READ_TIMEOUT}s")
    print("\n⚠️ ВАЖНО: Включите VPN для работы в России!")
    print("\n🚀 Бот запускается...\n")

    try:
        print("✅ Бот запущен и готов к работе!")
        print("📱 Откройте Telegram и найдите вашего бота")
        print("💬 Отправьте /start для начала работы")
        print("\n⌨️ Нажмите Ctrl+C для остановки бота\n")
        print("-" * 60)

        bot.infinity_polling(timeout=30, long_polling_timeout=30)

    except KeyboardInterrupt:
        print("\n\n🛑 Бот остановлен пользователем")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        print("\n💡 ВОЗМОЖНЫЕ РЕШЕНИЯ:")
        print("1. Проверьте, что VPN включен")
        print("2. Убедитесь, что токен правильный (config.py)")
        print("3. Проверьте подключение к интернету")
        print("=" * 60)

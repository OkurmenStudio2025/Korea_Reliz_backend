import telebot
from telebot import types
import requests
import os
# from io import BytesIO


TOKEN = '7928953840:AAGnh5kDj_DSF04NyPsPJvL5z2dQti6_fJQ'
API_URL = 'https://koreacenter.kg/api/products/product/'
CATEGORY_API_URL = 'https://koreacenter.kg/api/products/categories/'
MARKA_API_URL = 'https://koreacenter.kg/api/products/Marka/'

bot = telebot.TeleBot(TOKEN)

user_data = {}

START, TITLE, PRICE, DESCRIPTION, ARTIKUL, YEAR, IN_STOCK, CONDITION, MARKA, MODEL, SPARE_PART_NUMBER, GENERATION, CATEGORY, PRODUCT_IMAGES, CATEGORY_NAME = range(15)

admin = [5573835432, 5469335222]

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id in admin:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Создать продукт')
        btn2 = types.KeyboardButton('Добавить марки')
        btn3 = types.KeyboardButton('Создание модели')
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'у вас нет доступ к этому боту')

@bot.message_handler(func=lambda message: message.text == 'Создание модели')
def handle_create_marka(message):
    print('marka')
    bot.send_message(message.chat.id, 'Введите название новой марки:')
    bot.register_next_step_handler(message, add_marka_name)

@bot.message_handler(func=lambda message: message.text == 'Добавить марки')
def handle_add_category(message):
    user_data[message.from_user.id] = {}
    bot.send_message(message.chat.id, 'Введите название новой категории:')
    # bot.send_message(message.chat.id, 'Пожалуйста, отправьте изображение.')
    bot.register_next_step_handler(message, add_category_imagee)


@bot.message_handler(func=lambda message: message.text == 'Создать продукт')
def handle_create_product(message):
    user_data[message.from_user.id] = {}
    bot.send_message(message.chat.id, 'Привет! Давайте начнем создание нового продукта. Назовите продукт.')
    bot.register_next_step_handler(message, receive_title)

def receive_title(message):
    user_data[message.from_user.id]['title'] = message.text
    bot.send_message(message.chat.id, 'Введите цену продукта:')
    bot.register_next_step_handler(message, receive_price)

def receive_price(message):
    user_data[message.from_user.id]['price'] = message.text
    bot.send_message(message.chat.id, 'Введите описание продукта:')
    bot.register_next_step_handler(message, receive_description)

def receive_description(message):
    user_data[message.from_user.id]['description'] = message.text
    bot.send_message(message.chat.id, 'Введите артикул продукта:')
    bot.register_next_step_handler(message, receive_artikul)

# def receive_artikul(message):
#     user_data[message.from_user.id]['artikul'] = message.text
#     bot.send_message(message.chat.id, 'Введите год выпуска:')
#     bot.register_next_step_handler(message, receive_year)

def receive_artikul(message):
    user_data[message.from_user.id]['artikul'] = message.text
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    btn1 = types.KeyboardButton('В наличии')
    btn2 = types.KeyboardButton('Нет в наличии')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, 'Продукт в наличии?', reply_markup=markup)
    bot.register_next_step_handler(message, handle_in_stock)

def handle_in_stock(message):
    if message.text == 'В наличии':
        user_data[message.from_user.id]['in_stock'] = 'yes'
    else:
        user_data[message.from_user.id]['in_stock'] = 'no'
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    btn1 = types.KeyboardButton('Новый')
    btn2 = types.KeyboardButton('Б/У')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, 'Выберите состояние продукта:', reply_markup=markup)
    bot.register_next_step_handler(message, handle_condition)

def handle_condition(message):
    condition = message.text
    user_data[message.from_user.id]['choice'] = 'Новый' if condition == 'Новый' else 'Б/У'
    
    try:
        response = requests.get(MARKA_API_URL)
        response.raise_for_status()
        marka = response.json()
    except requests.RequestException as e:
        bot.send_message(message.chat.id, f'Ошибка при получении модель: {e}')
        return

    # Создаем клавиатуру с множественным выбором
    markup = types.InlineKeyboardMarkup()
    for cat in marka:
        markup.add(types.InlineKeyboardButton(cat['marka'], callback_data=f"marka:{cat['marka']}"))
    markup.add(types.InlineKeyboardButton("✅ Завершить выбор", callback_data="finish_selection"))

    # Отправляем сообщение с клавиатурой
    bot.send_message(message.chat.id, 'Выберите одну или несколько модель и нажмите "Завершить выбор":', reply_markup=markup)

# Обработчик нажатий кнопок
@bot.callback_query_handler(func=lambda call: call.data.startswith('marka') or call.data == 'finish_selection')
def handle_marka_selection(call):
    user_id = call.from_user.id

    # Инициализируем список марок, если его еще нет
    if 'selected_marka' not in user_data[user_id]:
        user_data[user_id]['selected_marka'] = []

    if call.data.startswith('marka'):
        # Добавляем или удаляем марку из выбора
        marka = call.data.split(':')[1]
        if marka in user_data[user_id]['selected_marka']:
            user_data[user_id]['selected_marka'].remove(marka)
            bot.answer_callback_query(call.id, f"Марка {marka} удалена из выбора.")
        else:
            user_data[user_id]['selected_marka'].append(marka)
            bot.answer_callback_query(call.id, f"Марка {marka} добавлена в выбор.")
    elif call.data == 'finish_selection':
        # Завершаем выбор
        selected_marka = user_data[user_id].get('selected_marka', [])
        if not selected_marka:
            bot.answer_callback_query(call.id, "Вы не выбрали ни одной модель.")
            return

        bot.send_message(call.message.chat.id, f"Вы выбрали модель: {', '.join(selected_marka)}")
        bot.send_message(call.message.chat.id, 'Введите номер запасной части:')
        bot.register_next_step_handler(call.message, receive_spare_part_number)

        # Удаляем клавиатуру
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

def receive_spare_part_number(message):
    user_data[message.from_user.id]['spare_part_number'] = message.text
    bot.send_message(message.chat.id, 'Введите поколение:')
    bot.register_next_step_handler(message, receive_generation)

def receive_generation(message):
    user_id = message.from_user.id

    # Убедимся, что пользовательские данные существуют
    if user_id not in user_data:
        user_data[user_id] = {}

    # Сохраняем поколение
    user_data[user_id]['generation'] = message.text

    # Получаем категории с API
    try:
        response = requests.get(CATEGORY_API_URL)
        response.raise_for_status()
        categories = response.json()
    except requests.RequestException as e:
        bot.send_message(message.chat.id, f'Ошибка при получении категорий: {e}')
        return

    # Создаем клавиатуру с категориями
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    category_map = {}  # Сопоставление названий категорий с их ID
    for cat in categories:
        markup.add(types.KeyboardButton(cat['category']))
        category_map[cat['category']] = cat['id']

    # Сохраняем карту категорий
    user_data[user_id]['category_map'] = category_map

    # Отправляем клавиатуру пользователю
    bot.send_message(message.chat.id, 'Выберите категорию:', reply_markup=markup)

    # Регистрируем следующий шаг
    bot.register_next_step_handler(message, handle_category_selection)


def handle_category_selection(message):
    user_id = message.from_user.id
    category_name = message.text

    # Убедимся, что пользователь выбрал существующую категорию
    category_map = user_data[user_id].get('category_map', {})
    if category_name in category_map:
        category_id = category_map[category_name]
        user_data[user_id]['category'] = category_id
        user_data[user_id]['marka'] = message.text
        bot.send_message(
            message.chat.id,
            f'Вы выбрали категорию: {category_name} (ID: {category_id}). Теперь отправьте изображения (до 4 изображений).'
        )
        # Переходим к следующему шагу
        bot.register_next_step_handler(message, receive_images)
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, выберите категорию из предложенного списка.')
        receive_generation(message)  # Показываем категории снова

@bot.message_handler(content_types=['photo', 'document'])
def receive_images(message):
    user_id = message.from_user.id

    # Убедимся, что пользовательские данные существуют
    if user_id not in user_data:
        user_data[user_id] = {}

    # Убедимся, что ключ 'image_urls' существует
    if 'image_urls' not in user_data[user_id]:
        user_data[user_id]['image_urls'] = []

    try:
        # Обработка фото
        if message.content_type == 'photo':
            file_info = bot.get_file(message.photo[-1].file_id)
            file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
        
        # Обработка документа
        elif message.content_type == 'document':
            file_info = bot.get_file(message.document.file_id)
            file_extension = message.document.file_name.split('.')[-1].lower()
            
            if file_extension not in ['jpg', 'jpeg', 'png']:
                bot.send_message(message.chat.id, "Поддерживаются только изображения формата JPG, JPEG или PNG.")
                return

            file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"

        # Добавление URL файла в список
        user_data[user_id]['image_urls'].append(file_url)

        # Сообщение о количестве загруженных изображений
        bot.send_message(
            message.chat.id,
            f"Загружено {len(user_data[user_id]['image_urls'])} изображение(ий). Вы можете загрузить ещё {4 - len(user_data[user_id]['image_urls'])} или отправить 'Готово' для завершения."
        )

        # Если загружено 4 изображения, автоматически завершаем процесс
        if len(user_data[user_id]['image_urls']) == 4:
            finalize_product_creation(message)
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при обработке изображения или документа: {e}")


@bot.message_handler(content_types=['text'])
def finalize_product_creation(message):
    user_id = message.from_user.id

    # Завершаем процесс только если пользователь отправил "Готово"
    if message.text.strip().lower() != 'готово':
        return

    # Проверяем, есть ли загруженные изображения
    if not user_data[user_id].get('image_urls'):
        bot.send_message(message.chat.id, "Вы не загрузили ни одного изображения.")
        return

    bot.send_message(message.chat.id, "Завершаем процесс создания продукта.")

    # Подготовка данных продукта
    product_data = {
        'title': user_data[user_id].get('title'),
        'price': user_data[user_id].get('price'),
        'description': user_data[user_id].get('description'),
        'artikul': user_data[user_id].get('artikul'),
        'year': user_data[user_id].get('year'),
        'in_stock': user_data[user_id].get('in_stock'),
        'model': ', '.join(user_data[user_id].get('selected_marka', [])),
        'marka': user_data[user_id].get('marka'),
        'spare_part_number': user_data[user_id].get('spare_part_number'),
        'generation': user_data[user_id].get('generation'),
        'choice': user_data[user_id].get('choice'),
        'category': user_data[user_id].get('category'),
    }

    # Подготовка файлов
    files = {
        f'image{i+1}': (
            f'Image{i+1}.jpg',
            requests.get(user_data[user_id]['image_urls'][i]).content,
            'image/jpeg'
        ) for i in range(len(user_data[user_id]['image_urls']))
    }

    try:
        response = requests.post(API_URL, data=product_data, files=files)
        response.raise_for_status()
        bot.send_message(message.chat.id, "Продукт успешно создан!")
        start(message)  # Переход к функции start
    except requests.RequestException as e:
        bot.send_message(
            message.chat.id,
            f"Произошла ошибка при создании продукта: {e}\nОтвет сервера: {response.text if response else 'Нет ответа'}"
        )


# @bot.message_handler(func=lambda message: message.text == 'Добавить категорию')
# def handle_add_category(message):
#     user_data[message.from_user.id] = {}
#     bot.send_message(message.chat.id, 'Введите название новой категории:')
#     # bot.send_message(message.chat.id, 'Пожалуйста, отправьте изображение.')
#     bot.register_next_step_handler(message, add_category_imagee)

def add_category_imagee(message):
    user_id = message.from_user.id

    # Проверяем и инициализируем структуру user_data для пользователя
    if user_id not in user_data:
        user_data[user_id] = {'category_name': '', 'image_category_urls': []}

    user_data[user_id]['category_name'] = message.text
    bot.send_message(message.chat.id, 'Теперь отправьте изображение')
    bot.register_next_step_handler(message, add_category_image)

@bot.message_handler(content_types=['photo', 'document'])
def add_category_image(message):
    user_id = message.from_user.id

    # Проверяем и инициализируем структуру user_data для пользователя
    if user_id not in user_data:
        user_data[user_id] = {'category_name': '', 'image_category_urls': []}

    try:
        # Обработка фото
        if message.content_type == 'photo':
            if not message.photo:
                bot.send_message(message.chat.id, "Ошибка: изображение отсутствует.")
                return

            file_info = bot.get_file(message.photo[-1].file_id)
            if not file_info.file_path:
                bot.send_message(message.chat.id, "Ошибка: не удалось получить путь к файлу.")
                return

            file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
            file_extension = 'jpg'
            mine_type = 'image/jpeg'

        # Обработка документа
        elif message.content_type == 'document':
            if not message.document:
                bot.send_message(message.chat.id, "Ошибка: документ отсутствует.")
                return

            file_info = bot.get_file(message.document.file_id)
            if not file_info.file_path:
                bot.send_message(message.chat.id, "Ошибка: не удалось получить путь к файлу.")
                return

            file_extension = message.document.file_name.split('.')[-1].lower()
            if file_extension not in ['jpg', 'jpeg', 'png']:
                bot.send_message(message.chat.id, "Поддерживаются только изображения формата JPG, JPEG или PNG.")
                return
            mine_type = f'image/{file_extension}'
            file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"

        # Добавляем URL файла в список
        if 'image_category_urls' not in user_data[user_id]:
            user_data[user_id]['image_category_urls'] = []

        user_data[user_id]['image_category_urls'].append(file_url)
        bot.send_message(message.chat.id, "Изображение успешно обработано!")

    except Exception as e:
        # Логируем и отправляем сообщение об ошибке
        print(f"Ошибка при обработке изображения или документа: {e}")
        bot.send_message(message.chat.id, f"Ошибка при обработке изображения или документа: {e}")
        return

    # Подготовка данных для отправки в API
    category_name = user_data[user_id].get('category_name')
    if not category_name:
        bot.send_message(message.chat.id, "Название категории отсутствует. Укажите категорию перед загрузкой изображений.")
        return
    
    try:
        # Проверяем данные перед отправкой
        category_name = user_data[user_id].get('category_name')
        if not category_name:
            bot.send_message(message.chat.id, "Название категории отсутствует. Укажите категорию.")
            return

        image_url = user_data[user_id]['image_category_urls'][-1]
        bot.send_message(message.chat.id, f"Проверка URL изображения: {image_url}")

        # Загружаем изображение
        image_content = requests.get(image_url).content
        if not image_content:
            bot.send_message(message.chat.id, "Ошибка: не удалось загрузить содержимое изображения.")
            return
        print(category_name)
        # Отправляем POST-запрос
        response = requests.post(
            CATEGORY_API_URL,
            data={'category': category_name},
            files={'image': (f'image.{file_extension}', image_content, mine_type)}
        )
        response.raise_for_status()  # Поднимет исключение, если статус код >= 400
        bot.send_message(message.chat.id, 'Категория добавлена успешно!')

    except requests.RequestException as e:
        # Логируем ошибку и отправляем сообщение
        print(f"Ошибка при добавлении категории: {e}")
        bot.send_message(message.chat.id, f'Ошибка при добавлении категории: {e}')



# @bot.message_handler(func=lambda message: message.text == 'Создание марки')
# def handle_create_marka(message):
#     print('marka')
#     bot.send_message(message.chat.id, 'Введите название новой марки:')
#     bot.register_next_step_handler(message, add_marka_name)

def add_marka_name(message):
    # Выводим отладочное сообщение для проверки
    print(f"User {message.from_user.id} is entering marka name: {message.text}")

    marka_name = message.text
    try:
        # Проверка, чтобы не создавать марку несколько раз
        if message.from_user.id in user_data and 'marka' in user_data[message.from_user.id]:
            bot.send_message(message.chat.id, 'Вы уже добавили марку.')
            return

        response = requests.post(MARKA_API_URL, json={"marka": marka_name})
        response.raise_for_status()

        # Сохраняем информацию о марке в user_data для предотвращения повторного запроса
        if message.from_user.id not in user_data:
            user_data[message.from_user.id] = {}

        user_data[message.from_user.id]['marka'] = marka_name
        bot.send_message(message.chat.id, f'Марка "{marka_name}" успешно создана!')
    except requests.RequestException as e:
        bot.send_message(message.chat.id, f'Ошибка при создании марки: {e}')
        # bot.register_next_step_handler(message, start)

if __name__ == '__main__':
    bot.polling(none_stop=True)


import telebot, buttons, db

from geopy import Nominatim

# Подключение к боту
my_bot = telebot.TeleBot('6086832562:AAH2Mtc0j_qmtOfpFHIUfKKB8erXMKyk7O0')
# Работа с локацией
geolocator = Nominatim(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Chrome/109.0.0.0 '
                                  'Safari/537.36')
# Временные данные для того чтоьбы работали Inline кнопки
users = {}


# Прописываем обработку команды /start
@my_bot.message_handler(commands=['start'])
def start_message(message):
    global user_id
    user_id = message.from_user.id
    check_user = db.checker(user_id)
    # Проверка на наличие пользователя в базе данных
    if check_user:
        products = db.get_pr_name_id()
        my_bot.send_message(user_id, 'Добро пожаловать!', reply_markup=telebot.types.ReplyKeyboardRemove()),
        my_bot.send_message(user_id, 'Выберите пункт меню:', reply_markup=buttons.main_menu_buttons(products))

        print(products)
    else:
        my_bot.send_message(user_id, 'Здравствуйте запишите ваше имя!')
        # Перевести на этап получения имени
        my_bot.register_next_step_handler(message, get_name)


# Этап получения имени
def get_name(message):
    user_name = message.text
    my_bot.send_message(user_id, 'Отлично, а теперь отправьте свой номер!',
                        reply_markup=buttons.num_button())
    # Перевести на этап получения номера
    my_bot.register_next_step_handler(message, get_number, user_name)


# Админ панель
@my_bot.message_handler(commands=['admin'])
def start_admin(message):
    if user_id == 123456789:
        pass


# Этап получения номера
def get_number(message, user_name):
    # Если пользователь отправил контакт через кнопку
    if message.contact:
        user_number = message.contact.phone_number
        my_bot.send_message(user_id, 'А теперь отправьте свою локацию!',
                            reply_markup=buttons.loc_button())
        # Перевести на этап получения локации
        my_bot.register_next_step_handler(message, get_location, user_name, user_number)
        # Если не через кнопку
    else:
        my_bot.send_message(user_id, 'Отправьте сообщение через кнопку!')
        my_bot.register_next_step_handler(message, get_number, user_name)


@my_bot.callback_query_handler(lambda call: call.data in ['increment', 'decrement', 'to_cart', 'back'])
def get_user_count(call):
    chat_id = call.message.chat.id

    if call.data == 'increment':
        actual_count = users[chat_id]['pr_count']

        users[chat_id]['pr_count'] += 1
        my_bot.edit_message_reply_markup(chat_id=chat_id,
                                         message_id=call.message.message_id,
                                         reply_markup=buttons.choose_product_count(actual_count, 'increment'))
    elif call.data == 'decrement':
        actual_count = users[chat_id]['pr_count']
        users[chat_id]['pr_count'] -= 1
        my_bot.edit_message_reply_markup(chat_id=chat_id,
                                         message_id=call.message.message_id,
                                         reply_markup=buttons.choose_product_count(actual_count, 'decrement'))
    elif call.data == 'back':
        products = db.get_pr_name_id()
        my_bot.edit_message_text('Выберите пуркт меню:',
                                 chat_id,
                                 call.message.message_id,
                                 reply_markup=buttons.main_menu_buttons(products))
    elif call.data == 'to_cart':
        products = db.get_pr_name_id()
        product_count = users[chat_id]['pr_count']

        user_product = users[chat_id]['pr_name']
        db.add_to_cart(chat_id, user_product, product_count)
        my_bot.edit_message_text('Продукт успешно добавлен! Хотите заказать что-нибудь еще?',
                                 chat_id,
                                 call.message.message_id,
                                 reply_markup=buttons.main_menu_buttons(products))

@my_bot.callback_query_handler(lambda call: call.data in ['cart', 'clear_cart', 'order', 'back'])
def cart_handle(call):
    user = call.message.chat.id
    message_id = call.message.message_id
    products = db.get_pr_name_id()

    if call.data == 'clear_cart':
        db.del_from_cart(user)
        my_bot.edit_message_text('Корзина очищена!',
                                 user,
                                 message_id,
                                 reply_markup=buttons.main_menu_buttons(products))
    elif call.data == 'order':
        db.del_from_cart(user)
        my_bot.send_message(870135238, 'Новый заказ!')
        my_bot.edit_message_text('Заказ оформлен! Желаете что-нибудь еще?',
                                 user,
                                 message_id,
                                 reply_markup=buttons.main_menu_buttons(products))
    elif call.data == 'back':
        products = db.get_pr_name_id()
        my_bot.edit_message_text('Выберите пункт меню:',
                                 user,
                                 call.message.message_id,
                                 reply_markup=buttons.main_menu_buttons(products))
    elif call.data == 'cart':
        my_bot.edit_message_text('Корзина',
                                 user,
                                 message_id,
                                 reply_markup=buttons.cart_buttons())


# Этап получения локации
def get_location(message, user_name, user_number):
    # Если пользаватель отправил локацию через кнопку
    if message.location:
        user_location = geolocator.reverse(f"{message.location.longitude},"
                                           f"{message.location.latitude}")
        # Регистрируем пользователя
        db.register(user_id, user_name, user_number, user_location)
        my_bot.send_message(user_id, 'Вы успешно зарегестрировались!',
                            reply_markup=buttons.remove())
        # Если не через кнопку
    else:
        my_bot.send_message(user_id, 'Отправьте сообщение через кнопку!')
        my_bot.register_next_step_handler(message, get_location, user_name, user_number)


# Функция выбора товара
@my_bot.callback_query_handler(lambda call: int(call.data) in db.get_pr_id())  # Прописывается для Inline кнопок
def get_user_product(call):
    chat_id = call.message.chat.id  # id чата с пользователем а не самого пользователя

    users[chat_id] = {'pr_name': call.data, 'pr_count': 1}

    message_id = call.message.message_id

    my_bot.edit_message_text('Выберите количество',
                             chat_id=chat_id, message_id=message_id,
                             reply_markup=buttons.choose_product_count())


# Запуск бота
my_bot.polling(non_stop=True)
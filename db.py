import sqlite3

#Подкдлючение к базе данных
connection = sqlite3.connect('tgbot_db.db', check_same_thread=False)
#Связь питона с базой данных
sql = connection.cursor()
#Создание таблицы пользователя
sql.execute('CREATE TABLE IF NOT EXISTS users '
            '(id INTEGER, '
            'name TEXT, '
            'number TEXT, '
            'location TEXT);')
#Создание таблицы продуктов
sql.execute('CREATE TABLE IF NOT EXISTS products '
            '(pr_id INTEGER PRIMARY KEY AUTOINCREMENT, '
            'pr_name TEXT, '
            'pr_amount INTEGER, '
            'pr_price REAL, '
            'pd_des TEXT,'
            'pr_photo TEXT);')
#Создание корзины пользавателей
sql.execute('CREATE TABLE IF NOT EXISTS user_cart '
            '(user_id INTEGER, '
            'user_product TEXT, '
            'product_quantity INTEGER, '
            'total REAL);')

##Методы для пользователя

#Регистрация
def register(id, name, number, location):
    sql.execute('INSERT INTO users VALUES (?, ?, ?, ?);',
                (id, name, number, location))
    #Фиксируем изменения
    connection.commit()

#Проверка на регистрацию
def checker(id):
    check = sql.execute('SELECT id FROM users WHERE id = ?;', (id, ))

    if check.fetchone():
        return True
    else:
        return False

#Методф для продуктов
#Вывод информации о конкретном продукте
def show_info(pr_name):
    sql.execute('SELECT pr_name, pr_des,'
                'pr_amount, pr_price,'
                'pr_photo, WHERE pr_name=?;', (pr_name, )).fetchone()

#Добавление товаров
def add_product(pr_name, pr_amount, pr_price, pr_des, pr_photo):
    sql.execute('INSERT INTO products (pr_name, '
                'pr_amount,'
                'pr_price,'
                'pr_des, '
                'pr_photo) VALUES (?, ?, ?, ?, ?);',
                (pr_name, pr_amount, pr_price, pr_des, pr_photo))
    #Фиксируем изменения
    connection.commit()
#Вывод всех продуктов из базы
def get_all_products():
    all_products = sql.execute('SELECT * FROM products;')

    return all_products.fetchall()

#Вывод id продуктов
def get_pr_name_id():
    products = sql.execute('SELECT pr_id, '
                           'pr_name, '
                           'pr_amount FROM products;').fetchall()
    return products

def get_pr_id():
    prods = sql.execute('SELECT pr_name, pr_id, pr_amount FROM products;').fetchall()
    sorted_prods = [i[1] for i in prods if i[2] > 0]
    return sorted_prods
#Меиоды корзины#
#Добавление в корзину
def add_to_cart(user_id, user_product, product_quantity, user_total=0):
    sql.execute('INSERT INTO user_cart VALUES (?, ?, ?, ?);',
                (user_id, user_product, product_quantity, user_total))
    #Фиксируем изменения
    connection.commit()

#Удаление из корзины
def del_from_cart(user_id):
    sql.execute('DELETE FROM user_cart WHERE user_id=?;', (user_id, ))
    #Фиксируем изменения
    connection.commit()

#Отображение корзины
def show_cart(user_id):
    cart = sql.execute('SELECT user_product,'
                'product_quantity,'
                'total FROM user_cart WHERE user_id=?;', (user_id, )).fetchone()
    return cart

#Получение корзины конкретного пользователя
#def get_exact_user_cart(user_id):
 #   user_cart = sql.execute('SELECT')
#def r():
   # sql.exexute('INSERT INTO product (pr_name, pr_amount, pr_price, pr_des, pr_photo)'
  #              'VALUES (?, ?, ?, ?, ?);')
 #   connection.commit()

#r()
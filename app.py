import hashlib
import os
import time
import requests
import random
import base64
from datetime import datetime
import json

from flask import Flask, render_template, request, redirect, url_for, jsonify, session, send_from_directory
from database import Database
from generate_model import GenerateAvarar
from fitting_online import fitting
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__, static_folder='static')
app.secret_key = 'a7ffa6121c67667045ccb87b57aac89f577d7235c1b8316bcc458decbef6ad5b'
db = Database()
AIML_API_KEY = "37d73fb346404448845afd8250938a47"
AIML_API_URL = "https://api.aimlapi.com/v1/images/generations"
IMGBB_API_KEY = "e7b6448153ab94ee3f4c67dcfd055e26"  # 🔑 ВСТАВЬ СЮДА СВОЙ КЛЮЧ

import requests


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import time

usd_cache = {"rate": 90, "timestamp": 0}

def get_usd_to_rub():
    global usd_cache
    now = time.time()
    if now - usd_cache['timestamp'] > 6 * 3600:
        try:
            res = requests.get('https://www.cbr-xml-daily.ru/daily_json.js')
            usd_cache['rate'] = res.json()['Valute']['USD']['Value']
            usd_cache['timestamp'] = now
        except:
            pass
    return usd_cache['rate']

import math

def beautify_price(price):
    return int(math.ceil(price / 100.0)) * 100

def hash_string(input_string):
    hash_object = hashlib.sha256()
    hash_object.update(input_string.encode('utf-8'))
    hash_hex = hash_object.hexdigest()

    return hash_hex

@app.route('/', methods=['GET', 'POST'])
def home():
    model_url = None
    error = None
    usdz_ready = False

    if request.method == 'POST':
        try:
            image = request.files['image']
            image_path = os.path.join('static', 'received.jpg')
            image.save(image_path)

            # Кодируем изображение в base64
            with open(image_path, "rb") as file:
                encoded_image = base64.b64encode(file.read()).decode("utf-8")

            # Загружаем на imgbb
            imgbb_url = "https://api.imgbb.com/1/upload"
            imgbb_payload = {
                "key": IMGBB_API_KEY,
                "image": encoded_image
            }

            imgbb_response = requests.post(imgbb_url, data=imgbb_payload)
            if imgbb_response.status_code != 200:
                error = "❌ Не удалось загрузить изображение на imgbb."
                return render_template("home.html", model_url=None, error=error)

            image_url = imgbb_response.json()["data"]["url"]

            # Отправляем image_url в AIML API
            headers = {
                "Authorization": f"Bearer {AIML_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "triposr",
                "image_url": image_url
            }

            response = requests.post(AIML_API_URL, headers=headers, json=payload, timeout=60)

            if response.status_code not in [200, 201]:
                error = f"⚠️ Ошибка API: {response.status_code}\n{response.text}"
                return render_template("home.html", model_url=None, error=error)

            data = response.json()
            model_url = data.get("model_mesh", {}).get("url")
            file_name = data.get("model_mesh", {}).get("file_name", "model.glb")

            if not model_url:
                error = "⚠️ Модель не сгенерирована. Нет ссылки."
                return render_template("home.html", model_url=None, error=error)

            # Скачиваем модель
            glb_path = os.path.join("static", file_name)
            glb_file = requests.get(model_url, stream=True)
            with open(glb_path, "wb") as f:
                for chunk in glb_file.iter_content(chunk_size=8192):
                    f.write(chunk)

            usdz_ready = True

        except Exception as e:
            error = f"❌ Ошибка: {str(e)}"

    try:
        # ✅ Фильтрация по ключевым словам
        include_keywords = ['shirt', 'tshirt', 'hoodie', 'dress', 'coat', 'jacket', 'clothing',
                            'shoes', 'sneakers', 'perfume', 'watch', 'bag', 'accessory',
                            'sunglasses', 'hat', 'sock']

        response = requests.get("https://dummyjson.com/products?limit=1000")
        all_products = response.json().get('products', [])

        visual_products = [
            p for p in all_products
            if any(word in p['title'].lower() or word in p['category'].lower() for word in include_keywords)
        ]

        # ✅ Перевод названий
        usd_to_rub = get_usd_to_rub()

        for p in visual_products:
            if 'price' in p:
                rub = p['price'] * usd_to_rub
                p['price'] = beautify_price(rub)
            p['translated_title'] = translate_text(p.get('title', 'Без названия'))
            p['translated_description'] = translate_description(p.get('description', ''), p['title'])


        random.shuffle(visual_products)
        carousel_products = visual_products[:18]

    except Exception as e:
        print("❌ Не удалось загрузить товары для карусели:", e)
        carousel_products = []

    return render_template("home.html",
                           model_url=model_url,
                           error=error,
                           usdz_ready=usdz_ready,
                           carousel_products=carousel_products)


@app.route('/studio', methods=['GET', 'POST'])
def studio():
    if request.method == 'POST':
        category = request.form.get('category')
        neck = request.form.get('neck')
        chest = request.form.get('chest')
        waist = request.form.get('waist')
        hips = request.form.get('hips')
        height = request.form.get('height')
        fabric = request.form.get('fabric')
        comment = request.form.get('comment')
        
        # Здесь можно добавить сохранение в БД или отправку на почту
        print("Новый заказ:", category, neck, chest, waist, hips, height, fabric, comment)

        return redirect(url_for('studio'))  # Перенаправление назад или на страницу с подтверждением

    return render_template('studio.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/reg', methods=['POST'])
def ref():
    data = request.json
    print(data)
    data = [el for el in data.values()]

    data[-1] = hash_string(data[-1])

    data.append('')

    response, message = db.insert_user(data)

    if response:
        session['logged_in'] = True
        session['user_data'] = {
            'name': data[0],
            'surname': data[1],
            'gender': data[3],
            'email': data[4],
            'phone': data[5],
            'role': data[6]
        }
        return jsonify({'success': True})
    
    return jsonify({'success': False})

@app.route('/login')
def login():
    return redirect(url_for('home', show_login='true'))

@app.route('/log', methods=['POST'])
def log():
    data = request.json
    data = [el for el in data.values()]
    data[-1] = hash_string(data[-1])

    ans, data = db.login_user(data)

    print(data)

    if ans:
        session['logged_in'] = True
        session['user_data'] = {
            'name': data[1],
            'surname': data[2],
            'gender': data[4],
            'email': data[5],
            'phone': data[6],
            'role': data[7]
        }
        return jsonify({"success": True})
    
    return jsonify({'success': False})

@app.route('/profile')
def profile():
    user_data = session.get('user_data', {})
    print(user_data)
    if 'logged_in' in session:
        return render_template(
            'info.html',
            user_type=user_data['role'],
            user_data=user_data,
            current_page='profile'  # 👈 добавляем это
        )
    else:
        return redirect(url_for('login'))



@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return jsonify({"success": True})

@app.route('/order_history')
def order_history():
    email = session.get('user_data', {}).get('email')
    if not email:
        return redirect('/login')

    # Получаем все товары
    try:
        products = requests.get("http://127.0.0.1:5000/api/products").json()
    except Exception as e:
        print("❌ Не удалось получить товары:", e)
        products = []

    orders = []
    for filename in os.listdir('orders'):
        if filename.endswith('.json'):
            filepath = os.path.join('orders', filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    order = json.load(f)
                    if order.get('email') == email:
                        # Подставляем подробности по каждому товару
                        for item in order['cart']:
                            product = next((p for p in products if str(p['id']) == str(item['id'])), None)
                            if product:
                                item['title'] = product.get('translated_title', product.get('title'))
                                item['thumbnail'] = product.get('thumbnail')
                                item['price'] = float(product.get('price', 0))
                                item['total'] = round(item['price'] * item['quantity'], 2)
                        order['total_sum'] = sum(i.get('total', 0) for i in order['cart'])
                        orders.append(order)
            except Exception as e:
                print("⚠️ Проблема с заказом:", e)
                continue

    orders.sort(key=lambda x: x.get('time', ''), reverse=True)

    return render_template('order_history.html',
                           orders=orders,
                           user_data=session['user_data'],
                           user_type=session['user_data']['role'])

@app.route('/check_session')
def check_session():
    return jsonify({"logged_in": 'logged_in' in session})


import logging

# Настраиваем логирование
logging.basicConfig(
    filename='email_debug.log',
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

def send_order_email(to_email, order_id, name, address, cart):
    from_email = "noreply@rafraf.bizml.ru"
    from_password = "8eWQkwCGxsxuipJqcJnS"
    subject = f"Ваш заказ #{order_id} подтверждён"

    logging.info(f"Начинаем подготовку письма заказчику {to_email} для заказа #{order_id}")

    # Загружаем все товары
    try:
        all_products = requests.get("http://127.0.0.1:5000/api/products").json()
        logging.info("Товары успешно загружены с API")
    except Exception as e:
        logging.error(f"Ошибка при загрузке товаров: {str(e)}")
        return

    # Формируем HTML
    items_html = ""
    for item in cart:
        product = next((p for p in all_products if str(p['id']) == str(item['id'])), None)
        if product:
            title = product.get('translated_title') or product.get('title', 'Без названия')
            size = item.get('size', '')
            items_html += f"<li>{item['quantity']} × {title} — {item['price']} ₽ {f'(размер: {size})' if size else ''}</li>"

    html_content = f"""
    <h2>Здравствуйте, {name}!</h2>
    <p>Ваш заказ <b>#{order_id}</b> успешно оформлен 🎉</p>
    <p><b>Адрес доставки:</b> {address}</p>
    <p><b>Состав заказа:</b></p>
    <ul>{items_html}</ul>
    <p>Спасибо, что выбираете LookBook ♥</p>
    """

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(html_content, 'html'))

    try:
        logging.info("Устанавливаем соединение с SMTP-сервером Mail.ru")
        with smtplib.SMTP_SSL('smtp.mail.ru', 465) as server:
            logging.info("Подключение установлено, выполняем login...")
            server.login(from_email, from_password)
            logging.info("Аутентификация прошла успешно")
            server.sendmail(from_email, to_email, msg.as_string())
            logging.info(f"Письмо отправлено на {to_email}")
    except smtplib.SMTPAuthenticationError as auth_err:
        logging.error(f"Ошибка аутентификации: {auth_err}")
    except Exception as e:
        logging.error(f"Ошибка при отправке письма: {str(e)}")

@app.route('/send_order', methods=['POST'])
def send_order():
    data = request.get_json()

    name = data.get('name')
    address = data.get('address')
    cart = data.get('cart')
    email = data.get('email')  # ⚠️ раньше бралось из session — теперь из тела запроса!

    if not all([name, address, email, cart]):
        return jsonify({'success': False, 'error': 'Missing fields'}), 400

    os.makedirs('orders', exist_ok=True)
    order_id = int(time.time())

    with open(f'orders/order_{order_id}.json', 'w', encoding='utf-8') as f:
        json.dump({
            'id': order_id,
            'name': name,
            'address': address,
            'email': email,
            'cart': cart,
            'time': datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)

    # Письмо — опционально
    try:
        send_order_email(email, order_id, name, address, cart)
    except Exception as e:
        print("Ошибка отправки письма:", e)

    return jsonify({'success': True, 'order_id': order_id})

@app.route('/cart')
def cart():
    return render_template('cart.html')
    
@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

@app.route('/api/products')
def api_products():
    # Получаем курс $ → ₽
    usd_to_rub = get_usd_to_rub()

    # Внешние товары — переводим в рубли
    response = requests.get("https://dummyjson.com/products?limit=1000")
    api_products = response.json().get('products', [])

    for p in api_products:
        if 'price' in p:
            rub = p['price'] * usd_to_rub
            p['price'] = beautify_price(rub)

    # Локальные товары — уже в рублях
    db_products_raw = db.get_all_items()
    db_products = [{
        'id': f'local_{item[0]}',
        'title': item[1],
        'description': item[4],
        'price': float(item[5]),
        'thumbnail': url_for('static', filename=item[3].split(';')[0].lstrip('/'))
    } for item in db_products_raw]

    # Объединяем и переводим названия/описания
    all_products = api_products + db_products
    for p in all_products:
        p['translated_title'] = translate_text(p['title'])
        p['translated_description'] = translate_description(p.get('description', ''), p['title'])

    return jsonify(all_products)

@app.route('/avatar')
def avatar():
    user_data = session.get('user_data', {})
    model = db.get_user(user_data['email'])[-1]
    is_model = False

    print(model)

    if model != '':
        is_model = True

    # print(is_model)

    return render_template(
            'avatar.html',
            model=is_model,
            user_type=user_data['role'],
            user_data=user_data)

@app.route('/generate_avatar')
def generate_avatar():
    user_data = session.get('user_data', {})
    model = db.get_user(user_data['email'])[-1]
    is_model = False

    if model is not None:
        is_model = True

    return render_template(
            'generate_avatar.html',
            model=is_model,
            user_type=user_data['role'],
            user_data=user_data)

@app.route('/generate_model', methods=['POST'])
def generate_model():
    data = request.json
    print(data)
    height = data['height'] / 100
    weight = data['weight']
    arm_span = data['arm_span'] / 100
    leg_length = data['leg_length'] / 100

    user_data = session.get('user_data', {})
    gender = user_data['gender']
    filename = hash_string(''.join([str(x) for x in user_data.values()]))

    model_path = GenerateAvarar(height, weight, arm_span, leg_length, gender).generate_avatar(filename)

    model_path = url_for('serve_model', filename=f'{filename}.obj')
    return jsonify({'model_path': model_path})

@app.route('/save_model')
def save_model():
    user_data = session.get('user_data', {})
    filename = hash_string(''.join([str(x) for x in user_data.values()]))
    email = user_data['email']

    ans = db.setup_model(email, filename)
    if ans:
        return jsonify({"success": True})
    
    return jsonify({"success": False})

@app.route('/get_model_name', methods=['GET'])
def get_model_name():
    user_data = session.get('user_data', {})
    filename = db.get_user(user_data['email'])[-1]
    model_path = url_for('serve_model', filename=f'{filename}.obj')
    return jsonify({'model_path': model_path})

@app.route('/styles/models/<path:filename>')
def serve_model(filename):
    return send_from_directory('styles/models', filename)

@app.route('/del_avatar')
def del_avatar():
    user_data = session.get('user_data', {})

    if db.del_model(user_data['email']):
        return jsonify({'success': True})
    
    return jsonify({'success': False})

@app.route('/items')
def items():
    user_data = session.get('user_data', {})
    id_ = db.get_user(user_data['email'])[0]
    items = db.get_items(id_)

    items_data = []
    
    for elem in items:
        item = {
            'name': elem[1],
            'price': elem[5],
            'image': elem[3].split(';')[0],
            'id': elem[0]
        }

        items_data.append(item)

    return render_template(
            'items.html',
            items=items_data,
            user_type=user_data['role'],
            user_data=user_data)

@app.route('/create_item')
def create_item():
    user_data = session.get('user_data', {})
    return render_template('create_item.html',
            user_type=user_data['role'],
            user_data=user_data)

@app.route('/edit_item')
def edit_item():
    user_data = session.get('user_data', {})
    dv = {}

    item_id = request.args.get('item_id')
    if item_id:
        item = db.get_item_by_id(item_id)

        dv = {
            'id': item[0],
            'product_name': item[1],
            'category': item[6],
            'product_description': item[4],
            'product_price': item[5],
            'product_quantity': item[7],
            'product_images': item[3].split(';'),
        }

        print(dv['product_images'])


    return render_template('edit_item.html',
            default_values=dv,
            user_type=user_data['role'],
            user_data=user_data)

@app.route('/add_item', methods=['POST']) 
def add_item():
    email = session.get('user_data', {})['email']
    id_ = db.get_user(email)[0]

    category = request.form['category']
    product_name = request.form['product_name']
    product_description = request.form['product_description']
    product_price = request.form['product_price']
    product_quantity = request.form['product_quantity']
    product_images = request.files.getlist('product_images')
    
    filename = hash_string(''.join([email, product_name, category]))
    
    if not os.path.exists('styles/items_images'):
        os.makedirs('styles/items_images')

    # Сохранение изображений
    image_paths = []
    for image in product_images:
        image_folder = os.path.join('static', 'items_images')
        if not os.path.exists(image_folder):
            os.makedirs(image_folder)

        image_paths = []
        for image in product_images:
            ext = image.filename.split('.')[-1]
            image_filename = f"{filename}_{random.randint(1000, 9999)}.{ext}"
            image_path = os.path.join(image_folder, image_filename)
            image.save(image_path)
            image_paths.append(f"items_images/{image_filename}")  # <— БЕЗ начального /

    item_params = [
        product_name, 
        id_, 
        ';'.join(image_paths),
        product_description, 
        product_price, 
        category, 
        product_quantity
    ]

    res = db.set_items(item_params)

    if res:
        return jsonify({'success': True, 'message': 'Товар успешно добавлен!', 'image_paths': image_paths})

    return jsonify({'success': False, 'message': 'some_problems'})

@app.route('/change_item', methods=['POST']) 
def change_item():
    print(request.form)
    category = request.form['category']
    product_name = request.form['product-name']
    product_description = request.form['product-description']
    product_price = request.form['product-price']
    product_quantity = request.form['product-quantity']
    id = request.form['item_id']
    images = request.files.getlist('images')

    res = db.del_item(id)

    print(res)

    email = session.get('user_data', {})['email']
    id_ = db.get_user(email)[0]

    filename = hash_string(''.join([email, product_name, category]))
    
    if not os.path.exists('styles/items_images'):
        os.makedirs('styles/items_images')

    # Сохранение изображений
    image_paths = []
    for image in images:
        image_path = os.path.join('styles/items_images', f"{filename}.{image.filename.split('.')[1]}")
        image.save(image_path)
        image_paths.append(f"/items_images/{filename}.{image.filename.split('.')[1]}")

    item_params = [
        product_name, 
        id_, 
        ';'.join(image_paths),
        product_description, 
        product_price, 
        category, 
        product_quantity
    ]

    res = db.set_items(item_params)

    if res:
        return jsonify({'success': True, 'message': 'Товар успешно добавлен!', 'image_paths': image_paths})

    return jsonify({'success': False, 'message': 'some_problems'})

@app.route('/item_page/<item_id>')
def item_page(item_id):
    print(f"👉 Перешли на товар: {item_id}")
    usd_to_rub = get_usd_to_rub()
    rub = product.get('price', 0) * usd_to_rub
    price_rub = beautify_price(rub)
    if str(item_id).startswith("local_"):
        item_id_clean = item_id.replace("local_", "")
        db_item = db.get_item_by_id(item_id_clean)
        if not db_item:
            return "Товар не найден", 404

        item = {
            'name': db_item[1],
            'description': db_item[4],
            'price': db_item[5],
            'image': db_item[3].split(';')[0],
            'id': db_item[0]
        }
    else:
        try:
            product = requests.get(f"https://dummyjson.com/products/{item_id}").json()
            if 'id' not in product:
                return "Товар не найден", 404

            item = {
                'name': product.get('title'),
                'description': product.get('description'),
                'price': price_rub,
                'image': product.get('thumbnail'),
                'id': product.get('id')
            }
        except Exception as e:
            return f"Ошибка: {e}", 500

    return render_template('item_page.html', product=item)

@app.route('/check_model',  methods=['POST'])
def check_model():
    data = request.json['id']
    model = db.check_item_model(data)[-1]

    return jsonify({'model': model})

@app.route('/create_model', methods=['POST'])
def create_model():
    item_id = request.form.get('item_id')
    print(item_id)

    if 'image' not in request.files:
        return jsonify({'error': 'No image part'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = os.path.join('styles/items2generate', file.filename)
        file.save(filename)

        url = 'http://localhost:8000/item_generate'
        files = {'image': open('styles/items2generate/selected_image.jpg', 'rb')}

        resp = requests.post(url, files=files)

        strr = 'qwertyuiopasdfghjklzxcvbnm1234567890'
        # filename = [strr[random.]]

        if resp.status_code == 200:
            with open('/home/main/Documents/order_08-10/site/styles/items2generate/', 'wb') as f:
                f.write(resp.content)

            return jsonify({'message': 'Model creation initiated', 'filename': filename})

        # Здесь можно добавить логику для создания модели на основе изображения
        return jsonify({'message': 'Error', 'filename': ''})

def gt_it(cats):
    items = db.get_items_cat(cats)

    items_data = [] 

    for elem in items:
        item = {
            'name': elem[1],
            'description': elem[4],
            'price': elem[5],
            'image': elem[3].split(';')[0],
            'id': elem[0]
        }

        items_data.append(item)

    return items_data

translations_cache_desc = {
    "Blue & Black Check Shirt": "Синяя и чёрная рубашка в клетку — Стильная и удобная рубашка с классическим узором. Подходит как для повседневной носки, так и для полуформальных мероприятий.",
    "Gigabyte Aorus Men Tshirt": "Мужская футболка Gigabyte Aorus — Футболка с логотипом Aorus и стильным дизайном для геймеров.",
    "Man Plaid Shirt": "Мужская рубашка в клетку — Универсальная рубашка с классическим клетчатым узором, идеальна для повседневной носки.",
    "Man Short Sleeve Shirt": "Мужская рубашка с коротким рукавом — Лёгкая и стильная рубашка на тёплую погоду с комфортной посадкой.",
    "Men Check Shirt": "Мужская клетчатая рубашка — Классическая рубашка с клетчатым узором для разных случаев.",
    "Nike Air Jordan 1 Red and Black": "Nike Air Jordan 1 красные и чёрные — Легендарные баскетбольные кроссовки с высоким качеством и стильным дизайном.",
    "Nike Baseball Cleats": "Бейсбольные бутсы Nike — Обувь с отличным сцеплением и поддержкой для игры в бейсбол.",
    "Puma Future Rider Trainers": "Кроссовки Puma Future Rider — Ретро-дизайн с комфортом на каждый день.",
    "Sports Sneakers Off White Red": "Спортивные кроссовки бело-красные — Удобные и стильные кроссовки для спорта и повседневной носки.",
    "Brown Leather Belt Watch": "Часы с коричневым кожаным ремешком — Стильные часы с кожаным ремешком и классическим дизайном.",
    "Apple Watch Series 4 Gold": "Apple Watch Series 4 золотые — Умные часы с мониторингом здоровья, фитнес-трекингом и Retina-дисплеем.",
    "Black Sun Glasses": "Чёрные солнцезащитные очки — Классические чёрные очки с УФ-защитой.",
    "Classic Sun Glasses": "Классические солнцезащитные очки — Универсальные очки с нейтральным дизайном.",
    "Green and Black Glasses": "Зелёные и чёрные очки — Очки с ярким сочетанием зелёного и чёрного.",
    "Party Glasses": "Очки для вечеринок — Яркие и необычные очки для праздничного образа.",
    "Sunglasses": "Солнцезащитные очки — Простые и функциональные очки с УФ-защитой.",
    "Girl Summer Dress": "Летнее платье для девочки — Лёгкое платье с яркими узорами для лета.",
    "Gray Dress": "Серое платье — Универсальное платье в нейтральном цвете для разных поводов.",
    "Tartan Dress": "Платье в клетку — Платье с классическим тартановым узором для осени и зимы.",
    "Blue Women's Handbag": "Синяя женская сумка — Просторная и яркая сумка на каждый день.",
    "Heshe Women's Leather Bag": "Женская кожаная сумка Heshe — Элегантная и долговечная кожаная сумка.",
    "Prada Women Bag": "Женская сумка Prada — Иконическая дизайнерская сумка для любительниц моды.",
    "White Faux Leather Backpack": "Белый рюкзак из искусственной кожи — Трендовый рюкзак с достаточным объёмом.",
    "Women Handbag in Black": "Женская чёрная сумка — Классическая чёрная сумка, подходящая к любому образу.",
    "Black Women's Gown": "Чёрное женское платье — Элегантное платье для вечерних мероприятий.",
    "Corset Leather With Skirt": "Кожаный корсет с юбкой — Эффектный и смелый образ для особого случая.",
    "Corset With Black Skirt": "Корсет с чёрной юбкой — Модный комплект с чёрной юбкой и корсетом.",
    "Dress Pea": "Платье в горошек — Игривое и удобное платье с узором в горох.",
    "Marni Red & Black Suit": "Костюм Marni красно-чёрный — Современный костюм с выразительной цветовой гаммой.",
    "Black & Brown Slipper": "Тапочки чёрно-коричневые — Удобные и стильные тапочки для дома.",
    "Calvin Klein Heel Shoes": "Туфли на каблуке Calvin Klein — Классические туфли для формальных мероприятий.",
    "Golden Shoes for Women": "Золотые женские туфли — Роскошные туфли с золотым блеском.",
    "Pampi Shoes": "Обувь Pampi — Удобная обувь с повседневным дизайном.",
    "Red Shoes": "Красные туфли — Яркие и стильные туфли для образа с акцентом.",
    "Gold Women's Watch": "Женские золотые часы — Роскошные женские часы с золотым покрытием.",
}

translations_cache = {
    "Blue & Black Check Shirt": "Синяя и чёрная рубашка в клетку",
    "Gigabyte Aorus Men Tshirt": "Мужская футболка Gigabyte Aorus",
    "Man Plaid Shirt": "Мужская рубашка в клетку",
    "Man Short Sleeve Shirt": "Мужская рубашка с коротким рукавом",
    "Men Check Shirt": "Мужская клетчатая рубашка",
    "Nike Air Jordan 1 Red And Black": "Nike Air Jordan 1 красные и чёрные",
    "Nike Baseball Cleats": "Бейсбольные бутсы Nike",
    "Puma Future Rider Trainers": "Кроссовки Puma Future Rider",
    "Sports Sneakers Off White & Red": "Спортивные кроссовки бело-красные",
    "Sports Sneakers Off White Red": "Спортивные кроссовки бело-красные",
    "Brown Leather Belt Watch": "Часы с коричневым кожаным ремешком",
    "Apple Watch Series 4 Gold": "Apple Watch Series 4 золотые",
    "Black Sun Glasses": "Чёрные солнцезащитные очки",
    "Classic Sun Glasses": "Классические солнцезащитные очки",
    "Green and Black Glasses": "Зелёные и чёрные очки",
    "Party Glasses": "Очки для вечеринок",
    "Sunglasses": "Солнцезащитные очки",
    "Girl Summer Dress": "Летнее платье для девочки",
    "Gray Dress": "Серое платье",
    "Tartan Dress": "Платье в клетку",
    "Blue Women's Handbag": "Синяя женская сумка",
    "Heshe Women's Leather Bag": "Женская кожаная сумка Heshe",
    "Prada Women Bag": "Женская сумка Prada",
    "White Faux Leather Backpack": "Белый рюкзак из искусственной кожи",
    "Women Handbag Black": "Женская чёрная сумка",
    "Black Women's Gown": "Чёрное женское платье",
    "Corset Leather With Skirt": "Кожаный корсет с юбкой",
    "Corset With Black Skirt": "Корсет с чёрной юбкой",
    "Dress Pea": "Платье в горошек",
    "Marni Red & Black Suit": "Костюм Marni красно-чёрный",
    "Black & Brown Slipper": "Тапочки чёрно-коричневые",
    "Calvin Klein Heel Shoes": "Туфли на каблуке Calvin Klein",
    "Golden Shoes Woman": "Золотые женские туфли",
    "Pampi Shoes": "Обувь Pampi",
    "Red Shoes": "Красные туфли",
    "Watch Gold for Women": "Женские золотые часы",
    "Women's Wrist Watch": "Женские наручные часы"
}


# В твоем app.py (или в нужной функции маршрута /clothes)
import requests

def translate_text(text):
    return translations_cache.get(text, text)

def translate_description(desc, title):
    return translations_cache_desc.get(title, desc)

@app.route('/clothes')
def clothes():
    category = request.args.get('category', 'all')
    max_price = float(request.args.get('max_price', 100_000))
    sort = request.args.get('sort', 'default')
    page = request.args.get('page', 1, type=int)

    # Получаем товары из внешнего API
    response = requests.get("https://dummyjson.com/products?limit=1000")
    all_products = response.json().get('products', [])

    # Фильтрация по ключевым словам
    include_keywords = ['shirt', 'tshirt', 'hoodie', 'dress', 'coat', 'jacket', 'clothing',
                        'shoes', 'sneakers', 'perfume', 'watch', 'bag', 'accessory',
                        'sunglasses', 'hat', 'sock']

    visual_products = [
        p for p in all_products
        if any(word in p['title'].lower() or word in p['category'].lower() for word in include_keywords)
    ]

    # ✅ Добавляем свои товары
    my_products_raw = db.get_all_items()
    for prod in my_products_raw:
        item = {
            'id': f'local_{prod[0]}',  # <-- совпадает с /api/products
            'title': prod[1],
            'price': float(prod[5]),
            'thumbnail': url_for('static', filename=prod[3].split(';')[0].lstrip('/')),
            'category': prod[6].lower()
        }
        visual_products.append(item)

    # Категори фильтр
    category_keywords = {
        'mens': ['men'],
        'womens': ['women'],
        'shoes': ['shoe'],
        'glasses': ['glasses', 'sunglass', 'eyewear'],
        'watches': ['watch'],
        'bags': ['bag', 'backpack', 'handbag']
    }
    usd_to_rub = get_usd_to_rub()
    # Конвертируем и округляем рубли
    for p in visual_products:
        if 'price' in p:
            rub = p['price'] * usd_to_rub
            p['price'] = beautify_price(rub)

    # Применяем категорийный фильтр
    if category != 'all' and category in category_keywords:
        keywords = category_keywords[category]
        filtered_products = [
            p for p in visual_products
            if any(word in p['title'].lower() or word in p['category'].lower() for word in keywords)
        ]
    else:
        filtered_products = visual_products

    # Фильтрация по цене
    filtered_products = [p for p in filtered_products if p['price'] <= max_price]

    # Сортировка
    if sort == 'price_asc':
        filtered_products.sort(key=lambda x: x['price'])
    elif sort == 'price_desc':
        filtered_products.sort(key=lambda x: x['price'], reverse=True)

    # Пагинация
    per_page = 12
    total_pages = (len(filtered_products) + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    page_products = filtered_products[start:end]

    for p in page_products:
        p['translated_title'] = translate_text(p['title'])
        desc = p.get('description', '')
        p['translated_description'] = translate_description(desc, p['title'])

    

    return render_template('clothes.html',
                           products=page_products,
                           total_pages=total_pages,
                           page=page,
                           category=category,
                           max_price=max_price,
                           sort=sort)
                           
                           
@app.route('/fit', methods=['POST'])
def fit():
    uploaded_image = request.files.get('uploadedImage')
    product_image_src = request.form.get('productImage')
    print(product_image_src)
    uploaded_image.save('styles/online_fitting/' + uploaded_image.filename)
    
    filename = fitting('styles/online_fitting/' + uploaded_image.filename, product_image_src)
    print(filename)

    return jsonify({'imageUrl': f'{filename}'})

# @app.route('/styles/online_fitting/<filename>')
# def uploaded_file(filename):
#     return send_from_directory("/styles/online_fitting", filename)

@app.route('/delete_item', methods=['POST'])
def delete_item():
    data = request.get_json()
    item_id = data.get('item_id')

    db.del_item(item_id)

    return jsonify({'success': True})

@app.route('/search_site')
def search_site():
    query = request.args.get('q', '').lower()
    results = []

    for filename in os.listdir('templates'):
        if filename.endswith('.html'):
            filepath = os.path.join('templates', filename)
            with open(filepath, encoding='utf-8') as f:
                content = f.read().lower()
                lines = content.splitlines()
                for line in lines:
                    if query in line:
                        clean_text = line.strip()
                        if clean_text:
                            results.append({
                                'text': clean_text[:150],  # обрезаем длинные строки
                                'source': filename.replace('.html', '')
                            })

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)

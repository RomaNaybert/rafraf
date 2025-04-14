import hashlib
import os

from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from database import Database
from generate_model import GenerateAvarar

app = Flask(__name__, static_folder='styles')
app.secret_key = 'a7ffa6121c67667045ccb87b57aac89f577d7235c1b8316bcc458decbef6ad5b'
db = Database()

def hash_string(input_string):
    hash_object = hashlib.sha256()
    hash_object.update(input_string.encode('utf-8'))
    hash_hex = hash_object.hexdigest()

    return hash_hex

@app.route('/')
def home():
    return render_template('home.html')
    
@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/reg', methods=['POST'])
def ref():
    data = request.json
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
    return render_template('login.html')

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
    profiles = {
        'buyer': 'buyer_account.html',
        'seller': 'seller_account.html'
    }

    user_data = session.get('user_data', {})
    print(user_data)
    if 'logged_in' in session:
        return render_template(
            profiles[user_data['role']], 
            user_data=user_data)
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return jsonify({"success": True})

@app.route('/check_session')
def check_session():
    return jsonify({"logged_in": 'logged_in' in session})

@app.route('/avatar')
def avatar():
    user_data = session.get('user_data', {})
    model = db.get_user(user_data['email'])[-1]
    
    print(model, 'gg')

    if model == '':
        return render_template('avatar_1.html')
    else:
        return render_template('avatar_2.html')

@app.route('/generate_avatar')
def generate_avatar():
    return render_template('generate_avatar.html')

@app.route('/generate_model', methods=['POST'])
def generate_model():
    data = request.json
    height = data['height'] / 100
    weight = data['weight']
    arm_span = data['arm_span'] / 100
    leg_length = data['leg_length'] / 100

    user_data = session.get('user_data', {})
    gender = user_data['gender']
    filename = hash_string(''.join([str(x) for x in user_data.values()]))

    model_path = GenerateAvarar(height, weight, arm_span, leg_length, gender).generate_avatar(filename)

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

@app.route('/get_model_name')
def get_model_name():
    user_data = session.get('user_data', {})
    
    filename = db.get_user(user_data['email'])[-1]

    path = f'static/models/{filename}.obj'

    return jsonify({'model_path': path})

@app.route('/del_avatar')
def del_avatar():
    user_data = session.get('user_data', {})

    if db.del_model(user_data['email']):
        return jsonify({'success': True})
    
    return jsonify({'success': False})

@app.route('/items')
def items():
    email = session.get('user_data', {})['email']
    items = db.get_items(email)

    items_data = []

    for elem in items:
        item = {
            'name': elem[1],
            'description': elem[4],
            'price': elem[5],
            'image': elem[3].split(';')[0],
        }

        items_data.append(item)

    if items:
        return render_template('items_2.html', items=items_data)
    
    return render_template('items.html')

@app.route('/get_half_items', methods=['GET'])
def get_half_items():
    email = session.get('user_data', {})['email']
    items = db.get_items(email)
    items_data = []

    for elem in items:
        item = {
            'name': elem[1],
            'description': elem[4],
            'price': elem[5],
            'image': elem[3].split(';')[0]
        }


        items_data.append(item)

    return jsonify({'products': items_data})

@app.route('/create_item')
def create_item():
    return render_template('create_item.html')

@app.route('/add_item', methods=['POST'])
def add_item():
    email = session.get('user_data', {})['email']

    category = request.form['category']
    product_name = request.form['product_name']
    product_description = request.form['product_description']
    product_price = request.form['product_price']
    product_quantity = request.form['product_quantity']
    product_images = request.files.getlist('product_images')
    
    filename = hash_string(''.join([email, product_name, category]))
    
    if not os.path.exists('static/items_images'):
        os.makedirs('static/items_images')

    # Сохранение изображений
    image_paths = []
    for image in product_images:
        image_path = os.path.join('static/items_images', f"{filename}.{image.filename.split('.')[1]}")
        image.save(image_path)
        image_paths.append(f"/items_images/{filename}.{image.filename.split('.')[1]}")

    item_params = [
        product_name, 
        email, 
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

def gt_it(cats):
    items = db.get_items_('top')

    items_data = []

    for elem in items:
        item = {
            'name': elem[1],
            'description': elem[4],
            'price': elem[5],
            'image': elem[3].split(';')[0]
        }

        items_data.append(item)

    return items_data

@app.route('/top')
def top():
    items = gt_it('top')
    if items:
        return render_template('category.html', products=items)
    
@app.route('/bottom')
def bottom():
    items = gt_it('bottom')
    if items:
        return render_template('category.html', products=items)
    
@app.route('/shoes')
def shoes():
    items = gt_it('shoes')
    if items:
        return render_template('category.html', products=items)
    
@app.route('/accessories')
def accessories():
    items = gt_it('accessories')
    if items:
        return render_template('category.html', products=items)

if __name__ == '__main__':
    app.run(debug=True)
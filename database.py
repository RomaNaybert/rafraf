import sqlite3


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('data.db', check_same_thread=False)
        self.cur = self.conn.cursor()

        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                surname TEXT,
                birth DATETIME,
                gender TEXT,
                email TEXT,
                phone TEXT,
                role TEXT,
                password TEXT,
                model TEXT
            )
        ''')
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                seller_id TEXT NOT NULL,
                photos TEXT,
                description TEXT,
                price FLOAT,
                category TEXT,
                count INTEGER,
                model TEXT
            )
        ''')

        # Создание таблицы orders
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                product_id INTEGER,
                quantity INTEGER,
                order_date DATETIME,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')

        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                reviewer_id INTEGER,
                product_id INTEGER,
                order_date DATETIME
            )
        ''')
        self.conn.commit()

    def insert_user(self, user_data):
        try:
            self.cur.execute('''
                SELECT * FROM users WHERE email = ?
            ''', (user_data[0],))
            user = self.cur.fetchone()

            
            if user is None:
                self.cur.execute('''
                    INSERT INTO users (name, surname, birth, gender, email, phone, role, password, model)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_data))
                self.conn.commit()

                return True, 'OK'
            else:
                return False, 'User exist'
        except:
            return False, 'Server error'


    def get_all_items(self):
        try:
            self.cur.execute("SELECT * FROM products")
            return self.cur.fetchall()
        except Exception as e:
            print(f"[get_all_items ERROR] {e}")
            return []

    def login_user(self, user_data):
        print(user_data)
        try:
            self.cur.execute('''
                SELECT * FROM users WHERE email = ?
            ''', (user_data[0],))
            user = self.cur.fetchone()
            print(user)
            if user[-2] == user_data[1]:
                return True, user
            
            return False, None
        except:
            return False, None
        
    def get_user(self, email):
        try:
            self.cur.execute('''
                SELECT * FROM users WHERE email = ?
            ''', (email,))
            user = self.cur.fetchone()

            return user
        except:
            return None
        
    def setup_model(self, email, model_value):
        try:
            self.cur.execute('''
                UPDATE users
                SET model = ?
                WHERE email = ?
            ''', (model_value, email))
            self.conn.commit()
        
            return True
        except:
            return False
        
    def del_model(self, email):
        try:
            self.cur.execute('''
                UPDATE users
                SET model = ?
                WHERE email = ?
            ''', ('', email))
            self.conn.commit()
        
            return True
        except:
            return False
        
    def get_items(self, id_):
        try:
            self.cur.execute('''
            SELECT * FROM products WHERE seller_id = ?
        ''', (id_,))
            
            items = self.cur.fetchall()

            return items
        except:
            return []
        
    def del_item(self, item_id):
        try:
            self.cur.execute("DELETE FROM products WHERE id = ?", (item_id,))
            return True
        except:
            return False
        
    def set_items(self, item_data):
        try:
            self.cur.execute('''
                    INSERT INTO products (name, seller_id, photos, description, price, category, count)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (item_data))
            self.conn.commit()

            return True
        except Exception as ex:
            # print(ex)
            return False
        
    def get_items_cat(self, category):
        try:
            self.cur.execute('''
            SELECT * FROM products WHERE category = ?
        ''', (category,))
            
            items = self.cur.fetchall()

            return items
        except:
            return []
        
    def get_item_by_id(self, id):
        try:
            self.cur.execute('''
            SELECT * FROM products WHERE id = ?
        ''', (id,))
            
            items = self.cur.fetchall()

            return items[0]
        except:
            return []
        
    def check_item_model(self, id):
        try:
            self.cur.execute('''
            SELECT * FROM products WHERE id = ?
        ''', (id,))
            
            items = self.cur.fetchone()

            return items
        except:
            return []
        

    def close(self):
        self.conn.close()
import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'change-this-secret-key'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'flowers_store.db')


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Flowers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            description TEXT,
            FOREIGN KEY (category_id) REFERENCES Categories(id)
        )
    ''')

    conn.commit()
    conn.close()


@app.route('/')
def home():
    conn = get_db_connection()
    flowers = conn.execute(
        '''
        SELECT f.id, f.name, f.price, f.stock, f.description,
               c.id AS category_id, c.name AS category_name
        FROM Flowers f
        LEFT JOIN Categories c ON f.category_id = c.id
        ORDER BY f.id DESC
        '''
    ).fetchall()
    categories = conn.execute('SELECT * FROM Categories ORDER BY name').fetchall()
    conn.close()
    return render_template('index.html', section='home', flowers=flowers, categories=categories)


@app.route('/flowers/new', methods=['GET', 'POST'])
def new_flower():
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM Categories ORDER BY name').fetchall()
    conn.close()

    if request.method == 'POST':
        name = request.form['name'].strip()
        category_id = request.form.get('category_id') or None
        price = request.form['price']
        stock = request.form['stock']
        description = request.form['description'].strip()

        if not name or not price or not stock:
            flash('กรุณากรอกชื่อสินค้า ราคา และจำนวนคงเหลือให้ครบถ้วน', 'warning')
            return render_template('index.html', section='flower_form', form_action=url_for('new_flower'), categories=categories, flower=request.form)

        try:
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO Flowers (name, category_id, price, stock, description) VALUES (?, ?, ?, ?, ?)',
                (name, category_id, float(price), int(stock), description)
            )
            conn.commit()
            conn.close()
            flash('เพิ่มสินค้าสำเร็จ', 'success')
            return redirect(url_for('home'))
        except Exception as exc:
            flash(f'เกิดข้อผิดพลาด: {exc}', 'danger')
            return render_template('index.html', section='flower_form', form_action=url_for('new_flower'), categories=categories, flower=request.form)

    return render_template('index.html', section='flower_form', form_action=url_for('new_flower'), categories=categories, flower={})


@app.route('/flowers/edit/<int:flower_id>', methods=['GET', 'POST'])
def edit_flower(flower_id):
    conn = get_db_connection()
    flower = conn.execute('SELECT * FROM Flowers WHERE id = ?', (flower_id,)).fetchone()
    categories = conn.execute('SELECT * FROM Categories ORDER BY name').fetchall()
    conn.close()

    if flower is None:
        flash('ไม่พบสินค้านี้', 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        name = request.form['name'].strip()
        category_id = request.form.get('category_id') or None
        price = request.form['price']
        stock = request.form['stock']
        description = request.form['description'].strip()

        if not name or not price or not stock:
            flash('กรุณากรอกชื่อสินค้า ราคา และจำนวนคงเหลือให้ครบถ้วน', 'warning')
            return render_template('index.html', section='flower_form', form_action=url_for('edit_flower', flower_id=flower_id), categories=categories, flower=request.form, is_edit=True)

        try:
            conn = get_db_connection()
            conn.execute(
                'UPDATE Flowers SET name = ?, category_id = ?, price = ?, stock = ?, description = ? WHERE id = ?',
                (name, category_id, float(price), int(stock), description, flower_id)
            )
            conn.commit()
            conn.close()
            flash('แก้ไขสินค้าสำเร็จ', 'success')
            return redirect(url_for('home'))
        except Exception as exc:
            flash(f'เกิดข้อผิดพลาด: {exc}', 'danger')
            return render_template('index.html', section='flower_form', form_action=url_for('edit_flower', flower_id=flower_id), categories=categories, flower=request.form, is_edit=True)

    return render_template('index.html', section='flower_form', form_action=url_for('edit_flower', flower_id=flower_id), categories=categories, flower=flower, is_edit=True)


@app.route('/flowers/delete/<int:flower_id>', methods=['POST'])
def delete_flower(flower_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Flowers WHERE id = ?', (flower_id,))
    conn.commit()
    conn.close()
    flash('ลบสินค้าสำเร็จ', 'success')
    return redirect(url_for('home'))


@app.route('/categories')
def manage_categories():
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM Categories ORDER BY name').fetchall()
    conn.close()
    return render_template('index.html', section='categories', categories=categories)


@app.route('/categories/new', methods=['GET', 'POST'])
def new_category():
    if request.method == 'POST':
        name = request.form['name'].strip()
        if not name:
            flash('กรุณากรอกชื่อหมวดหมู่', 'warning')
            return render_template('index.html', section='category_form', form_action=url_for('new_category'), category=request.form)

        try:
            conn = get_db_connection()
            conn.execute('INSERT INTO Categories (name) VALUES (?)', (name,))
            conn.commit()
            conn.close()
            flash('เพิ่มหมวดหมู่สำเร็จ', 'success')
            return redirect(url_for('manage_categories'))
        except sqlite3.IntegrityError:
            flash('ชื่อหมวดหมู่ซ้ำ กรุณาใช้ชื่ออื่น', 'warning')
            return render_template('index.html', section='category_form', form_action=url_for('new_category'), category=request.form)
        except Exception as exc:
            flash(f'เกิดข้อผิดพลาด: {exc}', 'danger')
            return render_template('index.html', section='category_form', form_action=url_for('new_category'), category=request.form)

    return render_template('index.html', section='category_form', form_action=url_for('new_category'), category={})


@app.route('/categories/edit/<int:category_id>', methods=['GET', 'POST'])
def edit_category(category_id):
    conn = get_db_connection()
    category = conn.execute('SELECT * FROM Categories WHERE id = ?', (category_id,)).fetchone()
    conn.close()

    if category is None:
        flash('ไม่พบหมวดหมู่นี้', 'danger')
        return redirect(url_for('manage_categories'))

    if request.method == 'POST':
        name = request.form['name'].strip()
        if not name:
            flash('กรุณากรอกชื่อหมวดหมู่', 'warning')
            return render_template('index.html', section='category_form', form_action=url_for('edit_category', category_id=category_id), category=request.form, is_edit=True)

        try:
            conn = get_db_connection()
            conn.execute('UPDATE Categories SET name = ? WHERE id = ?', (name, category_id))
            conn.commit()
            conn.close()
            flash('แก้ไขหมวดหมู่สำเร็จ', 'success')
            return redirect(url_for('manage_categories'))
        except sqlite3.IntegrityError:
            flash('ชื่อหมวดหมู่ซ้ำ กรุณาใช้ชื่ออื่น', 'warning')
            return render_template('index.html', section='category_form', form_action=url_for('edit_category', category_id=category_id), category=request.form, is_edit=True)
        except Exception as exc:
            flash(f'เกิดข้อผิดพลาด: {exc}', 'danger')
            return render_template('index.html', section='category_form', form_action=url_for('edit_category', category_id=category_id), category=request.form, is_edit=True)

    return render_template('index.html', section='category_form', form_action=url_for('edit_category', category_id=category_id), category=category, is_edit=True)


@app.route('/categories/delete/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM Categories WHERE id = ?', (category_id,))
        conn.commit()
        conn.close()
        flash('ลบหมวดหมู่สำเร็จ', 'success')
    except Exception as exc:
        flash('ไม่สามารถลบหมวดหมู่นี้ได้เพราะมีสินค้าเชื่อมโยงอยู่', 'danger')
    return redirect(url_for('manage_categories'))


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)

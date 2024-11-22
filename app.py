from crypt import methods
from traceback import print_tb

from flask import Flask, render_template,request, redirect, url_for, render_template, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'b2d5a69ec1f741f29d6ebeb0c41a2f4b'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
book_id = ''

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET','POST'])
def hello_world():
    user_id = session.get('user_id', '')
    if user_id == '':
        return redirect(url_for('login'))
    connexion = sqlite3.connect('bookstore.db')
    with open('schema.sql') as f:
        connexion.executescript(f.read())
    connexion.close()
    return render_template('/admin_home.html')

@app.route('/manage_books')
def manage_books():
    connexion = sqlite3.connect('bookstore.db')
    cursor = connexion.cursor()
    books = cursor.execute("SELECT * FROM books ").fetchall()
    category = cursor.execute("SELECT * FROM categories").fetchall()
    dic = {}
    for cat in category:
        dic[cat[0]] = cat[1]
    connexion.commit()
    connexion.close()
    return render_template('/books.html', books=books, categories=dic)

@app.route('/add_books')
def add_books():
    conn = sqlite3.connect('bookstore.db')
    cursor = conn.cursor()

    categories = cursor.execute("SELECT * FROM categories ").fetchall()
    conn.commit()
    conn.close()
    return render_template('/add_books.html', categories= categories)

@app.route('/add-book', methods=['POST'])
def post_book():
    if request.method == 'POST':
        book_name = request.form['book_name']
        book_description = request.form['book_description']
        category_id = request.form['category_id']
        book_number = request.form['book_number']
        book_author = request.form['book_author']
        book_price = request.form['book_price']
        book_image = request.files.get('book_image')
        if not book_name or not book_description or not category_id or not book_number or not book_author or not book_price or not book_author or not book_price:
            flash('danger', 'All fields are required!')
            return redirect(url_for('add_books'))
        image_path = './static/images/books/' + book_image.filename
        if book_image and allowed_file(book_image.filename):
            book_image.save(image_path)
        id = request.form['book_id']
        conn = sqlite3.connect('bookstore.db')
        cursor = conn.cursor()
        if id == "":
            cursor.execute("INSERT INTO books (name, description, category_id, url, nombre, price, author) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (book_name, book_description, category_id, book_image.filename, book_number, book_price, book_author))
            conn.commit()
            conn.close()
            flash('success', 'Book added successfully!')
        else:
            cursor.execute("UPDATE books SET name = ?, description = ?, category_id = ?, url = ?, nombre = ?, price = ?, author = ? WHERE id = ?",
                           (book_name, book_description, category_id, book_image.filename, book_number, book_price, book_author ,id))
            conn.commit()
            conn.close()
            flash('success', 'Book updated successfully!')
        return redirect(url_for('manage_books'))
    return redirect(url_for('manage_books'))

@app.route('/edit_book/<int:book_id>')
def edit_book(book_id):
    conn = sqlite3.connect('bookstore.db')
    cursor = conn.cursor()
    book = cursor.execute("SELECT * FROM books where id = ?", (book_id,)).fetchall()
    categories = cursor.execute("SELECT * FROM categories ").fetchall()
    conn.close()
    return render_template('/add_books.html', book=book, categories= categories)

@app.route('/delete_book/<int:book_id>')
def delete_book(book_id):
    conn = sqlite3.connect('bookstore.db')
    cursor = conn.cursor()
    book = cursor.execute("DELETE FROM books where id = ?", (book_id,))
    conn.commit()
    conn.close()
    flash('success', 'Book deleted successfully!')
    return redirect(url_for('manage_books'))
@app.route('/manage_categories')
def manage_categories():
    conn = sqlite3.connect('bookstore.db')
    cursor = conn.cursor()

    categories = cursor.execute("SELECT * FROM categories ").fetchall()
    conn.commit()
    conn.close()
    return render_template('/categories.html', categories=categories)


@app.route('/add_category')
def add_category():
    return render_template('/add_category.html')

@app.route('/add-category', methods=['POST'])
def post_category():
    category_name = request.form['category_name']
    category_description = request.form['categoryDescription']
    if category_name == "":
        flash('danger', 'Category name is required!')
        return redirect(url_for('add_category'))
    if category_description == "":
        flash('danger', 'Category description is required!')
        return redirect(url_for('add_category'))

    id = request.form['category_id']
    conn = sqlite3.connect('bookstore.db')
    cursor = conn.cursor()
    if id == "":
        cursor.execute("INSERT INTO categories (name, description) VALUES (?, ?)", (category_name,category_description))
        conn.commit()
        conn.close()
        flash('success', 'Category added successfully!')
    else:
        cursor.execute("UPDATE categories SET name = ?, description = ? WHERE id = ?", (category_name,category_description, id))
        conn.commit()
        conn.close()
        flash('success', 'Category updated successfully!')
    return redirect(url_for('manage_categories'))

@app.route('/delete_category/<int:cat_id>')
def delete_category(cat_id):
    conn = sqlite3.connect('bookstore.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM categories where id = ?", (cat_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('manage_categories'))
@app.route('/edit_category/<int:cat_id>', methods=['GET'])
def edit_category(cat_id: int):
    conn = sqlite3.connect('bookstore.db')
    cursor = conn.cursor()
    category = cursor.execute("SELECT * FROM categories where id = ?", (cat_id,)).fetchall()
    return render_template('/add_category.html', category=category)

@app.route('/manage_users')
def manage_users():
    # Implement logic for managing users
    return "Manage Users Page"

@app.route('/manage_comments', methods=['GET', 'POST'])
def manage_comments():
    conn = sqlite3.connect('bookstore.db')
    cursor = conn.cursor()
    comments = cursor.execute("SELECT * FROM comments").fetchall()
    names = []
    books = []
    for c in comments:
        user = cursor.execute("SELECT * FROM user where id = ?", (c[1],)).fetchall()
        names.append(user[0][1])
        book = cursor.execute("SELECT * FROM books where id = ?", (c[2],)).fetchall()
        books.append(book[0][1])
    conn.close()
    return render_template('/comments.html', comments = comments, names=names, books=books)

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('/login.html')


@app.route('/list_requests', methods=['GET', 'POST'])
def list_requests():
    conn = sqlite3.connect('bookstore.db')
    cursor = conn.cursor()
    commandes = cursor.execute("SELECT * FROM commande").fetchall()
    names = []
    prenoms = []
    books = []
    for c in commandes:
        user = cursor.execute("SELECT * FROM user where id = ?", (c[1],)).fetchall()
        names.append(user[0][1])
        prenoms.append(user[0][2])
        book = cursor.execute("SELECT * FROM books where id = ?", (c[2],)).fetchall()
        books.append(book[0][1])
    conn.close()
    return render_template('/tansactions.html', commandes=commandes, names = names, prenoms = prenoms, books = books)


@app.route('/history_requests', methods=['GET', 'POST'])
def history_requests():
    conn = sqlite3.connect('bookstore.db')
    cursor = conn.cursor()
    commandes = cursor.execute("SELECT * FROM commande where user_id = ?", (session['user_id'], )).fetchall()
    books = []
    for c in commandes:
        book = cursor.execute("SELECT * FROM books where id = ?", (c[2],)).fetchall()
        books.append(book[0][1])
    conn.close()
    return render_template('/transaction_details.html', commandes=commandes, books = books)

@app.route('/approve_requests/<int:val>/<int:comm_id>', methods=['GET', 'POST'])
def appove_request(val, comm_id):
    conn = sqlite3.connect('bookstore.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE commande SET accepted = ? WHERE id = ?", (val, comm_id))
    commande = cursor.execute("SELECT * FROM commande WHERE Id = ?", (comm_id,)).fetchall()
    if val == 1:
        cursor.execute("UPDATE books SET NOMBRE = NOMBRE - 1 WHERE ID = ?", (commande[0][2],))
    conn.commit()
    conn.close()
    return redirect(url_for('list_requests'))
@app.route('/by_book/<int:book_id>', methods = ['GET', 'POST'])
def by_book(book_id):
    conn = sqlite3.connect('bookstore.db')
    cursor = conn.cursor()

    cursor.execute("INSERT INTO commande(user_id, book_id, accepted) VALUES (?, ?, ?)", (session['user_id'], book_id, 0))
    commande = cursor.execute("SELECT * FROM commande").fetchall()
    print(commande)
    conn.commit()
    conn.close()
    return redirect(url_for('client_home', cat_id=0))

@app.route('/login-user', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('bookstore.db')
        cursor = conn.cursor()
        user = cursor.execute("SELECT * FROM user where username = ? and password = ?", (username, password)).fetchall()
        if not user:
            flash('danger', 'Invalid username or password!')
            return redirect(url_for('login'))
        session['user_id'] = user[0][0]
        session['user_role'] = user[0][5]
        if user[0][5] == 'client':
            return redirect(url_for('client_home', cat_id=0))
        return redirect(url_for('hello_world'))

@app.route('/client_home/<int:cat_id>', methods=['GET', 'POST'])
def client_home(cat_id:int):
    conn = sqlite3.connect('bookstore.db')
    cursor = conn.cursor()
    if cat_id == 0:
        books = cursor.execute("SELECT * FROM books WHERE nombre > 0").fetchall()
    else:
        books = cursor.execute("SELECT * FROM books WHERE category_id = ? and nombre > 0", (cat_id,)).fetchall()
    categories = cursor.execute("SELECT * FROM categories ").fetchall()
    dic = {}
    for cat in categories:
        dic[cat[0]] = cat[1]
    return render_template('/client_home.html', categories= categories, books=books, dic=dic)


@app.route('/book_details/<int:book_id>', methods=['GET', 'POST'])
def book_details(book_id):
    conn = sqlite3.connect('bookstore.db')
    cursor = conn.cursor()
    book = cursor.execute("SELECT * FROM books where id = ?", (book_id,)).fetchall()
    if not book:
        flash('danger', 'Book not found!')
        return redirect(url_for('client_home', cat_id=0))
    category = cursor.execute("SELECT * FROM categories where id = ?", (book[0][3],)).fetchall()
    comments = cursor.execute("SELECT * FROM comments where book_id = ?", (book_id,)).fetchall()
    return render_template('/book_details.html', book=book, category=category, comments = comments)

@app.route('/submit_comment/<int:book_id>', methods=['GET', 'POST'])
def submit_comment(book_id):
    if request.method == 'POST':
        print('hhhhhh')
        comment = request.form['comment']
        print(comment)
        user_id = session['user_id']
        conn = sqlite3.connect('bookstore.db')
        cursor = conn.cursor()
        print(user_id)
        cursor.execute("INSERT INTO comments (user_id, book_id, comment) VALUES(?, ?, ?)", (user_id, book_id, comment))
        conn.commit()
        conn.close()
        flash('success', 'Comment added successfully!')
        return redirect(url_for('book_details', book_id=book_id))
@app.route('/signup')
def sign_up():
    return render_template('/signup.html')

@app.route('/log-out', methods=['GET', 'POST'])
def log_out():
    session.clear()
    flash('success', 'You have been logged out successfully.')
    return redirect(url_for('login'))


@app.route('/add-user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == "" or password == "":
            flash('danger', 'Username or Password is required!')
            return redirect(url_for('sign_up'))
        conn = sqlite3.connect('bookstore.db')
        cursor = conn.cursor()
        user = cursor.execute("SELECT * FROM user where username = ?", (username,)).fetchall()
        if user != []:
            flash('danger', 'Username already is exist!')
            return redirect(url_for('sign_up'))
        cursor.execute("INSERT INTO user (username, password, user_role) VALUES (?, ?, ?)", (username, password, 'client'))
        conn.commit()
        cursor.close()
        return redirect(url_for('login'))
if __name__ == '__main__':
    app.run()

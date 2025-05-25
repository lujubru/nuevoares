from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import psycopg2
from dotenv import load_dotenv
import uuid

app = Flask(__name__)
load_dotenv()
secret_key = os.getenv('SECRET_KEY')
if not secret_key:
    raise ValueError("No SECRET_KEY set in environment variables")
print("SECRET_KEY loaded:", secret_key)
app.config['SECRET_KEY'] = secret_key
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
socketio = SocketIO(app, cors_allowed_origins="*")

# Conexión a PostgreSQL
def get_db_connection():
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    return conn

# Crear directorio para uploads si no existe
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Ruta para crear un admin por defecto
@app.route('/admin/setup', methods=['GET', 'POST'])
def admin_setup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()
        hashed_password = generate_password_hash(password)
        cur.execute(
            """
            INSERT INTO users (name, surname, phone, username, password, is_admin)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (username) DO UPDATE
            SET password = EXCLUDED.password
            RETURNING id
            """,
            ('Admin', 'Default', '1234567890', username, hashed_password, True)
        )
        admin_id = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if admin_id:
            flash(f'Admin {username} creado exitosamente. Inicia sesión.')
            return redirect(url_for('admin_login'))
        flash('Error al crear el admin.')
    return render_template('admin_setup.html')

# Ruta para el formulario inicial del usuario
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        phone = request.form['phone']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO users (name, surname, phone)
            VALUES (%s, %s, %s)
            ON CONFLICT (phone) DO UPDATE
            SET name = EXCLUDED.name, surname = EXCLUDED.surname
            RETURNING id
            """,
            (name, surname, phone)
        )
        user_id = cur.fetchone()
        if not user_id:
            flash('Error al procesar el usuario.')
            cur.close()
            conn.close()
            return render_template('index.html')
        
        user_id = user_id[0]
        cur.execute(
            """
            SELECT id FROM chats 
            WHERE user_id = %s AND status = 'open'
            """,
            (user_id,)
        )
        chat = cur.fetchone()
        if chat:
            chat_id = chat[0]
        else:
            cur.execute(
                """
                INSERT INTO chats (user_id) 
                VALUES (%s) 
                RETURNING id
                """,
                (user_id,)
            )
            chat_id = cur.fetchone()[0]
        
        conn.commit()
        session['user_id'] = user_id
        session['chat_id'] = chat_id
        cur.close()
        conn.close()
        return redirect(url_for('user_chat'))
    return render_template('index.html')

# Ruta para el login del admin
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, password FROM users WHERE username = %s AND is_admin = TRUE", (username,))
        admin = cur.fetchone()
        cur.close()
        conn.close()
        if admin:
            if check_password_hash(admin[1], password):
                session['admin_id'] = admin[0]
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Contraseña incorrecta.')
        else:
            flash('Usuario no encontrado o no es admin.')
    return render_template('admin_login.html')

# Ruta para el chat del usuario
@app.route('/chat')
def user_chat():
    if 'user_id' not in session or 'chat_id' not in session:
        return redirect(url_for('index'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT name, surname FROM users WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    cur.execute(
        "SELECT m.content, m.timestamp, u.name, u.surname, a.file_path "
        "FROM messages m JOIN users u ON m.sender_id = u.id "
        "LEFT JOIN attachments a ON m.id = a.message_id "
        "WHERE m.chat_id = %s ORDER BY m.timestamp",
        (session['chat_id'],)
    )
    messages = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('user_chat.html', user=user, messages=messages)

# Ruta para el dashboard del admin
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT c.id, u.name, u.surname, u.phone, c.unread, c.status "
        "FROM chats c JOIN users u ON c.user_id = u.id WHERE c.status = 'open'"
    )
    chats = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('admin_dashboard.html', chats=chats)

# Ruta para el chat del admin
@app.route('/admin/chat/<int:chat_id>')
def admin_chat(chat_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE chats SET unread = FALSE WHERE id = %s", (chat_id,))
    conn.commit()
    cur.execute(
        "SELECT m.content, m.timestamp, u.name, u.surname, a.file_path "
        "FROM messages m JOIN users u ON m.sender_id = u.id "
        "LEFT JOIN attachments a ON m.id = a.message_id "
        "WHERE m.chat_id = %s ORDER BY m.timestamp",
        (chat_id,)
    )
    messages = cur.fetchall()
    cur.execute("SELECT u.name, u.surname, u.phone FROM users u JOIN chats c ON u.id = c.user_id WHERE c.id = %s", (chat_id,))
    user = cur.fetchone()
    cur.execute(
        "SELECT c.id, u.name, u.surname, u.phone, c.unread, c.status "
        "FROM chats c JOIN users u ON c.user_id = u.id WHERE c.status = 'open'"
    )
    chats = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('admin_chat.html', chat_id=chat_id, user=user, messages=messages, chats=chats)

# Ruta para cerrar un chat
@app.route('/admin/close_chat/<int:chat_id>')
def close_chat(chat_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE chats SET status = 'closed' WHERE id = %s", (chat_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('admin_dashboard'))

# Ruta para enviar mensajes
@app.route('/send_message', methods=['POST'])
def send_message():
    chat_id = request.form['chat_id']
    sender_id = request.form['sender_id']
    content = request.form['content']
    file = request.files.get('file')
    is_admin = 'admin_id' in session
    file_path = None
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join('uploads', f"{uuid.uuid4()}_{filename}")
        file.save(os.path.join('static', file_path))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO messages (chat_id, sender_id, content) VALUES (%s, %s, %s) RETURNING id",
        (chat_id, sender_id, content)
    )
    message_id = cur.fetchone()[0]
    if file_path:
        cur.execute("INSERT INTO attachments (message_id, file_path) VALUES (%s, %s)", (message_id, file_path))
    cur.execute("UPDATE chats SET unread = TRUE WHERE id = %s AND %s = FALSE", (chat_id, is_admin))
    conn.commit()
    cur.close()
    conn.close()
    return '', 204

# SocketIO para mensajes en tiempo real
@socketio.on('send_message')
def handle_message(data):
    chat_id = data['chat_id']
    sender_id = data['sender_id']
    content = data['content']
    is_admin = data.get('is_admin', False)
    file = data.get('file')
    file_path = None
    if file:
        filename = secure_filename(file['name'])
        file_path = os.path.join('uploads', f"{uuid.uuid4()}_{filename}")
        with open(os.path.join('static', file_path), 'wb') as f:
            f.write(file['data'])
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO messages (chat_id, sender_id, content) VALUES (%s, %s, %s) RETURNING id",
        (chat_id, sender_id, content)
    )
    message_id = cur.fetchone()[0]
    if file_path:
        cur.execute("INSERT INTO attachments (message_id, file_path) VALUES (%s, %s)", (message_id, file_path))
    cur.execute("UPDATE chats SET unread = TRUE WHERE id = %s AND %s = FALSE", (chat_id, is_admin))
    conn.commit()
    cur.execute(
        "SELECT m.content, m.timestamp, u.name, u.surname, a.file_path "
        "FROM messages m JOIN users u ON m.sender_id = u.id "
        "LEFT JOIN attachments a ON m.id = a.message_id "
        "WHERE m.id = %s",
        (message_id,)
    )
    message = cur.fetchone()
    cur.close()
    conn.close()
    print(f"Emitting message to room {chat_id}: {message}")
    emit('new_message', {
        'content': message[0],
        'timestamp': message[1].strftime('%Y-%m-%d %H:%M:%S'),
        'name': message[2],
        'surname': message[3],
        'file_path': message[4]
    }, room=str(chat_id))

@socketio.on('join')
def on_join(data):
    chat_id = data['chat_id']
    join_room(str(chat_id))

if __name__ == '__main__':
    socketio.run(app, debug=True)
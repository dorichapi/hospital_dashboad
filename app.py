from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

app = Flask(__name__)
app.secret_key = '1912'  # セッション管理用の秘密鍵

#############################################
# データベース初期化（SQLiteを利用）
#############################################
def init_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS posts (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   title TEXT NOT NULL,
                   content TEXT NOT NULL,
                   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                   )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS strategy (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   content TEXT NOT NULL
                   )''')
    conn.commit()
    conn.close()

#############################################
# Google Sheets からデータ取得用関数
#############################################
def get_sheet_data(sheet_key, worksheet_name):
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_key(sheet_key)
    worksheet = sheet.worksheet(worksheet_name)
    data = worksheet.get_all_records()
    return data

spreadsheet_key = "1oW_EYbmi9MA9dE3ggtzA6CCjNOC6YRetVeOTzSAfCnc"

#############################################
# 戦略データの取得・保存
#############################################
def get_strategy():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT content FROM strategy ORDER BY id DESC LIMIT 1")
    result = cur.fetchone()
    conn.close()
    return result[0] if result else "まだ戦略が登録されていません。"

def save_strategy(content):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO strategy (content) VALUES (?)", (content,))
    conn.commit()
    conn.close()

#############################################
# ルート定義
#############################################
@app.route('/')
def index():
    strategy_content = get_strategy()
    authenticated = session.get('authenticated', False)
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT id, title, content, created_at FROM posts ORDER BY created_at DESC")
    posts = cur.fetchall()
    conn.close()
    return render_template('index.html', posts=posts, strategy_content=strategy_content, authenticated=authenticated)

@app.route('/post', methods=['GET', 'POST'])
def post():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)", (title, content))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('post.html')

@app.route('/dashboard')
def dashboard():
    data = get_sheet_data(spreadsheet_key, 'シート1')
    return render_template('dashboard.html', data=data)

@app.route('/update_strategy', methods=['POST'])
def update_strategy():
    password = request.form.get('password')
    if password == '1912':
        session['authenticated'] = True
    return redirect(url_for('index'))

@app.route('/save_strategy', methods=['POST'])
def save_strategy_route():
    if session.get('authenticated'):
        new_content = request.form.get('strategy')
        save_strategy(new_content)
    return redirect(url_for('index'))

@app.route('/important-metrics-1')
def important_metrics_1():
    return render_template('important_metrics.html', metric="重要指標 1")

@app.route('/important-metrics-2')
def important_metrics_2():
    return render_template('important_metrics.html', metric="重要指標 2")

@app.route('/surgeries')
def surgeries():
    return render_template('surgeries.html')

@app.route('/emergency')
def emergency():
    return render_template('emergency.html')

@app.route('/announcement', methods=['GET', 'POST'])
def announcement():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)", (title, content))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('announcement.html')

#############################################
# アプリ起動前にDB初期化
#############################################

if __name__ == '__main__':
    print(app.url_map)  # ★ ルートマップを表示
    if not os.path.exists('database.db'):
        init_db()
    app.run(debug=True)



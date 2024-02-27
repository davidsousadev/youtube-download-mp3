import os
import random
import string
import yt_dlp
import subprocess
import sqlite3
from flask import Flask, render_template, request, redirect, url_for
import re

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('audio_files.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    with app.open_resource('schema.sql', mode='r') as f:
        conn.cursor().executescript(f.read())
    conn.commit()
    conn.close()

def generate_random_filename(length=10):
    """Gera um nome de arquivo aleatório com o comprimento especificado."""
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

def download_convert_rename_and_save_to_db(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'static/downloads/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        mp3_filename = info_dict['title'] + '.mp3'
        
        return confirmation(mp3_filename, info_dict)

def clean_filename(filename):
    # Remove caracteres não desejados e substitui espaços por underscores
    cleaned_filename = re.sub(r'[^\w\s]', '', filename).replace(' ', '_')
    return cleaned_filename

def confirmation(mp3_filename, info_dict):
    # Verifica se o arquivo original existe
    return mp3_filename
    """
    if os.path.exists(mp3_filename):
        # Limpar o nome do arquivo
        # cleaned_filename = clean_filename(info_dict['title'])
        
        # Renomear o arquivo MP3 com o novo nome limpo
        random_name = generate_random_filename()
        new_filename = f"{random_name}.mp3"
        os.rename(mp3_filename, f"static/downloads/{new_filename}")  # Salva na pasta "static/downloads"
        
        # Salvar os nomes dos arquivos no banco de dados
        conn = get_db_connection()
        conn.execute("INSERT INTO files (original_name, modified_name) VALUES (?, ?)", (info_dict['title'], new_filename))
        conn.commit()
        conn.close()
        
        return new_filename
    else:
        # Se o arquivo original não existir, exibe uma mensagem de erro ou realiza outra ação apropriada
        return "Erro: O arquivo original não foi encontrado."
    """

def list_files_from_db():
    """Listar os dados do banco de dados."""
    conn = get_db_connection()
    files = conn.execute("SELECT * FROM files").fetchall()
    conn.close()
    return files

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        video_url = request.form['video_url']
        new_filename = download_convert_rename_and_save_to_db(video_url)
        return render_template('index.html', files=list_files_from_db(), message="Arquivo convertido para MP3 e salvo como: " + new_filename)
    else:
        return render_template('index.html', files=list_files_from_db())

@app.route('/clear_files', methods=['POST'])
def clear_files():
    # Excluir todos os arquivos MP3 na pasta "static/downloads"
    mp3_files = [f for f in os.listdir('static/downloads') if f.endswith('.mp3')]
    for mp3_file in mp3_files:
        os.remove(os.path.join('static/downloads', mp3_file))
    
    # Atualizar a lista de arquivos na página
    return redirect(url_for('index'))

@app.route('/clear_table', methods=['POST'])
def clear_table():
    # Limpar a tabela do banco de dados
    conn = get_db_connection()
    conn.execute("DELETE FROM files")
    conn.commit()
    conn.close()
    
    # Atualizar a lista de arquivos na página
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

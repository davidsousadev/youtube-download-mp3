import os
import random
import string
import yt_dlp
import subprocess
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

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

"""
@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        title = info_dict['title']
        file_name = title + '.mp3'
        audio = Audio(title=title, url=url, file_name=file_name)
        db.session.add(audio)
        db.session.commit()
        return redirect(url_for('index'))

"""

def download_convert_rename_and_save_to_db(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': 'static/downloads/%(title)s.%(ext)s',  # Salva na pasta "static/downloads"
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info_dict)
        
        # Converter para MP3 usando FFmpeg
        mp3_filename = filename[:-4] + '.mp3'
        subprocess.run(['ffmpeg', '-i', filename, '-vn', '-ar', '44100', '-ac', '2', '-ab', '192k', '-f', 'mp3', mp3_filename], check=True)
        
        # Excluir o arquivo WebM após a conversão
        os.remove(filename)
        
        # Renomear o arquivo MP3 com um número aleatório de 10 dígitos
        random_name = generate_random_filename()
        new_filename = f"{random_name}.mp3"
        os.rename(mp3_filename, f"static/downloads/{new_filename}")  # Salva na pasta "static/downloads"
        
        # Salvar os nomes dos arquivos no banco de dados
        conn = get_db_connection()
        conn.execute("INSERT INTO files (original_name, modified_name) VALUES (?, ?)", (info_dict['title'], new_filename))
        conn.commit()
        conn.close()
        
        return "Sucesso!!!"

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
        return render_template('index.html', files=list_files_from_db(), message="Arquivo convertido para MP3 e salvo com " + new_filename)
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

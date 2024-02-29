from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
import os
import yt_dlp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///audios.db'
db = SQLAlchemy(app)

class Audio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250))
    url = db.Column(db.String(500))
    file_name = db.Column(db.String(500))

@app.route('/')
def index():
    audios = Audio.query.all()
    return render_template('index.html', audios=audios)

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')  # Use get method to avoid KeyError if 'url' is empty
    if not url:
        return redirect(url_for('index'))  # Redirect to index if URL is empty
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            id = info_dict['id']
            title = info_dict['title']
            audio = Audio(title=title, url=url, file_name=id)
            db.session.add(audio)
            db.session.commit()
    except Exception as e:
        print(f"Error occurred during download: {e}")
    return redirect(url_for('index'))

@app.route('/play/<int:audio_id>')
def play(audio_id):
    audio = Audio.query.get(audio_id)
    if not audio:
        return redirect(url_for('index'))  # Redirect to index if audio not found
    file_path = os.path.join('downloads', f"{audio.file_name}.mp3")
    return send_file(file_path)

@app.route('/editar/<int:audio_id>', methods=['POST'])
def editar(audio_id):
    new_title = request.form.get('new_title')
    if new_title:
        audio = Audio.query.get(audio_id)
        if audio:
            audio.title = new_title
            db.session.commit()
    return redirect(url_for('index'))

@app.route('/excluir/<int:audio_id>', methods=['POST'])
def excluir(audio_id):
    audio = Audio.query.get(audio_id)
    if audio:
        db.session.delete(audio)
        db.session.commit()
        file_path = os.path.join('downloads', f"{audio.file_name}.mp3")
        if os.path.exists(file_path):
            os.remove(file_path)
    return redirect(url_for('index'))

@app.route('/limpar-downloads', methods=['POST'])
def limpar_downloads():
    try:
        folder = 'downloads'
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)
    except Exception as e:
        print(f"Error occurred while clearing downloads: {e}")
    return redirect(url_for('index'))

@app.route('/limpar-tabela', methods=['POST'])
def limpar_tabela():
    try:
        Audio.query.delete()
        db.session.commit()
    except Exception as e:
        print(f"Error occurred while clearing table: {e}")
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
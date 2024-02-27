import os
import random
import string
import yt_dlp
# import subprocess


def generate_random_filename(length=10):
    """Gera um nome de arquivo aleatório com o comprimento especificado."""
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

def download_convert_rename_and_save_to_db():
    url = str(input("Digite a url: ").strip())
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
        filename = ydl.prepare_filename(info_dict)
        mp3_filename = filename[:-4] + '.mp3'
        """
        random_name = generate_random_filename()
        new_filename = f"{random_name}.mp3"
        os.rename(mp3_filename, f"static/downloads/{new_filename}")  # Salva na pasta "static/downloads"
        
        
        conn = get_db_connection()
        conn.execute("INSERT INTO files (original_name, modified_name) VALUES (?, ?)", (info_dict['title'], new_filename))
        conn.commit()
        conn.close()
        """

        return info_dict["title"]
    
if __name__ == '__main__':
    
    print(download_convert_rename_and_save_to_db())
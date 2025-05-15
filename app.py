from flask import Flask, request, send_file, jsonify, send_from_directory, after_this_request
from flask_cors import CORS
import yt_dlp
import os
import shutil
import uuid
from zipfile import ZipFile

app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return send_from_directory("frontend", "index.html")

@app.route('/get_info', methods=['POST'])
def get_info():
    data = request.get_json()
    url = data.get('url')

    try:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'extract_flat': False,  # extrai dados completos dos vídeos
            'ignoreerrors': True,
            'playliststart': 1,
            'playlistend': 1000,  # ajuste ou remova para pegar todas as músicas
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        if 'entries' in info:
            items = []
            for entry in info['entries']:
                if not entry:
                    continue
                title = entry.get('title', 'Sem título')
                thumbnail = entry.get('thumbnail')
                if not thumbnail:
                    thumbnail = f"https://img.youtube.com/vi/{entry.get('id')}/hqdefault.jpg"
                items.append({
                    'title': title,
                    'thumbnail': thumbnail
                })

            return jsonify({
                'isPlaylist': True,
                'title': info.get('title', 'Playlist sem título'),
                'items': items
            })
        else:
            # Caso seja vídeo único
            return jsonify({
                'isPlaylist': False,
                'title': info.get('title', 'Sem título'),
                'thumbnail': info.get('thumbnail', '')
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download', methods=['POST'])
def download_playlist():
    data = request.get_json()
    url = data.get('url')
    format_type = data.get('format')

    if not url or format_type not in ['mp3', 'mp4']:
        return jsonify({"error": "Dados inválidos"}), 400

    session_id = str(uuid.uuid4())
    download_path = os.path.join(DOWNLOAD_FOLDER, session_id)
    os.makedirs(download_path, exist_ok=True)

    print(f"Iniciando download: URL={url} | formato={format_type} | pasta={download_path}")

    ydl_opts = {
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'format': 'bestaudio/best' if format_type == 'mp3' else 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4' if format_type == 'mp4' else None,
        'postprocessors': [],
        'quiet': True,
        'no_warnings': True,
        'ffmpeg_location': r'C:\Users\zackg\Documents\ffmpeg-7.1.1-essentials_build\bin'  # ajuste seu caminho do ffmpeg aqui
    }

    if format_type == 'mp3':
        ydl_opts['postprocessors'].append({
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            if 'entries' in info:
                print(f"Playlist com {len(info['entries'])} vídeos.")
            else:
                print("Vídeo único.")
    except Exception as e:
        print(f"Erro ao baixar: {e}")
        shutil.rmtree(download_path, ignore_errors=True)
        return jsonify({"error": str(e)}), 500

    files = []
    for root, _, filenames in os.walk(download_path):
        for filename in filenames:
            files.append(filename)
            print(f"Arquivo baixado: {filename}")

    if not files:
        shutil.rmtree(download_path, ignore_errors=True)
        return jsonify({"error": "Nenhum arquivo foi baixado."}), 500

    zip_path = os.path.join(DOWNLOAD_FOLDER, f"{session_id}.zip")
    with ZipFile(zip_path, 'w') as zipf:
        for filename in files:
            filepath = os.path.join(download_path, filename)
            zipf.write(filepath, arcname=filename)

    shutil.rmtree(download_path, ignore_errors=True)

    @after_this_request
    def cleanup(response):
        try:
            os.remove(zip_path)
            print(f"Arquivo zip {zip_path} removido após envio.")
        except Exception as e:
            print(f"Erro ao remover zip: {e}")
        return response

    print(f"Download finalizado e zip criado: {zip_path}")
    return send_file(
        zip_path,
        mimetype='application/zip',
        as_attachment=True,
        download_name='playlist.zip',
        conditional=False,
    )

if __name__ == '__main__':
    print("Rodando o Flask na porta 5000...")
    app.run(debug=True, port=5000)

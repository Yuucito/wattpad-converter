import os
import subprocess
from flask import Flask, render_template, request, send_file
from uuid import uuid4
import zipfile

app = Flask(__name__)
DOWNLOAD_DIR = 'downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        formats = request.form.getlist('formats')  # Lista de formatos seleccionados
        temp_filename = str(uuid4())  # Nombre base temporal
        output_files = []

        # Descargar el archivo como EPUB por defecto usando fanficfare
        epub_path = os.path.join(DOWNLOAD_DIR, f"{temp_filename}.epub")
        subprocess.run(['fanficfare', '-f', 'epub', '-o', epub_path, url])

        for fmt in formats:
            if fmt == 'epub':
                output_files.append(epub_path)
            else:
                converted_path = os.path.join(DOWNLOAD_DIR, f"{temp_filename}.{fmt}")
                subprocess.run(['ebook-convert', epub_path, converted_path])
                output_files.append(converted_path)

        # Si solo un archivo, lo enviamos directamente
        if len(output_files) == 1:
            return send_file(output_files[0], as_attachment=True)
        else:
            # Si son varios, los comprimimos en un zip
            zip_path = os.path.join(DOWNLOAD_DIR, f"{temp_filename}.zip")
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file_path in output_files:
                    zipf.write(file_path, os.path.basename(file_path))
            return send_file(zip_path, as_attachment=True)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

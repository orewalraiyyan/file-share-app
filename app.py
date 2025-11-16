import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, abort

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with secure key

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mp3', 'zip', 'rar'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB max limit

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def home():
    download_url = None
    error = None
    filename_to_show = None
    if request.method == 'POST':
        if 'upload_file' in request.form:
            # Handle file upload (Sender)
            if 'file' not in request.files:
                error = 'No file part'
            else:
                file = request.files['file']
                if file.filename == '':
                    error = 'No file selected'
                elif file and allowed_file(file.filename):
                    original = file.filename
                    unique_id = uuid.uuid4().hex
                    stored_name = f"{unique_id}_{original}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], stored_name))
                    download_url = url_for('download_file', filename=stored_name, _external=True)
                    filename_to_show = original
                else:
                    error = 'File type not allowed'

        elif 'download_link' in request.form:
            # Handle link paste (Receiver)
            link = request.form.get('download_link').strip()
            if not link:
                error = 'Please paste a valid download link'
            else:
                return redirect(link)

    return render_template('index.html', download_url=download_url, filename=filename_to_show, error=error)


@app.route('/files/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    else:
        abort(404)


if __name__ == '__main__':
    app.run(debug=True)
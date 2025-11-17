import os
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory, abort

app = Flask(__name__)

# It's better to read the secret key from an environment variable, fallback to fixed key for dev
app.secret_key = os.environ.get('SWIFTY_SHARE_SECRET_KEY', 'dev_secret_key_change_this')

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mp3', 'zip', 'rar', 'apk'}
MAX_FILE_SIZE = 3 * 1024 * 1024 * 1024  # 3GB limit

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files part in the request'}), 400

    files = request.files.getlist('files[]')
    if not files:
        return jsonify({'error': 'No files selected for uploading'}), 400

    links = []
    for file in files:
        if file and allowed_file(file.filename):
            unique_id = str(uuid.uuid4())
            filename = f"{unique_id}_{file.filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            download_link = f"/download?file_id={unique_id}&filename={file.filename}"
            links.append(download_link)
        else:
            return jsonify({'error': f'File type not allowed: {file.filename}'}), 400

    return jsonify({'links': links})


@app.route('/download')
def download_file():
    file_id = request.args.get('file_id')
    original_filename = request.args.get('filename')

    if not file_id or not original_filename:
        abort(400, "Invalid download link")

    for stored_file in os.listdir(app.config['UPLOAD_FOLDER']):
        if stored_file.startswith(file_id + '_') and stored_file.endswith(original_filename):
            return send_from_directory(app.config['UPLOAD_FOLDER'], stored_file, as_attachment=True)

    abort(404, "File not found")


if __name__ == '__main__':
    app.run(debug=True)

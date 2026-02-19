import os
import subprocess
import uuid
import zipfile
import glob
import threading
import time
from flask import Flask, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.abspath('uploads')
app.config['OUTPUT_FOLDER'] = os.path.abspath('output')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

CONVERSION_MAP = {
    'pdf':  ['pptx', 'docx', 'png', 'jpg', 'jpeg'],
    'pptx': ['pdf'],
    'docx': ['pdf', 'md'],
    'md':   ['pdf', 'docx'],
    'png':  ['jpg', 'jpeg', 'webp', 'pdf'],
    'jpg':  ['png', 'jpeg', 'webp', 'pdf'],
    'jpeg': ['png', 'jpg', 'webp', 'pdf'],
    'webp': ['png', 'jpg', 'jpeg', 'pdf'],
    'mp3':  ['mp4', 'webm'],
    'mp4':  ['webm', 'mp3'],
    'webm': ['mp4', 'mp3'],
}

ALLOWED_EXTENSIONS = set(CONVERSION_MAP.keys())

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Maps download_id -> upload file path so we can clean up both after download
pending_cleanups = {}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_ext(filename):
    return filename.rsplit('.', 1)[1].lower()


def _run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)


def convert_file(input_path, output_path, in_ext, out_ext):
    doc_formats = {'pdf', 'pptx', 'docx'}
    image_formats = {'png', 'jpg', 'jpeg', 'webp'}
    media_formats = {'mp3', 'mp4', 'webm'}
    actual_output = output_path

    if in_ext in image_formats and out_ext == 'pdf':
        _run(['convert', input_path, output_path])

    elif in_ext == 'pdf' and out_ext in image_formats:
        fmt_flag = '-png' if out_ext == 'png' else '-jpeg'
        stem = output_path.rsplit('.', 1)[0]
        _run(['pdftoppm', fmt_flag, '-r', '150', input_path, stem])
        pages = sorted(glob.glob(f"{stem}-*"))
        if not pages:
            raise RuntimeError("pdftoppm produced no output files")
        zip_path = stem + '.zip'
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for page in pages:
                zf.write(page, os.path.basename(page))
                os.remove(page)
        actual_output = zip_path

    elif in_ext in doc_formats and out_ext in doc_formats:
        outdir = app.config['OUTPUT_FOLDER']
        _run(['libreoffice', '--headless', '--convert-to', out_ext,
              '--outdir', outdir, os.path.abspath(input_path)])
        input_stem = os.path.splitext(os.path.basename(input_path))[0]
        lo_output = os.path.join(outdir, f"{input_stem}.{out_ext}")
        if not os.path.exists(lo_output):
            matches = [
                os.path.join(outdir, f) for f in os.listdir(outdir)
                if f.endswith(f'.{out_ext}') and f != os.path.basename(output_path)
            ]
            if not matches:
                raise RuntimeError(f"LibreOffice output not found: {lo_output}")
            lo_output = max(matches, key=os.path.getmtime)
        os.rename(lo_output, output_path)

    elif in_ext in image_formats and out_ext in image_formats:
        _run(['convert', input_path, output_path])

    elif in_ext in media_formats and out_ext in media_formats:
        if in_ext == 'mp3' and out_ext in {'mp4', 'webm'}:
            _run(['ffmpeg', '-y', '-f', 'lavfi', '-i', 'color=c=black:s=1280x720',
                  '-i', input_path, '-shortest', '-c:v', 'libx264',
                  '-c:a', 'aac', output_path])
        else:
            _run(['ffmpeg', '-y', '-i', input_path, output_path])

    elif in_ext == 'md' or out_ext == 'md':
        if out_ext == 'pdf':
            # Convert md -> docx first, then docx -> pdf via LibreOffice
            tmp_docx = output_path.replace('.pdf', '_tmp.docx')
            _run(['pandoc', input_path, '-o', tmp_docx])
            outdir = app.config['OUTPUT_FOLDER']
            _run(['libreoffice', '--headless', '--convert-to', 'pdf',
                  '--outdir', outdir, os.path.abspath(tmp_docx)])
            tmp_stem = os.path.splitext(os.path.basename(tmp_docx))[0]
            lo_output = os.path.join(outdir, f"{tmp_stem}.pdf")
            os.rename(lo_output, output_path)
            os.remove(tmp_docx)
        else:
            _run(['pandoc', input_path, '-o', output_path])

    else:
        raise ValueError(f"Unsupported conversion: {in_ext} to {out_ext}")

    return actual_output


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Unsupported or missing file'}), 400
    ext = get_ext(file.filename)
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    return jsonify({'file_id': filename, 'options': CONVERSION_MAP[ext]})


@app.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    file_id = data.get('file_id', '')
    target = data.get('target', '').lower()

    if not file_id or not target:
        return jsonify({'error': 'Missing file_id or target'}), 400

    in_ext = get_ext(file_id)
    if target not in CONVERSION_MAP.get(in_ext, []):
        return jsonify({'error': 'Invalid conversion target'}), 400

    input_path = os.path.join(app.config['UPLOAD_FOLDER'], file_id)
    if not os.path.exists(input_path):
        return jsonify({'error': 'File not found'}), 404

    out_filename = f"{uuid.uuid4().hex}.{target}"
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], out_filename)

    try:
        actual_output = convert_file(input_path, output_path, in_ext, target)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    download_id = os.path.basename(actual_output)
    # Register the upload file for cleanup after download
    pending_cleanups[download_id] = input_path
    return jsonify({'download_id': download_id})


@app.route('/download/<path:file_id>')
def download(file_id):
    path = os.path.realpath(os.path.join(app.config['OUTPUT_FOLDER'], file_id))
    if not path.startswith(app.config['OUTPUT_FOLDER']):
        return jsonify({'error': 'Invalid path'}), 400
    if not os.path.exists(path):
        return jsonify({'error': 'File not found'}), 404

    upload_to_delete = pending_cleanups.pop(file_id, None)
    response = send_file(path, as_attachment=True)

    def cleanup():
        time.sleep(3)
        for f in filter(None, [path, upload_to_delete]):
            try:
                os.remove(f)
            except Exception:
                pass

    threading.Thread(target=cleanup, daemon=True).start()
    return response


if __name__ == '__main__':
    app.run(debug=True)
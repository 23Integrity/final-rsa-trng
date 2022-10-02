import os
from io import BytesIO
from zipfile import ZipFile

from flask import Flask, flash, request, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from flask import send_from_directory

import encryptive

UPLOAD_FOLDER = os.path.basename('/uploads')
ALLOWED_EXTENSIONS = {'txt', 'pem', 'pom'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def main_page():
    return '''
    <!doctype html>
    <title>RSA</title>
    <h1><a href="/generate">Generate keys</h1>
    <h1><a href="/sign">Sign a file</h1>
    <h1><a href="/verify">Verify signature</h1>
    '''


@app.route('/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'POST':
        if encryptive.generate_keys():
            stream = BytesIO()
            with ZipFile(stream, 'w') as zf:
                zf.write("public.pem", "public.pem")
                zf.write("private.pem", "private.pem")
            stream.seek(0)
            return send_file(
                stream,
                as_attachment=True,
                download_name="archive.zip"
            )
        else:
            return '''
                <!doctype html>
                <title>RSA</title>
                <h1>Generating keys failed</h1>
                <p><a href="/generate">Generate keys</a></p>
                <p><a href="/sign">Sign a file</a></p>
                <p><a href="/verify">Verify a file</a></p>
            '''
    return '''
        <!doctype html>
        <title>RSA</title>
        <form method=post enctype=multipart/form-data>
            <input type=submit value=Generate>
        </form>
    '''


@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        if 'public_key' not in request.files:
            flash('No public_key part')
            return redirect(request.url)

        file = request.files['file']
        public_key = request.files['public_key']

        if file:
            status = encryptive.check_signature(file, public_key)
            print(status)
            if status:
                return '''
                            <!doctype html>
                            <title>RSA</title>
                            <h1>Signature correct</h1>
                            '''
            else:
                return '''
            <!doctype html>
            <title>RSA</title>
            <h1>Signature incorrect</h1>
            <p><a href="/generate">Generate keys</a></p>
            <p><a href="/sign">Sign a file</a></p>
            <p><a href="/verify">Verify a file</a></p>
            '''

    return '''
            <!doctype html>
            <title>RSA</title>
            <h1>Verify signature</h1>
            <form method=post enctype=multipart/form-data>
                <p>File to verify</p>
                <input type=file name=file>
                <p>Public key</p>
                <input type=file name=public_key>
                <input type=submit value=Upload>
            </form>
            '''


@app.route('/sign', methods=['GET', 'POST'])
def sign():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        if 'private_key' not in request.files:
            flash('No private_key part')
            return redirect(request.url)
        file = request.files['file']
        private_key = request.files['private_key']
        if file and allowed_file(file.filename):
            encryptive.sign_file(file, private_key)
            return send_file('signed_file', as_attachment=True, download_name='signed_file')
    if os.path.exists("signed_file"):
        os.remove('signed_file')
    return  '''
            <!doctype html>
            <title>RSA</title>
            <h1>Sign a file</h1>
            <h3>Upload new File</h3>
            <form method=post enctype=multipart/form-data>
                <p>File to sign</p>
                <input type=file name=file>
                <p>Private key</p>
                <input type=file name=private_key>
                <input type=submit value=Upload>
            </form>
            '''


@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


if __name__ == '__main__':
    app.run()

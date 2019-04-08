import os
import subprocess
from pathlib import Path
from random import randint
import shutil
from flask import Flask, request, send_from_directory, json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['TASK_FOLDER'] = Path(__file__).absolute().parent / 'pending_tasks'
app.config['TAG_RESULT_FOLDER'] = Path(__file__).absolute().parent / 'tag_results'
app.config['STATIC_CONTENT_FOLDER'] = Path(__file__).absolute().parent.parent / 'crotalpath_web_app'
if os.path.isdir(app.config['TASK_FOLDER']):
    shutil.rmtree(app.config['TASK_FOLDER'])
if os.path.isdir(app.config['TAG_RESULT_FOLDER']):
    shutil.rmtree(app.config['TAG_RESULT_FOLDER'])
os.mkdir(app.config['TASK_FOLDER'])
os.mkdir(app.config['TAG_RESULT_FOLDER'])


@app.route('/<path:path>')
def send_html(path):
    return send_from_directory(app.config['STATIC_CONTENT_FOLDER'], path)


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory(app.config['STATIC_CONTENT_FOLDER'] / 'js', path)


@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory(app.config['STATIC_CONTENT_FOLDER'] / 'css', path)


@app.route("/tasks", methods=['POST'])
def handle_job_creation():
    task_id = str(randint(10000, 99999))
    task_folder_path = app.config['TASK_FOLDER'] / task_id
    result_file_path = app.config['TAG_RESULT_FOLDER'] / task_id
    os.mkdir(task_folder_path)
    uploaded_files = request.files.getlist("file")

    for file in uploaded_files:
        file.save(os.path.join(task_folder_path, secure_filename(file.filename)))

    cmd = 'cd .. && python3 -m crotalpath_core -t 1 -f ' + str(task_folder_path) + ' -o ' + str(result_file_path)

    subprocess.Popen(cmd, shell=True)

    response = app.response_class(
        status=202,
        mimetype='application/text'
    )
    response.headers['location'] = 'tasks/' + task_id

    return response


@app.route("/tasks/<path:path>", methods=['GET'])
def serve_job(path):
    result_file_path = app.config['TAG_RESULT_FOLDER'] / path
    status = 200
    response = app.response_class(
        response=json.dumps({}),
        status=status,
        mimetype='application/json'
    )

    if os.path.isfile(result_file_path):
        status = 303
        response = app.response_class(
            response=json.dumps({}),
            status=status,
            mimetype='application/json'
        )
        response.headers['location'] = '/tags/' + path

    return response


@app.route("/tags/<path:path>", methods=['GET'])
def serve_tag(path):
    result_file_path = app.config['TAG_RESULT_FOLDER'] / path
    status = 404
    response = json.dumps({})
    if os.path.isfile(result_file_path):
        status = 200
        f = open(result_file_path, "r")
        response = f.read()

    response = app.response_class(
        response=response,
        status=status,
        mimetype='application/json'
    )
    return response


if __name__ == "__main__":
    app.run(host='0.0.0.0')

from flask import Flask, request, jsonify, render_template, send_file
import cv2
import numpy as np
from datetime import datetime
import os
import json

from model.detector import detect_objects, process_video
from utils.db import insert_history, get_last_result
from utils.report import generate_pdf, generate_excel

app = Flask(__name__, static_url_path='', static_folder='static')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process_image():
    file = request.files['image']
    img_bytes = file.read()
    img_array = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    output_img, count = detect_objects(img)
    cv2.imwrite('static/result.jpg', output_img)

    insert_history(datetime.now(), count)

    return jsonify(count=count)


@app.route('/report', methods=['GET'])
def download_report():
    report_format = request.args.get('format', 'pdf')

    # Получаем последний результат из базы данных
    row = get_last_result()
    if not row:
        return 'Нет данных для отчета', 404

    count = row[1]

    if report_format == 'pdf':
        path = generate_pdf(count)
    elif report_format == 'excel':
        path = generate_excel(count)
    else:
        return 'Неверный формат', 400

    return send_file(path, as_attachment=True)


@app.route('/process_video', methods=['POST'])
def process_video_route():
    file = request.files['video']
    video_path = 'static/uploaded_video.mp4'
    output_path = 'static/result_video.mp4'

    file.save(video_path)
    count = process_video(video_path, output_path)

    # Логирование или сохранение истории можно добавить здесь при необходимости
    return jsonify({
        "count": count,
        "video_url": "/static/result_video.mp4"
    })

@app.route('/static/<path:filename>')
def custom_static(filename):
    return send_file(f'static/{filename}', mimetype='video/mp4')
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 18:05:38 2024

@author: Administrator
"""

##########----------BEST----PERFECT-----------GREAT-----------ALL BUGS OVER----------###################
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_session import Session
import requests
import logging
import os
from pymongo import MongoClient
import secrets
import datetime
from flask import Flask, request, jsonify, session
import datetime
from datetime import timedelta
import uuid
import requests
from flask import make_response
app = Flask(__name__)


UPLOAD_FOLDER_IMAGES = "/app/uploads/images"
UPLOAD_FOLDER_AUDIOS = "/app/uploads/audios"
#UPLOAD_FOLDER_IMAGES = r'C:\inetpub\viabl\deploymentServer2\apps\_scripts\Whatsapp\images'
#UPLOAD_FOLDER_AUDIOS = r'C:\inetpub\viabl\deploymentServer2\apps\_scripts\Whatsapp\audios'
os.makedirs(UPLOAD_FOLDER_IMAGES, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_AUDIOS, exist_ok=True)

# Enable CORS for all origins
CORS(app)

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route("/upload_audio", methods=["POST"])
def upload_audio():
    if "file" not in request.files:
        return jsonify({"message": "No audio file uploaded"}), 400

    file = request.files["file"]
    email = request.form.get("email")
    Report_id = request.form.get("Report_id")

    if not email:
        return jsonify({"message": "Email is required"}), 400

    # Generate Unique ID for file
    file_id = str(uuid.uuid4())
    filename = f"{Report_id}_audio.mp3"
    filepath = os.path.join(UPLOAD_FOLDER_AUDIOS, filename)

    # Save file
    file.save(filepath)

    # Store in MongoDB (Uncomment if needed)
    # mongo.db.audio_files.insert_one({"email": email, "file_id": file_id, "filename": filename})

    return jsonify({"message": "Audio uploaded successfully.", "file_id": file_id,"audioUrl":"https://patientsafe.global-value-web.in//deploymentServer2//apps//_scripts//Whatsapp//audios//"+filename}), 200

# STEP 4: Upload Image
@app.route("/upload_image", methods=["POST"])
def upload_image():
    if "file" not in request.files:
        return jsonify({"message": "No image file uploaded"}), 400

    file = request.files["file"]
    email = request.form.get("email")
    Report_id = request.form.get("Report_id")

    if not email:
        return jsonify({"message": "Email is required"}), 400
    
    # Check existing files for this Report_id
    existing_files = [
        f for f in os.listdir(UPLOAD_FOLDER_IMAGES)
        if f.startswith(f"{Report_id}_img") and f.endswith("_image.png")
    ]
    
    # Find next available image number
    if existing_files:
        # Extract the numbers (img1, img2, etc.)
        numbers = []
        for fname in existing_files:
            try:
                num = int(fname.split("_img")[1].split("_")[0])  # get the X from imgX
                numbers.append(num)
            except:
                pass
        next_num = max(numbers) + 1 if numbers else 1
    else:
        next_num = 1

    # Generate filename
    file_id = str(uuid.uuid4())
    filename = f"{Report_id}_img{next_num}_image.png"
    filepath = os.path.join(UPLOAD_FOLDER_IMAGES, filename)


    # Save file
    file.save(filepath)

    # Store in MongoDB (Uncomment if needed)
    # mongo.db.image_files.insert_one({"email": email, "file_id": file_id, "filename": filename})

    return jsonify({"message": "Image uploaded successfully.", "file_id": file_id,"imageUrl":"https://patientsafe.global-value-web.in//deploymentServer2//apps//_scripts//Whatsapp//images//"+filename}), 200
# for api testing purpose
@app.route('/invoke', methods=['POST'])
def invoke():
    """
    Expects JSON:
    {
      "url": "http://192.168.1.43:6301/medical-terms",
      "method": "POST",            # optional, defaults to "GET"
      "data":   { "text": "…" }    # for GET → query params; for POST → JSON body
    }
    """
    payload = request.get_json(force=True)
    url     = payload.get('url')
    method  = payload.get('method', 'GET').upper()
    data    = payload.get('data', {})

    if not url:
        return jsonify({"error": "Missing 'url' field"}), 400

    try:
        if method == 'GET':
            upstream = requests.get(url, params=data, timeout=(3, 20))
        elif method == 'POST':
            upstream = requests.post(url, json=data, timeout=(3, 20))
        else:
            return jsonify({"error": f"Unsupported method '{method}'"}), 400

    except requests.RequestException as e:
        return jsonify({"error": "Upstream request failed", "details": str(e)}), 502

    # Relay status code and body, and preserve Content-Type
    resp = make_response(upstream.content, upstream.status_code)
    if 'Content-Type' in upstream.headers:
        resp.headers['Content-Type'] = upstream.headers['Content-Type']
    return resp        
        
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9096,
        debug=False,
        # If you have SSL certificates, you can use them like this:
        ssl_context=('/app/keys/xr-cert.pem', '/app/keys/xr-key.pem'))

##########----------BEST----PERFECT-----------GREAT-----------ALL BUGS OVER----------###################
from app import app, db
from flask import request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User, File

import pyzipper
import os

import subprocess, platform

from datetime import datetime

KEY = os.getenv("ENC_KEY")


@app.route("/list")
@jwt_required()
def get_backups():
    user = db.session.query(User).filter_by(username = get_jwt_identity()).first()

    files = db.session.query(File).filter_by(owner_id = user.id).all()
    return jsonify([file.name for file in files]), 200


@app.route("/upload", methods=['POST'])
@jwt_required()
def create_backup():
    file = request.files["arquivo"]
    user = db.session.query(User).filter_by(username = get_jwt_identity()).first()

    try:
        with pyzipper.AESZipFile(file, 'r') as zipfile:
            zipfile.extractall(f'backups/{user.username}/{file.filename[:-4]}/')
        
        base_path = f"backups/{user.username}/{file.filename}"
        with pyzipper.AESZipFile(
            f'backups/{user.username}/{file.filename}', 
            'w', compression=pyzipper.ZIP_LZMA
        ) as zipfile:
            zipfile.setpassword(KEY.encode())
            zipfile.setencryption(pyzipper.WZ_AES, nbits=256)

            for folder, sub_folder, filenames in os.walk(f'backups/{user.username}/{file.filename[:-4]}/'):
                for filename in filenames:
                    file_path = os.path.join(folder, filename)
                    arcname = os.path.relpath(file_path, os.path.dirname(base_path))
                    
                    zipfile.write(file_path, arcname=arcname)
        

        if platform.system() == "Windows":
            subprocess.run(f'rmdir /s /q "backups/{user.username}/{file.filename[:-4]}/"', shell = True)
        elif platform.system() == "Linux":
            subprocess.run(f'sudo rm -r "backups/{user.username}/{file.filename[:-4]}/"')

    
    except Exception:
        return jsonify({
            "msg": "Error while uploading file."
        }), 400
    
    try:
        file_object = File(name = file.filename, owner = user)

        db.session.add(file_object)
        db.session.commit()
    except:
        file_object = db.session.query(File).filter_by(name = file.filename).first()
        file_object.date = datetime.now()

        db.session.commit()


    return jsonify({
        "msg": "Uploaded files."
    }), 201


@app.route("/download/<file_name>")
@jwt_required()
def download_backup(file_name):
    user = db.session.query(User).filter_by(username = get_jwt_identity()).first()
    file_exists = db.session.query(File).filter_by(name = file_name, owner = user)

    if not file_exists:
        return jsonify({
            "msg": "File does not exist."
        }), 404
    
    return send_file(f'../backups/{user.username}/{file_name}.zip'), 200


@app.route("/delete/<file_name>", methods=['DELETE'])
@jwt_required()
def delete_backup(file_name):
    user = db.session.query(User).filter_by(username = get_jwt_identity()).first()
    file_exists = db.session.query(File).filter_by(name = f'{file_name}.zip', owner_id = user.id).first()

    if not file_exists:
        return jsonify({
            "msg": "File does not exist."
        }), 404
    
    if platform.system() == "Windows":
        subprocess.run(f'del /s /q "{file_exists.name}"', shell = True)
    elif platform.system() == "Linux":
        subprocess.run(f'sudo rm "{file_exists.name}"', shell = True)

    db.session.delete(file_exists)
    db.session.commit()

    return jsonify({
        "msg": "Deleted file."
    }), 200

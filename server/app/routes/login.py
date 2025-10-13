from app import app, db
from ..models import User
from flask import request, jsonify
from flask_jwt_extended import create_access_token
from datetime import timedelta
import os


@app.route('/register', methods=['POST'])
def register():
    username = request.json["username"]
    password = request.json["password"]

    user = db.session.query(User).filter_by(username = username).first()
    if user:
        return jsonify({
            "msg": "User already exists"
        }), 401
    
    user = User(username = username)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    os.mkdir(f'backups/{username}/')

    return jsonify({
        "Token": create_access_token(username)
    }), 201


@app.route("/login", methods=['POST'])
def login():
    username = request.json["username"]
    password = request.json["password"]

    user = db.session.query(User).filter_by(
        username = username
    ).first()

    if not user or not user.check_password(password):
        return jsonify({
            "msg": "Got user or password wrong."
        }), 404
    
    return jsonify({
        "Token": create_access_token(
            username, expires_delta=timedelta(days=7)
        )
    }), 200

from flask import Blueprint, jsonify, request
from .models import Blogger
from . import db
api = Blueprint('api', __name__)

@api.route('/add_blogger', methods=['POST'])
def add_blogger():
    data = request.json

    if not data or 'prompt' not in data or 'response' not in data:
        return jsonify({"error": "Invalid input"}), 400

    prompt = data['prompt']
    response_list = data['response']

    # Ensure response_list is a list of strings
    if not isinstance(response_list, list) or not all(isinstance(item, str) for item in response_list):
        return jsonify({"error": "Response must be a list of strings"}), 400

    try:
        new_blogger = Blogger(prompt=prompt, response_list=response_list)
        db.session.add(new_blogger)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Blogger added successfully"}), 201

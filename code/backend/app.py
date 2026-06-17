"""
REST API CityReport - Εξυπηρετει τους πολιτες.
Δεν απαιτειται authentication.
"""
from flask import Flask, jsonify, request
import db
import os
import uuid
import external_apis

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return jsonify({"message": "CityReport API is running"})

@app.route("/categories", methods=["GET"])
def get_categories():
    return jsonify(db.get_categories())

@app.route("/statuses", methods=["GET"])
def get_statuses():
    return jsonify(db.get_statuses())

@app.route("/problems", methods=["POST"])
def create_problem():
    title = request.form.get("title")
    description = request.form.get("description")
    category_id = request.form.get("category_id", type=int)
    latitude = request.form.get("latitude", type=float)
    longitude = request.form.get("longitude", type=float)
    if not title or not category_id:
        return jsonify({"error": "title and category_id are required"}), 400
    photo_path = None
    if "photo" in request.files:
        photo = request.files["photo"]
        if photo.filename:
            filename = f"{uuid.uuid4().hex[:8]}_{photo.filename}"
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            photo.save(save_path)
            photo_path = save_path
    address = external_apis.get_address_from_coordinates(latitude, longitude)
    ticket_id = db.insert_problem(title, description, category_id, latitude, longitude, photo_path, address)
    return jsonify({"ticket_id": ticket_id}), 201

@app.route("/problems", methods=["GET"])
def list_problems():
    category_id = request.args.get("category_id", type=int)
    status_id = request.args.get("status_id", type=int)
    order_by = request.args.get("order_by", default="created_at")
    return jsonify(db.get_problems(category_id=category_id, status_id=status_id, order_by=order_by))

@app.route("/problems/<ticket_id>", methods=["GET"])
def get_problem(ticket_id):
    problem = db.get_problem_by_ticket(ticket_id)
    if problem is None:
        return jsonify({"error": "Problem not found"}), 404
    return jsonify(problem)

@app.route("/problems/<ticket_id>", methods=["PATCH"])
def update_problem(ticket_id):
    problem = db.get_problem_by_ticket(ticket_id)
    if problem is None:
        return jsonify({"error": "Problem not found"}), 404
    data = request.get_json()
    new_description = data.get("description")
    if not new_description:
        return jsonify({"error": "description is required"}), 400
    updated = db.update_problem_description(ticket_id, new_description)
    if updated:
        return jsonify({"message": f"Problem {ticket_id} updated successfully"})
    return jsonify({"error": "Update failed"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)

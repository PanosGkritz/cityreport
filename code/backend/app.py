"""
REST API του συστήματος CityReport.
Εξυπηρετεί τους πολίτες για αναφορά και διαχείριση προβλημάτων της πόλης.
Δεν απαιτείται authentication (σύμφωνα με την εκφώνηση).
"""

from flask import Flask, jsonify, request
import db

app = Flask(__name__)


@app.route("/")
def home():
    """Βασικό endpoint για να ελέγξουμε ότι το API τρέχει."""
    return jsonify({"message": "CityReport API is running"})


@app.route("/categories", methods=["GET"])
def get_categories():
    """Επιστρέφει όλες τις διαθέσιμες κατηγορίες προβλημάτων."""
    categories = db.get_categories()
    return jsonify(categories)


@app.route("/statuses", methods=["GET"])
def get_statuses():
    """Επιστρέφει όλες τις διαθέσιμες καταστάσεις προβλημάτων."""
    statuses = db.get_statuses()
    return jsonify(statuses)



@app.route("/problems", methods=["POST"])
def create_problem():
    """Δημιουργεί νέα αναφορά προβλήματος. Επιστρέφει το ticket_id."""
    data = request.get_json()

    title = data.get("title")
    description = data.get("description")
    category_id = data.get("category_id")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if not title or not category_id:
        return jsonify({"error": "title and category_id are required"}), 400

    ticket_id = db.insert_problem(title, description, category_id, latitude, longitude)
    return jsonify({"ticket_id": ticket_id}), 201


if __name__ == "__main__":
    app.run(debug=True, port=5000)

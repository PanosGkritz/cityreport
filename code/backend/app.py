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



@app.route("/problems", methods=["GET"])
def list_problems():
    """
    Επιστρέφει λίστα προβλημάτων με δυνατότητα φιλτραρίσματος
    μέσω query parameters: ?category_id=1&status_id=2&order_by=title
    """
    category_id = request.args.get("category_id", type=int)
    status_id = request.args.get("status_id", type=int)
    order_by = request.args.get("order_by", default="created_at")

    problems = db.get_problems(category_id=category_id, status_id=status_id, order_by=order_by)
    return jsonify(problems)



@app.route("/problems/<ticket_id>", methods=["GET"])
def get_problem(ticket_id):
    """Επιστρέφει τα στοιχεία ενός προβλήματος με βάση το ticket_id."""
    problem = db.get_problem_by_ticket(ticket_id)

    if problem is None:
        return jsonify({"error": "Problem not found"}), 404

    return jsonify(problem)


if __name__ == "__main__":
    app.run(debug=True, port=5000)

"""
Συναρτήσεις για επικοινωνία με τη βάση δεδομένων.
Χρησιμοποιούνται τόσο από το REST API (Flask) όσο και από
το Admin Dashboard (Streamlit), ώστε να μην επαναλαμβάνεται κώδικας.
"""

import sqlite3
import os
import uuid
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "cityreport.db")


def get_connection():
    """Ανοίγει σύνδεση με τη βάση δεδομένων SQLite."""
    conn = sqlite3.connect(DB_PATH)
    # Έτσι τα αποτελέσματα έρχονται σαν dictionary-like rows
    conn.row_factory = sqlite3.Row
    return conn


def get_categories():
    """Επιστρέφει όλες τις κατηγορίες προβλημάτων."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM categories ORDER BY id").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_statuses():
    """Επιστρέφει όλες τις πιθανές καταστάσεις προβλημάτων."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM statuses ORDER BY id").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def insert_problem(title, description, category_id, latitude, longitude, photo_path=None, address=None):
    """
    Καταχωρεί νέο πρόβλημα στη βάση.
    Επιστρέφει το ticket_id που δημιουργήθηκε.
    """
    ticket_id = str(uuid.uuid4())[:8]  # σύντομο μοναδικό αναγνωριστικό
    created_at = datetime.now().isoformat()

    conn = get_connection()
    conn.execute(
        """
        INSERT INTO problems (
            ticket_id, title, description, category_id, status_id,
            latitude, longitude, address, photo_path, created_at
        ) VALUES (?, ?, ?, ?, 1, ?, ?, ?, ?, ?)
        """,
        (ticket_id, title, description, category_id, latitude, longitude, address, photo_path, created_at)
    )
    # status_id = 1 -> "Αναφέρθηκε" (αρχική κατάσταση κάθε νέου προβλήματος)
    conn.commit()
    conn.close()

    return ticket_id


def get_problem_by_ticket(ticket_id):
    """Επιστρέφει τα στοιχεία ενός προβλήματος με βάση το ticket_id, ή None αν δεν υπάρχει."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM problems WHERE ticket_id = ?", (ticket_id,)
    ).fetchone()
    conn.close()

    if row is None:
        return None
    return dict(row)


def get_problems(category_id=None, status_id=None, order_by="created_at"):
    """
    Επιστρέφει λίστα προβλημάτων, με δυνατότητα φιλτραρίσματος
    ανά κατηγορία και/ή κατάσταση, και ταξινόμησης.
    """
    query = "SELECT * FROM problems WHERE 1=1"
    params = []

    if category_id is not None:
        query += " AND category_id = ?"
        params.append(category_id)

    if status_id is not None:
        query += " AND status_id = ?"
        params.append(status_id)

    # Επιτρέπουμε ταξινόμηση μόνο σε συγκεκριμένες στήλες για ασφάλεια
    allowed_order_columns = ["created_at", "title", "category_id", "status_id"]
    if order_by not in allowed_order_columns:
        order_by = "created_at"

    query += f" ORDER BY {order_by} DESC"

    conn = get_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()

    return [dict(row) for row in rows]


def update_problem_description(ticket_id, new_description):
    """Ο πολίτης ενημερώνει την περιγραφή ενός υπάρχοντος προβλήματος."""
    conn = get_connection()
    cursor = conn.execute(
        "UPDATE problems SET description = ?, updated_at = ? WHERE ticket_id = ?",
        (new_description, datetime.now().isoformat(), ticket_id)
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def update_problem_status(ticket_id, new_status_id, admin_comment=None):
    """Ο διαχειριστής αλλάζει την κατάσταση ενός προβλήματος (μέσω Streamlit)."""
    conn = get_connection()

    resolved_at = None
    # Αν η νέα κατάσταση είναι "Επιλύθηκε" (id=3), καταγράφουμε την ημερομηνία επίλυσης
    if new_status_id == 3:
        resolved_at = datetime.now().isoformat()

    conn.execute(
        """
        UPDATE problems
        SET status_id = ?, admin_comment = ?, updated_at = ?, resolved_at = ?
        WHERE ticket_id = ?
        """,
        (new_status_id, admin_comment, datetime.now().isoformat(), resolved_at, ticket_id)
    )
    conn.commit()
    conn.close()

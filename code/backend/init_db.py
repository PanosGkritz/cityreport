"""
Script αρχικοποίησης της βάσης δεδομένων CityReport.
Διαβάζει το schema από db/schema.sql, δημιουργεί τους πίνακες
και εισάγει τις αρχικές κατηγορίες και καταστάσεις.
Εκτέλεση: python init_db.py
"""

import sqlite3
import os

# Path προς το αρχείο βάσης δεδομένων (δημιουργείται στο code/backend/)
DB_PATH = os.path.join(os.path.dirname(__file__), "cityreport.db")

# Path προς το schema.sql (βρίσκεται στον φάκελο db/ στη ρίζα του project)
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "db", "schema.sql")

# Αρχικές κατηγορίες προβλημάτων
CATEGORIES = [
    "Οδοποιία",
    "Ηλεκτροφωτισμός",
    "Καθαριότητα",
    "Ύδρευση",
    "Πράσινο",
    "Εγκαταλελειμμένα Οχήματα",
    "Βλάβες Δημόσιων Υποδομών"
]

# Αρχικές καταστάσεις επίλυσης
STATUSES = [
    "Αναφέρθηκε",
    "Σε εξέλιξη",
    "Επιλύθηκε",
    "Απορρίφθηκε"
]


def init_db():
    # Σύνδεση με τη βάση (δημιουργείται το αρχείο αν δεν υπάρχει)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Εκτέλεση του schema.sql για δημιουργία πινάκων
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)

    # Εισαγωγή αρχικών κατηγοριών (αν δεν υπάρχουν ήδη)
    for category in CATEGORIES:
        cursor.execute(
            "INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,)
        )

    # Εισαγωγή αρχικών καταστάσεων (αν δεν υπάρχουν ήδη)
    for status in STATUSES:
        cursor.execute(
            "INSERT OR IGNORE INTO statuses (name) VALUES (?)", (status,)
        )

    conn.commit()
    conn.close()
    print(f"Database initialized at: {DB_PATH}")


if __name__ == "__main__":
    init_db()

"""
Script για την εισαγωγή εικονικών δεδομένων στη βάση.
Στέλνει 25 POST requests στο REST API για να γεμίσει η βάση
με δεδομένα διαφορετικών κατηγοριών, περιοχών και καταστάσεων.
Εκτέλεση: python seed_data.py (ο Flask server πρέπει να τρέχει)
"""
import requests
import sqlite3
import os
from datetime import datetime, timedelta
import random

API_URL = "http://127.0.0.1:5000"
DB_PATH = os.path.join(os.path.dirname(__file__), "cityreport.db")

problems = [
    {"title": "Λακκουβα στην οδο Πανεπιστημιου", "description": "Μεγαλη λακκουβα κοντα στη σταση λεωφορειου", "category_id": 1, "latitude": 37.9838, "longitude": 23.7275},
    {"title": "Χαλασμενο φαναρι στην πλατεια", "description": "Το φαναρι δεν λειτουργει εδω και 3 μερες", "category_id": 2, "latitude": 37.9755, "longitude": 23.7348},
    {"title": "Σκουπιδια στο πεζοδρομιο", "description": "Σωρος σκουπιδια που δεν εχουν μαζευτει", "category_id": 3, "latitude": 37.9801, "longitude": 23.7219},
    {"title": "Διαρροη νερου στην οδο Σταδιου", "description": "Τρεχει νερο απο τον δρομο εδω και μια εβδομαδα", "category_id": 4, "latitude": 37.9776, "longitude": 23.7341},
    {"title": "Καταστραμμενο παγκακι στο παρκο", "description": "Σπασμενο παγκακι που ειναι επικινδυνο", "category_id": 5, "latitude": 37.9812, "longitude": 23.7298},
    {"title": "Εγκαταλελειμμενο αυτοκινητο", "description": "Παλιο αυτοκινητο χωρις πινακιδες εδω και μηνες", "category_id": 6, "latitude": 37.9743, "longitude": 23.7412},
    {"title": "Χαλασμενη πεζοδιαβαση", "description": "Σπασμενες πλακες στην πεζοδιαβαση", "category_id": 7, "latitude": 37.9867, "longitude": 23.7187},
    {"title": "Κοιλωμα στην ασφαλτο", "description": "Μεγαλο κοιλωμα που προκαλει ζημιες στα οχηματα", "category_id": 1, "latitude": 37.9821, "longitude": 23.7356},
    {"title": "Καμενος λαμπτηρας στην οδο Αθηνας", "description": "Σκοταδι στον δρομο τις νυχτερινες ωρες", "category_id": 2, "latitude": 37.9794, "longitude": 23.7263},
    {"title": "Παρανομη χωματερη", "description": "Καποιοι πεταουν μπαζα σε κενο οικοπεδο", "category_id": 3, "latitude": 37.9758, "longitude": 23.7389},
    {"title": "Βλαβη στο δικτυο υδρευσης", "description": "Χαμηλη πιεση νερου σε ολη τη γειτονια", "category_id": 4, "latitude": 37.9833, "longitude": 23.7301},
    {"title": "Χαλασμενο συντριβανι", "description": "Το συντριβανι της πλατειας δεν λειτουργει", "category_id": 5, "latitude": 37.9769, "longitude": 23.7445},
    {"title": "Εγκαταλελειμμενη μοτοσικλετα", "description": "Μοτοσικλετα παρκαρισμενη εδω και 2 μηνες", "category_id": 6, "latitude": 37.9845, "longitude": 23.7234},
    {"title": "Σπασμενο καπακι φρεατιου", "description": "Επικινδυνο ανοιχτο φρεατιο στο πεζοδρομιο", "category_id": 7, "latitude": 37.9778, "longitude": 23.7367},
    {"title": "Χαλασμενη ασφαλτος στη γωνια", "description": "Μεγαλη τρυπα στο οδοστρωμα μετα τις βροχες", "category_id": 1, "latitude": 37.9856, "longitude": 23.7312},
    {"title": "Σβηστα φαναρια σε διασταυρωση", "description": "Επικινδυνη διασταυρωση χωρις φωτισμο", "category_id": 2, "latitude": 37.9723, "longitude": 23.7423},
    {"title": "Κοντεινερ γεματο σκουπιδια", "description": "Ξεχειλιζει ο κοντεινερ εδω και μια εβδομαδα", "category_id": 3, "latitude": 37.9812, "longitude": 23.7278},
    {"title": "Σπασμενος αγωγος", "description": "Νερο τρεχει και δημιουργει λιμνη στον δρομο", "category_id": 4, "latitude": 37.9789, "longitude": 23.7334},
    {"title": "Ξερα δεντρα στο αλσος", "description": "Κινδυνος πτωσης κλαδιων σε περιπατητες", "category_id": 5, "latitude": 37.9834, "longitude": 23.7289},
    {"title": "Εγκαταλελειμμενο φορτηγο", "description": "Μεγαλο φορτηγο μπλοκαρει τον δρομο", "category_id": 6, "latitude": 37.9761, "longitude": 23.7401},
    {"title": "Χαλασμενο κιγκλιδωμα", "description": "Σπασμενη προστατευτικη μπαριερα στη γεφυρα", "category_id": 7, "latitude": 37.9847, "longitude": 23.7256},
    {"title": "Βαθουλωμα στην εισοδο σχολειου", "description": "Επικινδυνο για παιδια και γονεις", "category_id": 1, "latitude": 37.9803, "longitude": 23.7378},
    {"title": "Χαλασμενος προβολεας παρκου", "description": "Σκοταδι στο παρκο τις βραδινες ωρες", "category_id": 2, "latitude": 37.9772, "longitude": 23.7445},
    {"title": "Παρανομη αποθεση μπαζων", "description": "Μπαζα απο ανακαινιση στο πεζοδρομιο", "category_id": 3, "latitude": 37.9829, "longitude": 23.7267},
    {"title": "Βλαβη σε αντλια νερου", "description": "Η αντλια της περιοχης εχει χαλασει", "category_id": 4, "latitude": 37.9756, "longitude": 23.7389},
]

statuses = [1, 1, 2, 2, 3, 3, 4, 1, 2, 3, 1, 2, 3, 4, 1, 2, 1, 3, 2, 1, 4, 2, 1, 3, 2]

def seed():
    print("Αρχη εισαγωγης δεδομενων...")
    ticket_ids = []

    for i, problem in enumerate(problems):
        response = requests.post(
            f"{API_URL}/problems",
            data={
                "title": problem["title"],
                "description": problem["description"],
                "category_id": problem["category_id"],
                "latitude": problem["latitude"],
                "longitude": problem["longitude"]
            }
        )
        if response.status_code == 201:
            ticket_id = response.json()["ticket_id"]
            ticket_ids.append(ticket_id)
            print(f"[{i+1}/25] Δημιουργηθηκε: {ticket_id} - {problem['title'][:40]}")
        else:
            print(f"[{i+1}/25] Αποτυχια: {response.text}")

    print("\nΕνημερωση καταστασεων...")
    conn = sqlite3.connect(DB_PATH)

    for i, ticket_id in enumerate(ticket_ids):
        status_id = statuses[i]
        resolved_at = None
        if status_id == 3:
            resolved_at = (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
        
        conn.execute(
            "UPDATE problems SET status_id = ?, resolved_at = ? WHERE ticket_id = ?",
            (status_id, resolved_at, ticket_id)
        )

    conn.commit()
    conn.close()
    print("Ολοκληρωση! 25 προβληματα εισηχθησαν επιτυχως.")

if __name__ == "__main__":
    seed()

"""
Συναρτήσεις για κλήσεις σε εξωτερικά REST APIs.
Αυτή τη στιγμή περιλαμβάνει το Nominatim geocoding API
για μετατροπή συντεταγμένων σε διεύθυνση.
"""
import requests

def get_address_from_coordinates(latitude, longitude):
    """
    Καλεί το OpenStreetMap Nominatim API για να μετατρέψει
    συντεταγμένες (latitude, longitude) σε διεύθυνση.
    Επιστρέφει τη διεύθυνση ως string, ή None αν αποτύχει.
    """
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": latitude,
        "lon": longitude,
        "format": "json"
    }
    headers = {
        "User-Agent": "CityReport/1.0"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("display_name", None)
    except requests.exceptions.RequestException:
        pass

    return None

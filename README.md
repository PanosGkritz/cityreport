# CityReport

City problem reporting and management system.
Developed for the MSc Information Systems & Services course.

## Setup and Installation

### 1. Clone the repository
git clone https://github.com/PanosGkritz/cityreport.git
cd cityreport

### 2. Create virtual environment

Windows:
python -m venv venv
source venv/Scripts/activate

Linux/Mac:
python3 -m venv venv
source venv/bin/activate

### 3. Install dependencies
pip install -r code/backend/requirements.txt

### 4. Initialize the database
python code/backend/init_db.py

### 5. Start the Flask server
cd code/backend
python app.py

Server runs at http://127.0.0.1:5000

### 6. Insert sample data (optional)
cd code/backend
python seed_data.py

## API Endpoints

GET    /                        Health check
GET    /categories              List categories
GET    /statuses                List statuses
POST   /problems                Submit new problem report
GET    /problems                List problems with filters
GET    /problems/<ticket_id>    Get problem details
PATCH  /problems/<ticket_id>    Update problem description

## Filter parameters for GET /problems

category_id: filter by category
status_id: filter by status
order_by: sort results (created_at, title, category_id, status_id)

Example: GET /problems?category_id=1&order_by=title

## Postman Collection

Import postman/CityReport API.postman_collection.json into Postman.

## Libraries

- Flask 3.1.3
- SQLite3
- Requests
- Nominatim OpenStreetMap geocoding

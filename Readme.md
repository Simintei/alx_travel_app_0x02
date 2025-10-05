# alx_travel_app_0x01

A Django-based travel booking application, duplicate of `alx_travel_app` for experimentation and learning purposes.

## Features
- User authentication and management
- CRUD operations for Listings, Bookings, and Reviews
- REST API endpoints for interacting with data
- Swagger API documentation at `/swagger/`

## Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/Simintei/alx_travel_app
   cd alx_travel_app_0x01
Create and activate a virtual environment:

python3 -m venv venv
source venv/bin/activate


Install dependencies:

pip install -r requirements.txt


Run migrations:

python manage.py makemigrations
python manage.py migrate


Run the development server:

python manage.py runserver

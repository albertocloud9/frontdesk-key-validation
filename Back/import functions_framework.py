import functions_framework
from pyairtable import Table
import os
import json
from google.auth import jwt
from datetime import datetime

# Airtable configuration
AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_NAME = os.environ.get('AIRTABLE_TABLE_NAME')

# Initialize Airtable table
table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)

def authenticate_request(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise ValueError('No Authorization header provided')
    
    parts = auth_header.split()
    if parts[0].lower() != 'bearer':
        raise ValueError('Authorization header must start with Bearer')
    elif len(parts) == 1:
        raise ValueError('Token not found')
    elif len(parts) > 2:
        raise ValueError('Authorization header must be Bearer token')
    
    token = parts[1]
    try:
        # Verify and decode the JWT token
        decoded_token = jwt.decode(token, audience='your-audience')
        # You can add more checks here, e.g., checking specific claims
        return decoded_token
    except Exception as e:
        raise ValueError(f'Invalid token: {str(e)}')

@functions_framework.http
def check_room(request):
    # Set CORS headers for the preflight request
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    try:
        # Authenticate the request
        authenticate_request(request)
    except ValueError as auth_error:
        return (json.dumps({"error": str(auth_error)}), 401, headers)

    # Parse the request body
    request_json = request.get_json(silent=True)
    
    if not request_json or 'room_number' not in request_json:
        return (json.dumps({"error": "Room number is required"}), 400, headers)
    
    room_number = request_json['room_number']
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Search for the room in Airtable with today's check-in
    formula = f"AND({{Unit(s)}} = '{room_number}', {{Check In}} = '{today}')"
    records = table.all(formula=formula)
    
    # Check if any records were found
    exists = len(records) > 0
    
    response = {
        "exists": "Yes" if exists else "No",
        "records": [record['fields'] for record in records] if exists else []
    }
    
    return (json.dumps(response), 200, headers)
import functions_framework
from pyairtable import Table
import os
import json
from google.auth import jwt

# Airtable configuration
AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
# AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')
AIRTABLE_BASE_ID = 'appWI25CjKMkmxK6N'
# AIRTABLE_TABLE_NAME = os.environ.get('AIRTABLE_TABLE_NAME')
AIRTABLE_TABLE_NAME = 'Reservations'

# Initialize Airtable table
table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)



class RequestValidator:
    def __init__(self, request_json, request_args):
        self.request_json = request_json
        self.request_args = request_args

    def get_value(self, key):
        return self.request_json.get(key) or self.request_args.get(key)

    def validate_required_fields(self, *required_fields):
        missing_fields = [field for field in required_fields if not self.get_value(field)]
        if missing_fields:
            return False, f"Missing fields: {', '.join(missing_fields)}"
        return True, None


class CORSHandler:
    @staticmethod
    def handle_preflight():
        # CORS preflight response
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    @staticmethod
    def set_cors_headers():
        # Set CORS headers for the main request
        return {'Access-Control-Allow-Origin': '*'}


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


def handle_request(request, request_json, request_args):
    # Handle CORS preflight request
    if request.method == 'OPTIONS':
        return False , CORSHandler.handle_preflight()

    # Set CORS headers for the main request
    headers = CORSHandler.set_cors_headers()

    # Validate required fields using RequestValidator
    validator = RequestValidator(request_json, request_args)
    
    # Validate room_number and building fields
    is_valid, error_message = validator.validate_required_fields('room_number', 'building')
    
    if not is_valid:
        print(f"Validation failed: {error_message}")
        return is_valid, (json.dumps({"error": error_message}), 400, headers), headers

    # Extract validated values
    room_number = validator.get_value('room_number')
    building = validator.get_value('building')

    # Continue processing with room_number and building
    print(f"Validated request with room_number: {room_number} and listing_id: {building}")
    return is_valid , (room_number , building) , headers


@functions_framework.http
def check_room(request):
    print('heyyyy, starting')

    try:
        # Authenticate the request
        # authenticate_request(request)
        print('proximily authentication')
    except ValueError as auth_error:
        return (json.dumps({"error": str(auth_error)}), 401, headers)

    # Parse the request body
    request_json = request.get_json(silent=True)
    request_args = request.args

    is_valid ,  data_or_error , headers  = handle_request(request, request_json, request_args)
    
    if not is_valid:
        return data_or_error 

    room_number , building = data_or_error
    
    # Search for the room in Airtable with today's check-in
    formula = f"AND( FIND('{room_number}',{{Unit(s)}}) != 0, {{Building}} = '{building}',  {{Check In}} = TODAY() , FIND('anceled' , {{Reservation Status}}) = 0 )"

    records = table.all(formula=formula)
    
    # Check if any records were found
    exists = len(records) > 0
    
    response = {
        "exists": "Yes" if exists else "No",
        "records": [record['fields'] for record in records] if exists else []
    }
    return (json.dumps(response), 200, headers)
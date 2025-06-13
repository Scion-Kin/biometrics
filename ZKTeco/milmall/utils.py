import requests
from datetime import datetime, timedelta
from milmall.config import api_url, client_id, client_secret, username, password
from milmall.exceptions import AuthenticationError, NetworkError, TokenRefreshError, LoginError
from db import db
from logger import logger

default_headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'User-Agent': 'Mozilla/5.0 (compatible; MilMallBot/1.0; +https://milmall.rw/bot)'
}

def login_to_milmall() -> dict:
    """
    Logs in to the MilMall API and returns the access token.
    
    :param username: The username for MilMall API
    :param password: The password for MilMall API
    :param client_secret: The client secret for MilMall API
    :param client_id: The client ID for MilMall API
    :return: Access token if login is successful, None otherwise (stores the bearer token in JSON file, with its expiry time)
    """
    url = f"{api_url}/oauth/token"
    payload = {
        "grant_type": "password",
        "client_id": client_id,
        "client_secret": client_secret,
        "username": username,
        "password": password
    }

    response = requests.post(url, json=payload, headers=default_headers)

    if response.status_code == 200:
        client = db.get_db('auth')
        if client is None:
            raise NetworkError("Database connection failed. Cannot store authentication data.")

        storage_data = {}
        storage_data['access_token'] = response.json().get('access_token')
        storage_data['expires_in'] = timedelta(seconds=response.json().get('expires_in') - 3600) + datetime.now()
        storage_data['token_type'] = response.json().get('token_type', 'Bearer')
        storage_data['refresh_token'] = response.json().get('refresh_token', None)

        result = client.insert_one(storage_data)
        if result.acknowledged:
            logger.log("Login successful. Access token stored in database.", 'SUCCESS')
            return storage_data
        else:
            raise NetworkError("Failed to store authentication data in the database.")

    else:
        raise LoginError(f"Login failed: {response.status_code} - {response.text}")


def refresh_token() -> dict:
    """
    Refreshes the access token using the refresh token.
    
    :param client_id: The client ID for MilMall API
    :param client_secret: The client secret for MilMall API
    :return: New access token if refresh is successful, None otherwise
    """
    client = db.get_db('auth')
    if client is None:
        raise NetworkError("Database connection failed. Cannot refresh token.")

    storage_data = client.find_one({})

    if not storage_data or 'refresh_token' not in storage_data:
        raise AuthenticationError("Refresh token is missing. Please login again.")

    refresh_token = storage_data.get('refresh_token')

    url = f"{api_url}/oauth/token"
    payload = {
        'grant_type': 'refresh_token',
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token
    }

    response = requests.post(url, data=payload, headers=default_headers)

    if response.status_code == 200:
        response = response.json()
        storage_data['access_token'] = response.get('access_token')
        storage_data['expires_in'] = timedelta(seconds=response.get('expires_in') - 3600) + datetime.now()
        storage_data['token_type'] = response.get('token_type', 'Bearer')
        storage_data['refresh_token'] = response.get('refresh_token', None)
        
        result = client.update_one({ storage_data['_id'] }, { '$set': storage_data })
        if result.modified_count > 0:
            logger.log("Token refreshed successfully. New access token stored in database.", 'SUCCESS')
            return storage_data
        else:
            raise TokenRefreshError("Failed to update access token in the database.")

    else:
        raise TokenRefreshError(f"Token refresh failed: {response.status_code} - {response.text}")


def try_auth() -> dict:
    """
    Attempts to authenticate with the MilMall API and returns the authentication data.

    :return: A dictionary containing authentication data
    """
    try:
        return refresh_token()
    except (AuthenticationError, TokenRefreshError) as e:
        logger.log(f"Authentication error: {e}", 'ERROR')
        logger.log("Attempting to login to MilMall...", 'INFO')
        return login_to_milmall()
    

def load_storage() -> dict:
    """
    Loads the storage data from the JSON file.
    
    :return: Storage data as a dictionary
    """

    try:
        client = db.get_db('auth')
        if client is None:
            raise NetworkError("Database connection failed. Cannot load storage data.")

        storage_data = client.find_one({})
        if storage_data:
            if 'expires_in' in storage_data and datetime.now() >= storage_data['expires_in']:
                logger.log("Access token has expired. Refreshing token...", 'INFO')
                storage_data = try_auth()

            return storage_data
        else:
            return try_auth()

    except Exception as e:
        logger.log(f"Error loading storage data: {e}", 'ERROR')
        return {}


def format_data(data: dict={}, reverse: bool=False, keeps: list=None) -> dict:
    """
    Formats the data to match the MilMall API requirements.

    :param data: The data to be formatted
    :param reverse: If True, reverses the formatting (from MilMall to Attendance Algorithm API format)
    :param keeps: List of required fields to keep in the formatted data
    :return dict: Formatted data as a dictionary
    """

    expects = [ "employee", "employee_name", "attendance_date", "company", "check_in", "check_out", "status", "attendance_device_id", "default_shift", "device" ]
    answers = [ "id", "first_name+last_name", "date", "business_id", "clock_in_time", "clock_out_time", "status", "user_id", "essentials_shift_id", "ip_address" ]

    formatted_data = {}
    query = expects if not reverse else answers
    reply = answers if not reverse else expects

    for key in query:
        if key in data:
            if '+' not in reply[query.index(key)]:
                formatted_data[reply[query.index(key)]] = data[key]
            else:
                keys = reply[query.index(key)].split('+')
                values = data.get(key, '').strip().split(' ')
                if len(values) == len(keys):
                    formatted_data[keys[0]], formatted_data[keys[1]] = values[0], values[1]

        else:
            keys = key.split('+')
            if len(keys) > 1:
                vals = [data.get(k, '') for k in keys]
                vals = [v for v in vals if v is not None]

                formatted_data[reply[query.index(key)]] = ' '.join(vals).strip() if all(vals) else None
                if not formatted_data[reply[query.index(key)]]: del formatted_data[reply[query.index(key)]]

        if key in data: del data[key]

    res = {**data, **formatted_data}

    return {k: res[k] for k in keeps if k in res} if keeps else res

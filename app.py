"""Main application code"""
import os
from functools import wraps
from flask import Flask, request, make_response
from flask_apscheduler import APScheduler
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
import requests
import db.database as db
# from db.database import init_app, add_product, update_product, delete_product,\
#     add_offers, get_all_products, get_offers_by_id, get_all_offers,\
#     update_offers, get_product_by_id

app = Flask(__name__)
db.init_app(app)
load_dotenv()

# Load the environment variables from the .env file
REFRESH_TOKEN = os.environ['REFRESH_TOKEN']
OFFERS_URL = os.environ['OFFERS_URL']
API_TOKEN = os.environ['API_TOKEN']

app.config['ACCESS_TOKEN'] = None

REQUEST_TIMEOUT = 10
SCHEDULER_INTERVAL = 60  # How often to update offers database in seconds


# Load latest ACCESS_TOKEN from previous session
with open("token", "r", encoding="utf-8") as token_file:
    token = token_file.readline()
    if token:
        with app.app_context():
            app.config['ACCESS_TOKEN'] = token


@app.before_request
def check_api_token():
    """Check if API token is valid"""
    api_token = request.headers.get("Token")
    if not api_token or api_token != API_TOKEN:
        return make_response({'message': 'Token missing or incorrect'}), 401


def update_access_token(func):
    """Check if access token is valid and update it if needed and possible"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        response = get_access_token()
        if response.status_code == 201:
            access_token = response.json()["access_token"]
            app.config['ACCESS_TOKEN'] = access_token
            app.logger.debug(app.config['ACCESS_TOKEN'])
            # Save current token to the cache file to use it between the sessions
            # To avoid "Cannot generate access token because another is valid" condition
            with open("token", "w", encoding="utf-8") as file:
                file.write(access_token)
        return func(*args, **kwargs)
    return wrapper


def update_all_offers():
    """Call offers update for all products in database"""
    with app.app_context():
        app.logger.debug("Updating offers...")
        products = db.get_all_products()
        for product in products:
            update_offers_for_product(product["id"])


def update_offers_for_product(product_id):
    """Update all offers in database for given product_id using Offers microservice"""
    response = get_latest_offers(product_id)
    if response.status_code == 200:
        db.update_offers(response.json())


# --- Offers microservice endpoints ---
def get_access_token():
    """Get a new token if the old one is expired"""
    url = f"{OFFERS_URL}/api/v1/auth"
    return requests.post(url=url, headers={'Bearer': REFRESH_TOKEN}, timeout=REQUEST_TIMEOUT)


@update_access_token
def register_product(product_json):
    """Register a new product to the Offers microservice and save it to database"""
    url = f'{OFFERS_URL}/api/v1/products/register'
    response = requests.post(url=url, headers={'Bearer': app.config['ACCESS_TOKEN']}, json=product_json,
                             timeout=REQUEST_TIMEOUT)
    return response


@update_access_token
def get_latest_offers(product_id):
    """Get latest offers from the Offers microservice of product with given product_id and save them to database"""
    url = f"{OFFERS_URL}/api/v1/products/{product_id}/offers"
    response = requests.get(url=url, headers={'Bearer': app.config['ACCESS_TOKEN']}, timeout=REQUEST_TIMEOUT)
    return response
# --- Offers microservice endpoints end ---


@app.post('/api/refresh_access_token')
def refresh_access_token():
    """Refresh access token for the Offers microservice"""
    acces_token = update_access_token()
    if acces_token:
        return make_response({'access_token': acces_token}), 201
    return make_response({'message': 'Cannot refresh access token'}), 409


def add_new_product(product_json):
    """Complete process of adding new product"""
    # Register new product to Offer microservice
    response = register_product(product_json)
    if response.status_code == 201:
        # If success, add product to database
        db.add_product(product_json=product_json)

        # Get latest offers for the product from Offer microservice
        response = get_latest_offers(product_json["id"])
        if response.status_code == 200:
            # If success, add offers to database
            db.add_offers(response=response, product_id=product_json["id"])
    return response


@app.route('/api/products', methods=['GET', 'POST', 'PATCH', 'DELETE'])
@app.get('/api/products/<string:product_id>')
def product_handler(product_id=None):
    """Handler for products requests"""
    method = request.method
    # POST - Add new product
    if method == "POST":
        try:
            response = add_new_product(request.get_json())
            return make_response(response.text), response.status_code
        except IntegrityError:
            return make_response({'message': 'Product already exists'}), 409

    if method == "PATCH" or method == "DELETE":
        json_product_id = request.json.get('id')
        if not json_product_id:
            return make_response({'message': 'Missing product ID'}), 409
        response = ""

        # PATCH - Update an existing product
        if method == "PATCH":
            response = db.update_product(
                product_id=json_product_id,
                new_name=request.json.get('name'),
                new_description=request.json.get('description'))

        # DELETE - Delete an existing product
        elif method == "DELETE":
            response = db.delete_product(product_id=json_product_id)

        if response is False:
            return make_response({'message': 'Product not found'}), 404
        return make_response(), 204

    # GET - Get product by ID
    if product_id:
        product = db.get_product_by_id(product_id)
        if product is None:
            return make_response({'message': 'Product not found'}), 404
        return make_response(product.to_dict()), 200

    # GET - Get all products
    return make_response(db.get_all_products()), 200


@app.get('/api/offers')
@app.get('/api/offers/<string:product_id>')
def offers_handler(product_id=None):
    """Handler for offers requests"""
    if product_id:
        offers = db.get_offers_by_id(product_id=product_id)
        if offers is None:
            return make_response({'message': 'Product not found'}), 404
    else:
        offers = db.get_all_offers()
    return make_response(offers), 200


# Run the scheduler, which will periodically call the update_all_offers function
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
INTERVAL_TASK_ID = 'update-all-offers'

scheduler.add_job(id=INTERVAL_TASK_ID,
                  func=update_all_offers,
                  trigger='interval',
                  seconds=SCHEDULER_INTERVAL)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', use_reloader=False)

# TODO Update readme

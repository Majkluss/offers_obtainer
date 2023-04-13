"""Main application code"""
import os
import sys
from flask import Flask, request, make_response
from flask_apscheduler import APScheduler
import requests
from sqlalchemy.exc import IntegrityError
from db.database import init_app, add_product, update_product, delete_product,\
    add_offers, get_all_products, get_offers, update_offers


app = Flask(__name__)
init_app(app)

# Load the environment variables from the .env file
# REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')
# OFFERS_URL = os.getenv('OFFERS_URL')
# API_TOKEN = os.getenv('API_TOKEN')

REFRESH_TOKEN = "ec209bf0-1212-47d5-be33-f06a2d995e63"
OFFERS_URL = "https://python.exercise.applifting.cz"
REQUEST_TIMEOUT = 10
SCHEDULER_INTERVAL = 60  # How often to update offers database


# Load latest ACCESS_TOKEN from previous session
with open("token", "r", encoding="utf-8") as token_file:
    os.environ['ACCESS_TOKEN'] = token_file.readline()


def update_token():
    """Get new token and save it"""
    response = get_access_token()
    if response.status_code == 201:
        access_token = response.json()["access_token"]
        app.logger.debug(access_token)
        os.environ['ACCESS_TOKEN'] = access_token

        # Save current token to the cache file to use it between the sessions
        # To avoid "Cannot generate access token because another is valid" condition
        with open("token", "w", encoding="utf-8") as file:
            file.write(access_token)
    return response


@app.post('/api/refresh_access_token')
def refresh_access_token():
    """Refresh access token for the Offers microservice"""
    response = update_token()
    return make_response(response.text), response.status_code


def get_access_token() -> requests.models.Response:
    """Get a new token if the old one is expired"""
    url = f"{OFFERS_URL}/api/v1/auth"
    return requests.post(url=url, headers={'Bearer': REFRESH_TOKEN}, timeout=REQUEST_TIMEOUT)


def register_product(product_json) -> requests.models.Response:
    """Register a new product to the Offers microservice and save it to database"""
    url = f'{OFFERS_URL}/api/v1/products/register'
    response = requests.post(url=url,
                             headers={'Bearer': os.environ['ACCESS_TOKEN']},
                             json=product_json,
                             timeout=REQUEST_TIMEOUT)
    if response.status_code == 401:
        refresh_access_token()
    return response


def get_latest_offers(product_id) -> requests.models.Response:
    """Get latest offers from the Offers microservice of product with given product_id and save them to database"""
    url = f"{OFFERS_URL}/api/v1/products/{product_id}/offers"
    response = requests.get(url=url,
                            headers={'Bearer': os.environ['ACCESS_TOKEN']},
                            timeout=REQUEST_TIMEOUT)

    if response.status_code == 401:
        refresh_access_token()
    return response


@app.route('/api/products', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def product_handler():
    """Handler for products requests"""
    method = request.method

    # POST - Add new product
    if method == "POST":
        product_json = request.get_json()

        # Register new product to Offer microservice
        response = register_product(product_json)

        if response.status_code == 201:
            # If success, add product to database
            add_product(product_json=product_json)

            # Get latest offers for the product from Offer microservice
            response = get_latest_offers(product_json["id"])
            if response.status_code == 200:
                # If success, add offers to database
                add_offers(response=response, product_id=product_json["id"])

        return make_response(response.text), response.status_code

    if method == "PATCH" or method == "DELETE":
        product_id = request.json.get('id')
        if not product_id:
            return make_response({'message': 'Missing product ID'}), 409

        response = False

        # PATCH - Update an existing product
        if method == "PATCH":
            response = update_product(
                product_id=product_id,
                new_name=request.json.get('name'),
                new_description=request.json.get('description'))

        # DELETE - Delete an existing product
        elif method == "DELETE":
            response = delete_product(product_id=product_id)

        if response is False:
            return make_response({'message': 'Product not found'}), 404

        return make_response(), 204

    # GET - Get all products
    return make_response(get_all_products()), 200


@app.get('/api/offers')
@app.get('/api/offers/<string:product_id>')
def offers_handler(product_id=None):
    """Handler for offers requests"""
    offers = get_offers(product_id=product_id)
    return make_response(offers), 200


@app.patch('/api/offers')
def offers_updater():
    """Handler for offers requests"""
    update_all_offers()
    return make_response(), 200


def update_all_offers():
    """Call offers update for all products in database"""
    with app.app_context():
        products = get_all_products()
        for product in products:
            update_offers_for_product(product["id"])


def update_offers_for_product(product_id) -> None:
    """Update all offers in database for given product_id using Offers microservice"""
    offers = get_latest_offers(product_id)
    if offers.status_code == 200:
        update_offers(offers.json())


# Run the scheduler, which will periodically call the update_all_offers function
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
INTERVAL_TASK_ID = 'update-all-offers'

scheduler.add_job(id=INTERVAL_TASK_ID,
                  func=update_all_offers,
                  trigger='interval',
                  seconds=SCHEDULER_INTERVAL)


if __name__ == '__main__':
    app.run(debug=True)

# TODO - dodělat testy
# TODO - dodělat check api tokenu pomocí app.before_request
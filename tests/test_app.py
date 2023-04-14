"""Tests for the Offers Obtainer application"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app
from db.database import add_product

# q: How Can i run these tests in docker?
# a: docker-compose -f docker-compose-test.yml up --build
# q: How should I configure it?
# a: docker-compose -f docker-compose-test.yml up --build   # run tests in docker
headers = {"Token": os.environ.get('API_TOKEN')}
print(headers)

SPICE_HARVESTER = {
    "id": "42424242-4242-4242-4242-424242424242",
    "name": "Test Spice Harvester",
    "description": "Spice Harvester obtains the Spice."
}

SAND_WORM_WITHOUT_ID = {
    "name": "Test Sand Worm",
    "description": "Sand Worm creates the Spice."
}

SAND_WORM_WRONG_ID = {
    "id": "42424242-4242-4242-4242-424242424243",
    "name": "Test Sand Worm",
    "description": "Sand Worm creates the Spice."
}

SAND_WORM = {
    "id": "42424242-4242-4242-4242-424242424242",
    "name": "Test Sand Worm",
    "description": "Sand Worm creates the Spice."
}


class TestsProducts:
    def test_get_product_without_token(self):
        with app.test_client() as client:
            response = client.get(f'/api/products')
            assert response.status_code == 401

    def test_create_product(self):
        with app.test_client() as client:
            with app.app_context():
                # Add product only to database, without register to Offer microservice
                add_product(SPICE_HARVESTER)
                response = client.get('/api/products', headers=headers)
                assert response.status_code == 200

    def test_get_product(self):
        with app.test_client() as client:
            response = client.get(f'/api/products/{SPICE_HARVESTER["id"]}', headers=headers)
            assert response.status_code == 200
            assert response.get_json() == SPICE_HARVESTER

    def test_update_product_missing_id(self):
        with app.test_client() as client:
            response = client.patch('/api/products', headers=headers, json=SAND_WORM_WITHOUT_ID)
            assert response.status_code == 409

    def test_update_product_wrong_id(self):
        with app.test_client() as client:
            response = client.patch('/api/products', headers=headers, json=SAND_WORM_WRONG_ID)
            assert response.status_code == 404

    def test_update_product(self):
        with app.test_client() as client:
            response = client.patch('/api/products', headers=headers, json=SAND_WORM)
            assert response.status_code == 204

    def test_get_updated_product(self):
        with app.test_client() as client:
            response = client.get(f'/api/products/{SPICE_HARVESTER["id"]}', headers=headers)
            assert response.status_code == 200
            assert response.get_json() == SAND_WORM

    def test_delete_product(self):
        with app.test_client() as client:
            response = client.delete('/api/products', headers=headers, json={"id": SPICE_HARVESTER["id"]})
            assert response.status_code == 204

    def test_get_deleted_product(self):
        with app.test_client() as client:
            response = client.get(f'/api/products/{SPICE_HARVESTER["id"]}', headers=headers)
            assert response.status_code == 404

"""Tests for the Offers Obtainer application"""
import os
from pytest import fixture
from app import app
from db.database import init_app

SPICE_HARVESTER = {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66af45",
    "name": "Spice Harvester",
    "description": "Spice Harvester obtains the Spice."
}

SAND_WORM = {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66af45",
    "name": "Sand Worm",
    "description": "Spice Harvester obtains the Spice."
}

# headers = {'Bearer': os.getenv('ACCESS_TOKEN')}
test_connection_string = "mysql+pymysql://root:root@localhost/testoffersdtb"
init_app(app=app, conn_string=test_connection_string)


class TestProducts:
    def test_get_products(self):
        with app.test_client() as client:
            response = client.get('/api/products')
            assert response.status_code == 200



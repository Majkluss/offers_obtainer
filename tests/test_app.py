"""Tests for the Offers Obtainer application"""
import os
import sys
from pytest import fixture
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
# init_app(app=app, conn_string=test_connection_string)
# init_app(test, test_connection_string)


# from sqlalchemy import create_engine
#
# def init_app(app, conn_string=connection_string):
#     """Init the database"""
#     app.config['SQLALCHEMY_DATABASE_URI'] = conn_string
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#     db.init_app(app)
#
#     engine = create_engine(conn_string)
#     with engine.connect() as conn:
#         conn.execute("CREATE DATABASE IF NOT EXISTS testoffersdtb")
#
#     with app.app_context():
#         db.create_all()



class TestProducts:
    def test_get_products(self):
        with app.test_client() as client:
            response = client.get('/api/products')
            assert response.status_code == 200



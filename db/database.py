"""Database handling"""
import os
from typing import Optional
from .models import db, Products, Offers
from dotenv import load_dotenv
from sqlalchemy_utils import create_database, database_exists
load_dotenv()

print(os.environ.get('MYSQL_USER'))

conn = "mysql+pymysql://{user}:{passwd}@{host}:{port}/{db}".format(
    user=os.environ.get('MYSQL_USER'),
    passwd=os.environ.get('MYSQL_PASSWORD'),
    host=os.environ.get('MYSQL_HOST'),
    port=int(os.environ.get('MYSQL_PORT')),
    db=os.environ.get('MYSQL_DATABASE'))


def init_app(app) -> None:
    app.config['SQLALCHEMY_DATABASE_URI'] = conn
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    if not database_exists(conn):
        create_database(conn)

    with app.app_context():
        db.create_all()


def add_product(product_json) -> None:
    """Add new product, defined by product_json to database"""
    product = Products(id=product_json['id'], name=product_json['name'], description=product_json['description'])
    db.session.add(product)
    db.session.commit()


def get_product_by_id(product_id) -> Optional[Products]:
    """Return product by product_id from database"""
    product = Products.query.filter_by(id=product_id).first()
    return product


def get_all_products() -> list:
    """Return list of all products from database"""
    products = Products.query.all()
    return [product.to_dict() for product in products]


def update_product(product_id, new_name=None, new_description=None) -> bool:
    """Update product with given id in database"""
    product = get_product_by_id(product_id)
    if product:
        if new_name:
            product.name = new_name
        if new_description:
            product.description = new_description
        db.session.commit()
    return bool(product)


def delete_product(product_id) -> bool:
    """Delete product with given id from database"""
    product = get_product_by_id(product_id)
    if product:
        db.session.query(Offers).filter_by(product_id=product_id).delete()
        db.session.delete(product)
        db.session.commit()
    return bool(product)


def add_offers(response, product_id) -> None:
    """Add new offers to database"""
    offers = response.json()
    for offer in offers:
        offer = Offers(id=offer['id'], price=offer['price'], items_in_stock=offer['items_in_stock'],
                       product_id=product_id)
        db.session.add(offer)
    db.session.commit()


def get_offers_by_id(product_id) -> Optional[list]:
    """Return product by product_id from database"""
    product = Products.query.filter_by(id=product_id).first()
    if not product:
        return None
    offers = Offers.query.filter_by(product_id=product_id).all()
    return [offer.to_dict() for offer in offers]


def get_all_offers() -> list:
    """Return list of all offers in database or all offers for product with given id"""
    offers = Offers.query.all()
    return [offer.to_dict() for offer in offers]


def update_offers(offers) -> None:
    """Update product with given id in database"""
    for offer_dict in offers:
        offer = Offers.query.get(offer_dict['id'])
        if offer:
            offer.price = offer_dict['price']
            offer.items_in_stock = offer_dict['items_in_stock']
    db.session.commit()

"""Database handling"""
import os
from typing import Optional
from .models import db, Products, Offers

# connection_string = "mysql+pymysql://{user}:{passwd}@{host}:{port}/{db}".format(
#     user=os.getenv('MYSQL_USER'),
#     passwd=os.getenv('MYSQL_PASSWORD'),
#     host=os.getenv('MYSQL_HOST'),
#     port=int(os.getenv('MYSQL_PORT')),
#     db=os.getenv('MYSQL_DATABASE'))

connection_string = "mysql+pymysql://root:root@localhost/offersdtb"


def init_app(app, conn_string=connection_string) -> None:
    """Init the database"""
    app.config['SQLALCHEMY_DATABASE_URI'] = conn_string
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

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


def get_offers(product_id=None) -> list:
    """Return list of all offers in database or all offers for product with given id"""
    if product_id:
        offers = Offers.query.filter_by(product_id=product_id).all()
    else:
        offers = Offers.query.all()

    return [offer.to_dict() for offer in offers]


def update_offers(offers) -> None:
    """Update product with given id in database"""
    for offer_dict in offers:
        offer = Offers.query.get(offer_dict['id'])
        offer.price = offer_dict['price']
        offer.items_in_stock = offer_dict['items_in_stock']
    db.session.commit()






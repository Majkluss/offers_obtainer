"""Database handling"""
import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# connection_string = "mysql+pymysql://{user}:{passwd}@{host}:{port}/{db}".format(
#     user=os.getenv('MYSQL_USER'),
#     passwd=os.getenv('MYSQL_PASSWORD'),
#     host=os.getenv('MYSQL_HOST'),
#     port=int(os.getenv('MYSQL_PORT')),
#     db=os.getenv('MYSQL_DATABASE'))

connection_string = "mysql+pymysql://root:root@localhost/offersdtb"


def init_app(app, conn_string=connection_string):
    """Init the database"""
    app.config['SQLALCHEMY_DATABASE_URI'] = conn_string
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()


def add_product_to_dtb(table, product_json) -> None:
    """Add new product, defined by product_json to the database"""
    product = table(id=product_json['id'], name=product_json['name'], description=product_json['description'])
    db.session.add(product)
    db.session.commit()


def update_product_in_dtb(table, product_id, new_name=None, new_description=None) -> bool:
    """Update product with given id in the database"""
    product = table.query.filter_by(product_id=product_id).first()
    if product:
        if new_name:
            product.name = new_name
        if new_description:
            product.description = new_description
        db.session.commit()
    return bool(product)


def delete_product_from_dtb(table, product_id) -> bool:
    """Delete product with given id from the database"""
    product = table.query.filter_by(id=product_id).first()
    if product:
        db.session.delete(product)
        db.session.commit()
    return bool(product)


def add_offers_to_dtb(table, response, product_id) -> None:
    """Add new offers to database"""
    offers = response.json()
    for offer in offers:
        offer = table(id=offer['id'], price=offer['price'], items_in_stock=offer['items_in_stock'],
                       product_id=product_id)
        db.session.add(offer)
    db.session.commit()


def get_products(table) -> list:
    """Return list of all products in database"""
    products = table.query.all()
    return [product.to_dict() for product in products]


def get_offers(table, product_id=None) -> list:
    """Return list of all offers in database or all offers for product with given id"""
    if product_id:
        offers = table.query.filter_by(product_id=product_id).all()
    else:
        offers = table.query.all()

    return [offer.to_dict() for offer in offers]

"""Module with database models"""
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class Products(db.Model):
    """Class database model for Products"""
    # pylint: disable=too-few-public-methods
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(155))
    description = db.Column(db.String(255))
    offers = db.relationship('Offers', backref='product')

    def to_dict(self):
        """Return dict representation of the product"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }


class TestProducts(Products):
    """Class database model for Products for tests"""
    __tablename__ = 'test_products'


class Offers(db.Model):
    """Class database model for Offers"""
    # pylint: disable=too-few-public-methods
    id = db.Column(db.String(36), primary_key=True)
    price = db.Column(db.Integer)
    items_in_stock = db.Column(db.Integer)
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'))

    def to_dict(self):
        """Return dict representation of the offer"""
        return {
            'id': self.id,
            'price': self.price,
            'items_in_stock': self.items_in_stock,
            'product_id': self.product_id
        }


class TestOffers(Offers):
    """Class database model for Offers for tests"""
    __tablename__ = 'test_offers'

import datetime

from data.database import session
from data.tables import Product

def add_product(name, expiration_date):
    """Add a new product to the database."""
    new_product = Product(name=name, expiration_date=expiration_date)
    session.add(new_product)
    session.commit()

def get_near_expiry_products():
    """Fetch products that are nearing expiration."""
    today = datetime.date.today()
    warning_date = today + datetime.timedelta(days=3)  # Example: alert 3 days before
    products = session.query(Product).filter(Product.expiration_date <= warning_date).all()
    return products

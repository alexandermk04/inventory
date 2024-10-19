import datetime

from data.database import session
from data.tables import Product, ProductInformation, Category

def add_product(product_id: int, purchase_date: datetime.datetime, expiration_date: datetime.datetime = None):
    """Add a new product to the database."""
    new_product = Product(product_information_id=product_id,
                            purchase_date=purchase_date, 
                            expiration_date=expiration_date)
    session.add(new_product)
    session.commit()
    return new_product.id

def add_product_information(name: str, average_shelf_life_days: int = None):
    """Add a new product information to the database."""
    new_product_information = ProductInformation(name=name,
                                                average_shelf_life_days=average_shelf_life_days)
    session.add(new_product_information)
    session.commit()

def get_product_information(name: str) -> ProductInformation | None:
    """Get the product information for a given name."""
    res = session.query(ProductInformation).filter_by(name=name).first()
    return res

def update_shelf_life(product_id: int, average_shelf_life_days: int):
    """Update the shelf life of a product."""
    # Update in the product information
    product = session.query(ProductInformation).filter_by(id=product_id).first()
    product.average_shelf_life_days = average_shelf_life_days
    
    # Update in all products currently in inventory
    existing_products = session.query(Product).filter_by(product_information_id=product_id).all()
    for existing_product in existing_products:
        existing_product.expiration_date = existing_product.purchase_date + datetime.timedelta(days=average_shelf_life_days)
    session.commit()

def add_category(name: str):
    """Add a new category to the database."""
    new_category = Category(name=name)
    session.add(new_category)
    session.commit()

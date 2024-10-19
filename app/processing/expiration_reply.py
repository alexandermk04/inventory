import datetime

from data.tables import ProductInformation
from data.repository import get_product_information, update_shelf_life

import logging

logger = logging.getLogger(__name__)

class ExpirationProcessor:
    product_name: str
    expiration_date_string: str
    expiration_date: datetime.datetime
    product_information: ProductInformation

    def __init__(self, product_name: str, expiration_date: str):
        self.product_name = product_name
        self.expiration_date_string = expiration_date

    def search_product(self) -> bool:
        """Search for the product in the database."""
        self.product_information = get_product_information(self.product_name)
        return self.product_information is not None
    
    def parse_expiration_date(self):
        """Parse the expiration date string."""
        try:
            self.expiration_date = datetime.datetime.strptime(self.expiration_date_string, '%d.%m.%Y')
            return True
        except:
            return False
        
    def update_shelf_life(self):
        """Update the shelf life of the product."""
        shelf_life_days = (self.expiration_date - datetime.datetime.now()).days
        update_shelf_life(self.product_information.id, shelf_life_days)
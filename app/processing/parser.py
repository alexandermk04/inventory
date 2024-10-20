import logging
import re
import os
import datetime
import pytesseract

from PIL import Image

from data.repository import add_product, add_product_information, get_product_information

logger = logging.getLogger(__name__)

class ReceiptProcessor:
    file_path: str
    image: Image
    full_receipt: str
    lines: list[str]
    pruchase_date: datetime.datetime
    items: list[tuple[str, int]]
    added_products: int
    new_products: list[str]

    def __init__(self, file_path):
        self.file_path = file_path
        self.image = Image.open(file_path)
        self.full_receipt = str(pytesseract.image_to_string(self.image, lang='deu'))
        os.remove(file_path)
        #logger.info(f"Extracted text from the receipt: {self.full_receipt}")
        self.lines = self.full_receipt.splitlines()
        self.purchase_date = self.extract_date()
        self.items = self.extract_items()
        self.added_products = 0
        self.new_products = []
        

    def extract_date(self) -> datetime.datetime:
        date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
        date_of_purchase = None
        for line in self.lines:
            match = date_pattern.search(line)
            if match:
                date_of_purchase = match.group()
                break
        try:
            date = datetime.datetime.strptime(date_of_purchase, '%Y-%m-%d')
        except:
            date = datetime.datetime.now()
            
        today = datetime.datetime.now()

        # Check if the date is valid:
        if date > today or date < today - datetime.timedelta(days=7):
            return today

        return date
    
    def extract_items(self) -> list[tuple[str, int]]:
        items = []
        item_pattern = re.compile(r'\s*(\d+\,\d+)\s*[A|B]')
        
        for line in self.lines:
            match = item_pattern.search(line)
            if match:
                item_name = self.extract_name(line)
                optional_quantity = self.extract_quantity(line) or 1
                items.append((item_name.strip(), optional_quantity))
        
        return items

    def extract_name(self, line: str):
        name_pattern = re.compile(r'([^\d]+)')
        match = name_pattern.search(line)
        return str(match.group(1)) or "Unknown"

    def extract_quantity(self, line: str):
        quantity_pattern = re.compile(r'([\d+,]?\d{2})\s*x\s*(\d+)')
        match = quantity_pattern.search(line)
        return int(match.group(2)) if match else None
    
    def process_receipt(self):
        for item in self.items:
            self.move_item_to_db(item)
        logger.info(f"Added {self.added_products} products to the database.")
        logger.info(f"New products: {', '.join(self.new_products)}")

    
    def move_item_to_db(self, item: tuple[str, int]):
        name, quantity = item
        product_information = get_product_information(name)
        if not product_information:
            add_product_information(name)
            self.new_products.append(name)
            product_information = get_product_information(name)
        
        days = product_information.average_shelf_life_days
        expiration_date = self.purchase_date + datetime.timedelta(days=days) if days else None
        for _ in range(quantity):
            add_product(product_information.id, self.purchase_date, expiration_date=expiration_date)
            self.added_products += 1
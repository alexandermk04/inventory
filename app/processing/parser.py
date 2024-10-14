import logging
import re
import datetime
import pytesseract

from PIL import Image

from data.repository import add_product

logger = logging.getLogger(__name__)

def process_receipt(file_path):
    # Open the receipt image or PDF
    image = Image.open(file_path)
    
    # Use Tesseract to extract text
    full_receipt = str(pytesseract.image_to_string(image, lang='deu'))
    lines = full_receipt.splitlines()
    date = extract_date(lines)
    items = extract_items(lines)

    amount = process_items(items, date)
    return amount

def process_items(items: list[tuple[str, int]], date: datetime.datetime) -> int:
    amount = 0
    for item in items:
        # TODO: Calculate expiration date based on the current date and the item's shelf life
        expiration_date = date + datetime.timedelta(days=7)
        name, quantity = item
        for _ in range(quantity):
            add_product(name, expiration_date)
            amount += 1
    
    return amount

def extract_date(lines: list[str]) -> datetime.datetime:
    date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
    date_of_purchase = None
    for line in lines:
        match = date_pattern.search(line)
        if match:
            date_of_purchase = match.group()
            break

    logger.info(f'Date of purchase: {date_of_purchase}')
    # TODO: Parse to datetime object
    # TODO: Add check to ensure date is valid

    date = datetime.datetime.strptime(date_of_purchase, '%Y-%m-%d')
    today = datetime.datetime.now()

    # Check if the date is valid:
    if date > today or date < today - datetime.timedelta(days=7):
        return today

    return date

def extract_items(lines: list[str]) -> list[tuple[str, int]]:
    items = []
    item_pattern = re.compile(r'\s*(\d+\,\d+)\s*[A|B]')
    
    for line in lines:
        match = item_pattern.search(line)
        if match:
            item_name = extract_name(line)
            optional_quantity = extract_quantity(line) or 1
            items.append((item_name, optional_quantity))
    
    return items

def extract_name(line: str):
    name_pattern = re.compile(r'([^\d]+)')
    match = name_pattern.search(line)
    return match.group(1) or "Unknown"

def extract_quantity(line: str):
    quantity_pattern = re.compile(r'([\d+,]?\d{2})\s*x\s*(\d+)')
    match = quantity_pattern.search(line)
    return int(match.group(2)) if match else None


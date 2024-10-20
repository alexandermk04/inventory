import logging

from telegram.ext import ContextTypes
from telegram import Update

from processing.parser import ReceiptProcessor
from processing.expiration_reply import ExpirationProcessor
from data.repository import get_categories, add_active_poll, get_product_information, get_active_poll, \
    add_product_category, delete_active_poll, delete_product_categories, add_category

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Hi! Send me a receipt, and I will track expiration dates for you.')

async def add_category_from_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a new category to the database."""
    category_name = update.message.text.split(' ')[1]
    add_category(category_name)
    await update.message.reply_text(f'Category {category_name} added.')

async def handle_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the receipt sent by the user."""
    photo = update.message.photo[-1]
    # Download the file for further processing
    if photo:
        file_id = photo.file_id
        new_file = await context.bot.get_file(file_id)
        await new_file.download_to_drive('receipts/receipt.png')  # Save file locally for processing
        await update.message.reply_text('Receipt received. Processing...')

        processor = ReceiptProcessor('receipts/receipt.png')
        processor.process_receipt()

        await update.message.reply_text(f'Added {processor.added_products} items to your inventory.')
        if len(processor.new_products) > 0:
            await update.message.reply_text(
                '''
                There are some new products with unknown expiration dates.
                Please provide those by replying to their names.
                '''
            )
        for new_product in processor.new_products:
            await update.message.reply_text(new_product)
            await send_category_poll(update, new_product)

    else:
        await update.message.reply_text('Please send a valid receipt!')

async def send_category_poll(update: Update, product_name: str):
    categories = get_categories()
    product = get_product_information(product_name)

    poll = await update.message.reply_poll(
                question=f"Please select the categories for {product_name}",
                options=[category.name for category in categories],
                is_anonymous=False,
                allows_multiple_answers=True)
    
    add_active_poll(poll.poll.id, product)

async def handle_expiration_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the expiration date update."""
    processor = ExpirationProcessor(
        product_name=update.message.reply_to_message.text,
        expiration_date=update.message.text
    )
    if not processor.search_product():
        await update.message.reply_text("The referenced product doesn't exist.")
        return
    if not processor.parse_expiration_date():
        await update.message.reply_text("Invalid date: Please use the form dd.mm.yyyy!")
        return
    processor.update_shelf_life()
    await update.message.reply_text("Expirations dates updated.")

async def handle_category_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Collects information from the category poll of a product."""
    # Answer removed from poll
    try:
        update.poll_answer.option_ids
    except AttributeError:
        return
    
    poll_id = update.poll_answer.poll_id
    poll = get_active_poll(poll_id)
    if poll is None:
        await update._bot.send_message(chat_id=update.effective_user.id, # Appearently works also with user id
                                       text="This poll is not active anymore.")
        return

    product_id = poll.product_information.id
    categories = get_categories()

    # Purge all previous categories before adding the new ones
    delete_product_categories(product_id)
    
    for option in update.poll_answer.option_ids:
        category = categories[option]
        add_product_category(product_id, category.id)

    delete_active_poll(poll_id)
import os

from dotenv import load_dotenv
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes, ApplicationBuilder
from telegram import Update
import logging

from processing.parser import ReceiptProcessor
from processing.expiration_reply import ExpirationProcessor

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define your bot token here
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Hi! Send me a receipt, and I will track expiration dates for you.')

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

    else:
        await update.message.reply_text('Please send a valid receipt!')

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

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    """Start the bot."""
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_receipt))
    app.add_handler(MessageHandler(filters.REPLY, handle_expiration_update))
    app.add_error_handler(error)

    app.run_polling(poll_interval=3)

if __name__ == '__main__':
    main()

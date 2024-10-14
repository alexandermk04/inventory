import os

from dotenv import load_dotenv
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes, ApplicationBuilder
from telegram import Update
import logging

from processing.parser import process_receipt

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

        # TODO: Call your OCR function to process the receipt and extract the items
        items_amount = process_receipt('receipts/receipt.png')
        await update.message.reply_text(f'Added {items_amount} items to your inventory.')

    else:
        await update.message.reply_text('Please send a valid receipt!')

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    """Start the bot."""
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_receipt))
    app.add_error_handler(error)

    app.run_polling(poll_interval=3)

if __name__ == '__main__':
    main()

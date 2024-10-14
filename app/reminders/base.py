from apscheduler.schedulers.background import BackgroundScheduler
import datetime

from data.database import get_near_expiry_products

def send_reminders(context):
    products = get_near_expiry_products()
    for product in products:
        message = f"Reminder: {product.name} is expiring on {product.expiration_date}!"
        context.bot.send_message(chat_id='YOUR_CHAT_ID', text=message)

def setup_reminders(bot):
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_reminders, 'interval', hours=24, args=[bot])  # Check every 24 hours
    scheduler.start()

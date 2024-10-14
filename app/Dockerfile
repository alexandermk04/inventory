FROM python:3.10.14-slim

WORKDIR /app

# Update and install tesseract along with German language support
RUN apt-get update \
  && apt-get -y install tesseract-ocr \
  && apt-get -y install tesseract-ocr-deu \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install python-telegram-bot alembic pytesseract
RUN pip install watchdog
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire app directory
COPY . .

# Ensure the .env file is included
COPY .env /app/.env

# Run Alembic migrations before starting the bot
CMD ["sh", "-c", "./run_alembic.sh && watchmedo auto-restart --patterns=*.py --recursive -- python bot.py"]
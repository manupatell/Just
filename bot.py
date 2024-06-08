import requests
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext
import logging
import threading
import time

# Replace 'YOUR_TELEGRAM_BOT_TOKEN' with the token you received from BotFather
TELEGRAM_BOT_TOKEN = '7464935338:AAFIYTzrtJqMvsm7m1x6HUxGJhsf9fvEMLs'
PING_URL = 'https://just-ltho.onrender.com'  # Replace with the URL you want to ping
PING_INTERVAL = 60  # Interval in seconds (e.g., 300 seconds = 5 minutes)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Welcome! Use /search <movie_or_series_name> to get information. Use /ping to check bot responsiveness.')

def ping(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Pong!')

def search(update: Update, context: CallbackContext) -> None:
    if not context.args:
        update.message.reply_text('Please provide a movie or series name.')
        return

    query = ' '.join(context.args)
    url = f'https://apis.justwatch.com/content/titles/en_US/popular?body={{"query":"{query}"}}'
    response = requests.get(url)

    # Check for a valid response
    if response.status_code != 200:
        update.message.reply_text('Error: Unable to fetch data from JustWatch.')
        logger.error(f'JustWatch API error: {response.status_code} - {response.text}')
        return

    try:
        data = response.json()
    except ValueError as e:
        update.message.reply_text('Error: Received invalid JSON from JustWatch.')
        logger.error(f'JSON decode error: {e} - Response text: {response.text}')
        return

    if not data['items']:
        update.message.reply_text('No results found.')
        return

    result = data['items'][0]
    title = result['title']
    original_release_year = result.get('original_release_year', 'N/A')
    object_type = result['object_type']
    scoring = next((score for score in result.get('scoring', []) if score['provider_type'] == 'tmdb:score'), {'value': 'N/A'})['value']

    providers = []
    if 'offers' in result:
        for offer in result['offers']:
            provider = offer['provider_id']
            provider_name = get_provider_name(provider)
            if provider_name not in providers:
                providers.append(provider_name)
        providers = ', '.join(providers)
    else:
        providers = 'N/A'

    message = (
        f"*Title:* {title}\n"
        f"*Year:* {original_release_year}\n"
        f"*Type:* {object_type.capitalize()}\n"
        f"*Rating:* {scoring}\n"
        f"*Providers:* {providers}\n"
        f"[More Info](https://www.justwatch.com)"
    )

    update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

def get_provider_name(provider_id):
    # This function maps provider IDs to human-readable names
    provider_mapping = {
        8: "Netflix",
        9: "Amazon Prime Video",
        337: "Disney+",
        356: "Aha",
        121: "ETV Win",
        122: "Zee5",
        # Add more mappings as needed
    }
    return provider_mapping.get(provider_id, f"Provider {provider_id}")

def auto_ping():
    while True:
        try:
            response = requests.get(PING_URL)
            if response.status_code == 200:
                logger.info(f'Successfully pinged {PING_URL}')
            else:
                logger.warning(f'Failed to ping {PING_URL}: {response.status_code}')
        except Exception as e:
            logger.error(f'Error pinging {PING_URL}: {e}')
        time.sleep(PING_INTERVAL)

def main() -> None:
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("ping", ping))
    dispatcher.add_handler(CommandHandler("search", search))

    # Start the auto-pinger in a separate thread
    ping_thread = threading.Thread(target=auto_ping, daemon=True)
    ping_thread.start()

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

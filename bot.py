import requests
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext

# Replace 'YOUR_TELEGRAM_BOT_TOKEN' with the token you received from BotFather
TELEGRAM_BOT_TOKEN = '7464935338:AAFIYTzrtJqMvsm7m1x6HUxGJhsf9fvEMLs'

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Welcome! Use /search <movie_or_series_name> to get information.')

def search(update: Update, context: CallbackContext) -> None:
    if not context.args:
        update.message.reply_text('Please provide a movie or series name.')
        return

    query = ' '.join(context.args)
    url = f'https://apis.justwatch.com/content/titles/en_US/popular?body={{"query":"{query}"}}'
    response = requests.get(url)
    data = response.json()

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

def main() -> None:
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("search", search))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

import logging
from dotenv import load_dotenv
import telegram
from telegram import Update
from telegram.ext import Updater, Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
import os
from query import search
import geopy
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


geolocator = geopy.Nominatim(user_agent='recycleTeleBot972022')
load_dotenv()
TOKEN = os.getenv('TOKEN')
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
cred = credentials.Certificate("test-6d84c-firebase-adminsdk-qknug-c1c6c4f968.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
geolocator = geopy.Nominatim(user_agent='recycleTeleBot972022')

POSTAL_CODE = range(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="I'm a bot, please talk to me!")

async def search_bin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttonList =  [[telegram.KeyboardButton(text='Share your location!', request_location = True)]]
    markup = telegram.ReplyKeyboardMarkup(buttonList, one_time_keyboard = True)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Share your location with us to find out the nearest e-waste bin! "
                                        + "Remember to turn on location services :)",
                                   reply_markup=markup)


async def manage_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lat = update.message.location.latitude
    long= update.message.location.longitude
    location = geolocator.reverse([lat, long])
    postal_code = location.raw['address']['postcode']
    messages = search(postal_code, db)
    for msg in messages:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text = msg)

async def postal_code_search_bin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a valid postal code to find e-waste bins nearby :)")
    return POSTAL_CODE

async def postal_code_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = str(update.effective_message.text)
    if (len(message) != 6) or (not message.isnumeric()) or (int(message) >= 900000):
        await update.message.reply_text("Invalid postal code. Try again :)")
    else:
        messages = search(message, db)
        for msg in messages:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                    text = msg)
        return ConversationHandler.END


if __name__ == '__main__':
    application = Application.builder().token(TOKEN).build()
    start_handler = CommandHandler('start', start)
    search_bin_handler = CommandHandler('search_bin', search_bin)
    application.add_handler(start_handler)
    application.add_handler(search_bin_handler)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('postalcodesearchbin', postal_code_search_bin)],
        fallbacks=[],
        states={
            POSTAL_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, postal_code_search)],
        },
    )
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.LOCATION & ~filters.COMMAND, manage_location))

    application.run_polling()

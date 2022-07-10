
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ConversationHandler, MessageHandler, filters, ApplicationBuilder, ContextTypes
import os
import telegram
import logging
from query import search
import geopy
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

geolocator = geopy.Nominatim(user_agent=os.environ.get('USER_AGENT'))
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

PROJECT_ID = os.environ.get('PROJECT_ID')
PRIVATE_KEY_ID = os.environ.get('PRIVATE_KEY_ID')
PRIVATE_KEY = os.environ.get('PRIVATE_KEY').replace('\\n', '\n')
CLIENT_EMAIL = os.environ.get('CLIENT_EMAIL')
CLIENT_ID = os.environ.get('CLIENT_ID')
logger.info(CLIENT_ID)
CLIENT_CERT_URL = os.environ.get('CLIENT_CERT_URL')
json = {
  "type": "service_account",
  "project_id": PROJECT_ID,
  "private_key_id": PRIVATE_KEY_ID,
  "private_key": PRIVATE_KEY,
  "client_email": CLIENT_EMAIL,
  "client_id": CLIENT_ID,
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": CLIENT_CERT_URL
}

PORT = int(os.environ.get('PORT', '8443'))
BOT_TOKEN = os.environ.get('BOT_TOKEN')
cred = credentials.Certificate(json)
firebase_admin.initialize_app(cred)
db = firestore.client()
POSTAL_CODE = range(1)
bot = ApplicationBuilder().token(BOT_TOKEN).build()

async def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


async def start(update, context):
    logger.info("start command")
    await update.message.reply_text(f"Hello {update.effective_user.first_name}! I am GreenSGBot, the recycling expert! Use the following commands to find out more information about recycling! \n \n" + 
        "Use /info to find out whether an item is suitable for recycling.\nUse /search_bin to find out the e-waste bins located near you by sharing your location.\nUse /postalcodesearchbin to find out the e-waste bins near you by sending your postal code. ")

async def help(update, context):
    await update.message.reply_text("Use the following commands to find out more information about recycling! \n \n" + 
        "Use /info to find out whether an item is suitable for recycling.\nUse /search_bin to find out the e-waste bins located near you by sharing your location.\nUse /postalcodesearchbin to find out the e-waste bins near you by sending your postal code.")

async def getInfo(update, context):
    item = update.message.text.casefold()
    items_ref = db.collection(u'recycling-information')
    query_ref = items_ref.where(u'item', u'==', item).stream()
    for query in query_ref:
        if query:
            await update.effective_message.reply_text(getMessage(query), reply_markup = ReplyKeyboardRemove())
            return
    query_keywords = item.rsplit(" ")
    query_ref = items_ref.where(u'keywords', u'array_contains_any', query_keywords).stream()
    keyboard = []
    for query in query_ref:
        result = query.get('item')
        keyboard.append([InlineKeyboardButton(result, callback_data=result)])

    if len(keyboard):
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Did you mean:", reply_markup=reply_markup)
    else:
        await update.effective_message.reply_text(f"Oh no! I have no information for {item}. Please try another keyword.", reply_markup = ReplyKeyboardRemove())

async def getSpcifiedInfo(update, context):
    query = update.callback_query

    query.answer()
    item = query.data
    items_ref = db.collection(u'recycling-information')
    query_ref = items_ref.where(u'item', u'==', item).stream()
    for query in query_ref:
        await update.effective_message.reply_text(getMessage(query), reply_markup = ReplyKeyboardRemove())

def getMessage(query):
    message = query.get("info")
    if query.get("bluebin"):
        return message +"\nYou can simply place it in the blue recycling bins."
    else:
        return message + "\nPlease do not place it in the blue recycling bins"

async def startGetInfo(update, context):
    await update.message.reply_text("What would you like to recycle today?")  
    return ConversationHandler.END

message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, getInfo)

async def search_bin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot.add_handler(MessageHandler(filters.LOCATION & ~filters.COMMAND, manage_location))
    buttonList =  [[telegram.KeyboardButton(text='Share your location!', request_location = True)]]
    markup = telegram.ReplyKeyboardMarkup(buttonList, one_time_keyboard = True)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Share your location with us to find out the nearest e-waste bin! "
                                        + "Remember to turn on location services :)",
                                   reply_markup=markup)
    return ConversationHandler.END


async def manage_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lat = update.message.location.latitude
    long= update.message.location.longitude
    location = geolocator.reverse([lat, long])
    postal_code = location.raw['address']['postcode']
    messages = search(postal_code, db)
    for msg in messages:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text = msg, reply_markup=ReplyKeyboardRemove())
                                       

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

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('postalcodesearchbin', postal_code_search_bin)],
    fallbacks=[],
    states={
        POSTAL_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, postal_code_search)],
    },
)

def main():
    search_bin_handler = CommandHandler('search_bin', search_bin)
    bot.add_handler(CommandHandler('start', start))
    bot.add_handler(CommandHandler('help', help))
    bot.add_error_handler(error)
    bot.add_handler(CommandHandler('info', startGetInfo))
    bot.add_handler(search_bin_handler)
    bot.add_handler(conv_handler)
    bot.add_handler(message_handler) 
    bot.add_handler(CallbackQueryHandler(getSpcifiedInfo))
    bot.run_webhook(listen="0.0.0.0",
                            port=int(PORT),
                            url_path=BOT_TOKEN,
                            webhook_url='https://arcane-beyond-43802.herokuapp.com/' + BOT_TOKEN)
    bot.start()


if __name__ == '__main__':
    main()

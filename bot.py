from queue import Queue
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler, filters, ApplicationBuilder
import os
import logging
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

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
  "project_id": "test-6d84c",
  "private_key_id": PRIVATE_KEY_ID,
  "private_key": PRIVATE_KEY,
  "client_email": CLIENT_EMAIL,
  "client_id": CLIENT_ID,
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": CLIENT_CERT_URL
}

PORT = int(os.environ.get('PORT', 8443))
BOT_TOKEN = os.environ.get('BOT_TOKEN')
db = None

async def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def start(update, context):
    logger.info("start command")
    update.message.reply_text(f"Hello {update.effective_user.first_name}! I am SYJ, the recycling expert! Use the following commands to find out more information about recycling! \n \n" + 
        "Use /info to find out whether an item is suitable to recycling.\nUse /ewaste to find out the e-waste bins located near you.")

def help(update, context):
    update.message.reply_text("Use the following commands to find out more information about recycling! \n \n" + 
        "Use /info to find out whether an item is suitable to recycling.\nUse /ewaste to find out the e-waste bins located near you.")

def getInfo(update, context):
    item = update.message.text.casefold()
    items_ref = db.collection(u'recycling-information')
    query_ref = items_ref.where(u'item', u'==', item).stream()
    for query in query_ref:
        if query:
            update.effective_message.reply_text(getMessage(query))
            return
    query_keywords = item.rsplit(" ")
    query_ref = items_ref.where(u'keywords', u'array_contains_any', query_keywords).stream()
    keyboard = []
    for query in query_ref:
        result = query.get('item')
        keyboard.append([InlineKeyboardButton(result, callback_data=result)])

    if len(keyboard):
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Did you mean:", reply_markup=reply_markup)
    else:
        update.effective_message.reply_text(f"No information can be found for {item}. Please try another keyword. ")

def getSpcifiedInfo(update, context):
    query = update.callback_query

    query.answer()
    item = query.data
    items_ref = db.collection(u'recycling-information')
    query_ref = items_ref.where(u'item', u'==', item).stream()
    for query in query_ref:
        update.effective_message.reply_text(getMessage(query))

def getMessage(query):
    message = query.get("info")
    if query.get("bluebin"):
        return message +"\nYou can simply place it in the blue recycling bins."
    else:
        return message + "\nPlease do not place it in the blue recycling bins"

def startGetInfo(update, context):
    update.message.reply_text("What would you like to recycle today?")  
    
def ewaste(update, context):
    update.message.reply_text("Get e-waste bin location")

message_handler = MessageHandler(filters.TEXT, getInfo)

def main():
    # bot = Bot(BOT_TOKEN)
    # updater = Updater(bot, update_queue=Queue())
    # updater.initialize()
    bot = ApplicationBuilder().token(BOT_TOKEN).build()

    logger.info("main called")
    cred = credentials.Certificate(json)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    bot.add_handler(CommandHandler('start', start))
    bot.add_handler(CommandHandler('help', help))
    bot.add_error_handler(error)
    bot.add_handler(CommandHandler('info', startGetInfo))
    bot.add_handler(message_handler) 
    bot.add_handler(CallbackQueryHandler(getSpcifiedInfo))
    bot.add_handler(CommandHandler("ewaste", ewaste))
    update_queue = bot.update_queue
    bot.run_webhook(listen="0.0.0.0",
                            port=int(PORT),
                            url_path=BOT_TOKEN,
                            webhook_url='https://arcane-beyond-43802.herokuapp.com/')
    bot.start()


if __name__ == '__main__':
    main()
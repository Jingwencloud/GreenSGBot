from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler, filters, Updater
import os
import logging
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# PROJECT_ID = os.environ.get('PROJECT_ID')
# PRIVATE_KEY_ID = os.environ.get('PRIVATE_KEY_ID')
# PRIVATE_KEY = os.environ.get('PRIVATE_KEY')
# CLIENT_EMAIL = os.environ.get('CLIENT_EMAIL')
# CLIENT_ID = os.environ.get('CLIENT_ID')
# CLIENT_CERT_URL = os.environ.get('CLIENT_CERT_URL')
# json = {
#   "type": "service_account",
#   "project_id": PROJECT_ID,
#   "private_key_id": PRIVATE_KEY_ID,
#   "private_key": PRIVATE_KEY,
#   "client_email": CLIENT_EMAIL,
#   "client_id": CLIENT_ID,
#   "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#   "token_uri": "https://oauth2.googleapis.com/token",
#   "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#   "client_x509_cert_url": CLIENT_CERT_URL
# }


# cred = credentials.Certificate(json)
# firebase_admin.initialize_app(cred)

# db = firestore.client()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

PORT = int(os.environ.get('PORT', 5000))
BOT_TOKEN = os.environ.get('BOT_TOKEN')

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

async def start(update, context):
    logger.log("start command")
    await update.message.reply_text(f"Hello {update.effective_user.first_name}! I am SYJ, the recycling expert! Use the following commands to find out more information about recycling! \n \n" + 
        "Use /info to find out whether an item is suitable to recycling.\nUse /ewaste to find out the e-waste bins located near you.")

async def help(update, context):
    await update.message.reply_text("Use the following commands to find out more information about recycling! \n \n" + 
        "Use /info to find out whether an item is suitable to recycling.\nUse /ewaste to find out the e-waste bins located near you.")

# async def getInfo(update, context):
#     item = update.message.text.casefold()
#     items_ref = db.collection(u'recycling-information')
#     query_ref = items_ref.where(u'item', u'==', item).stream()
#     for query in query_ref:
#         if query:
#             await update.effective_message.reply_text(getMessage(query))
#             return
#     query_keywords = item.rsplit(" ")
#     query_ref = items_ref.where(u'keywords', u'array_contains_any', query_keywords).stream()
#     keyboard = []
#     for query in query_ref:
#         result = query.get('item')
#         keyboard.append([InlineKeyboardButton(result, callback_data=result)])

#     if len(keyboard):
#         reply_markup = InlineKeyboardMarkup(keyboard)
#         bot.add_handler(CallbackQueryHandler(getSpcifiedInfo))
#         await update.message.reply_text("Did you mean:", reply_markup=reply_markup)
#     else:
#         await update.effective_message.reply_text(f"No information can be found for {item}. Please try another keyword. ")

# async def getSpcifiedInfo(update, context):
#     query = update.callback_query

#     await query.answer()
#     item = query.data
#     items_ref = db.collection(u'recycling-information')
#     query_ref = items_ref.where(u'item', u'==', item).stream()
#     for query in query_ref:
#         await update.effective_message.reply_text(getMessage(query))

# def getMessage(query):
#     message = query.get("info")
#     if query.get("bluebin"):
#         return message +"\nYou can simply place it in the blue recycling bins."
#     else:
#         return message + "\nPlease do not place it in the blue recycling bins"

# async def startGetInfo(update, context):
#     await update.message.reply_text("What would you like to recycle today?")  
    
# async def ewaste(update, context):
#     await update.message.reply_text("Get e-waste bin location")

# message_handler = MessageHandler(filters.TEXT, getInfo)

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    bot = updater.dispatcher
    logger.log("main called")
    bot.add_handler(CommandHandler('start', start))
    bot.add_handler(CommandHandler('help', help))
    bot.add_error_handler(error)
    # bot.add_handler(CommandHandler('info', startGetInfo))
    # bot.add_handler(message_handler) 
    # bot.add_handler(CommandHandler("ewaste", ewaste))
    updater.start_webhook(listen="0.0.0.0",
                            port=int(PORT),
                            url_path=BOT_TOKEN)
    updater.bot.setWebhook('https://arcane-beyond-43802.herokuapp.com/' + BOT_TOKEN)
    updater.idle()

if __name__ == '__main__':
    main()
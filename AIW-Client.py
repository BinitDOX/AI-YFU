import logging
from telegram import Update, ChatAction
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from gradio_client import Client
from threading import Thread, Timer
from datetime import datetime
import schedule
import pytz
import random
import time
import ngrok


# ---CONFIG---
TZ_IST = pytz.timezone('Asia/Shanghai')

BOT_TOKEN = 'bot_token'
YOUR_USER_ID = 000000

NGROK_API_KEY = "auth_key"

AI = 'ai name'

TIMES_SELF_START = 50
FROM_HRS = 9  # 9AM to
TO_HRS = 26  # 2AM

DELAYED_RESPONSES = True
# ------------

gr_client = None
ngrok_api = None
last_update = None
scheduled_job = None
idle = True
idle_job = None

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the /start command handler
def start(update: Update, context: CallbackContext) -> None:
    global last_update
    last_update = update
    update.message.reply_text(f'SYSTEM: {AI} is now initialized')


def auto_update_api():
    global NGROK_API_KEY
    global ngrok_api
    global gr_client

    try:
        client = ngrok.Client(NGROK_API_KEY)

        tunnels = client.tunnels.list(limit=1)
        if len(tunnels.tunnels) == 0:
            gr_client = None
            return

        for t in tunnels:
            if str(t.public_url) != ngrok_api:
                ngrok_api = str(t.public_url)
                gr_client = Client(str(t.public_url))
                logger.info("[+] API updated successfully!")
    except Exception as e:
        error_message = f"An error occurred in auto_update_api: {str(e)}"
        logger.error(error_message)


def handle_message(update: Update, context: CallbackContext) -> None:
    global last_update
    global scheduled_job
    global idle

    last_update = update

    if gr_client == None:
        logger.error("[-] API is down")
        update.message.reply_text(f"SYSTEM: {AI} is sleeping. Please try again later.")
        return

    try:
        if str(update.message.from_user.id) != str(YOUR_USER_ID):
            update.message.reply_text("SYSTEM: Unauthorized user. Access denied.")
            return

        message_text = update.message.text
        message_audio = update.message.voice

        # Check if the message contains text or audio
        if message_text:
            # Call the API for text processing
            message_text = str(''.join(update.message.text))

            if DELAYED_RESPONSES and idle:
                if scheduled_job and scheduled_job.is_alive():
                    scheduled_job.cancel()

                result = gr_client.predict("RESPOND_TO_TEXT", "[NOP]"+message_text, None, api_name="/predict")
                delay_seconds = random.randint(15, 50)
                scheduled_job = Timer(delay_seconds, manual_self_start)
                scheduled_job.start()
            else:
                update.message.chat.send_action(ChatAction.TYPING)
                result = gr_client.predict("RESPOND_TO_TEXT", message_text, None, api_name="/predict")
                send_results(update, result)
        elif message_audio:
            update.message.chat.send_action(ChatAction.TYPING)
            # Call the API for audio processing
            audio_file_id = message_audio.file_id
            audio_file_path = 'voice_msg.mp3'
            context.bot.get_file(audio_file_id).download(audio_file_path)

            result = gr_client.predict("RESPOND_TO_AUDIO", None, audio_file_path, api_name="/predict")
            send_results(update, result)
        else:
            update.message.reply_text("SYSTEM: Unsupported message type. Send text or audio.")

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        logger.error(error_message)
        update.message.reply_text("SYSTEM: An error occurred. Please try again later.")

def manual_self_start():
    global last_update
    global scheduled_job
    global idle
    global idle_job

    idle = False
    last_update.message.chat.send_action(ChatAction.TYPING)

    result = gr_client.predict("SELF_START", None, None, api_name="/predict")
    send_results(last_update, result)

    scheduled_job = None
    if idle_job and idle_job.is_alive():
        idle_job.cancel()
    idle_job = Timer(85, set_idle)
    idle_job.start()


def set_idle():
    global idle
    idle = True

# Function to send results to the user
def send_results(update: Update, result: list) -> None:
    try:
        # Check if the result list is not empty
        if result:
            print(result)
            # Send text result
            if result[0]:
                resp = result[0]
                if '<SEP>' in result[0]:
                    trans, resp = result[0].split('<SEP>')
                    original_message_id = update.message.message_id
                    trans = trans.replace(".", "\.")
                    update.message.reply_text(f"_Heard: {trans}_", reply_to_message_id=original_message_id, parse_mode='MarkdownV2')
                update.message.reply_text(resp)

            # Send audio result
            if result[1]:
                audio_file_path = result[1]
                with open(audio_file_path, 'rb') as audio_file:
                    update.message.reply_voice(audio_file)

            # Send image result
            if result[2]:
                image_file_path = result[2]
                with open(image_file_path, 'rb') as image_file:
                    update.message.reply_photo(image_file)
        else:
            update.message.reply_text("SYSTEM: No results to send.")

    except Exception as e:
        # Handle errors while sending results
        error_message = f"An error occurred while sending results: {str(e)}"
        logger.error(error_message)
        update.message.reply_text("SYSTEM: An error occurred. Please try again later.")

def execute_self_start():
    global last_update

    if last_update == None:
        logger.error("[-] Bot not started")
        return

    if gr_client == None:
        logger.error("[-] API is down")
        return

    try:
        # Call the API for SELF_START processing
        logger.info("SELF_START executing...")
        result = gr_client.predict("SELF_START", None, None, api_name="/predict")
        send_results(last_update, result)

    except Exception as e:
        error_message = f"An error occurred while executing SELF_START: {str(e)}"
        logger.exception(error_message)

# Random self start scheduler
scheduled_times = []
for _ in range(TIMES_SELF_START):
    random_hour = random.randint(FROM_HRS, TO_HRS) % 24  # Random hour between 9 am and 3 am
    random_minute = random.randint(0, 59)  # Random minute
    scheduled_time = TZ_IST.localize(datetime(datetime.now().year, datetime.now().month, datetime.now().day, random_hour, random_minute))
    scheduled_times.append(scheduled_time.strftime("%H:%M"))
    schedule.every().day.at(scheduled_time.strftime("%H:%M")).do(execute_self_start)

datetime_objects = sorted([datetime.strptime(time, "%H:%M") for time in scheduled_times])
sorted_12hr_format = [time.strftime("%I:%M %p") for time in datetime_objects]
for st in sorted_12hr_format:
    print(st)

# Set up the updater and dispatcher
updater = Updater(BOT_TOKEN)
dispatcher = updater.dispatcher

# Add command and message handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text | Filters.voice, handle_message))

# Start the bot
bot_thread = Thread(target=updater.start_polling)
bot_thread.daemon = True
bot_thread.start()

try:
    while True:
        schedule.run_pending()
        auto_update_api()
        time.sleep(60)

except KeyboardInterrupt:
    print("Received Keyboard Interrupt. Stopping...")

# Wait for the bot thread to finish
bot_thread.join()
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv
import connect
import logging
import os
import datetime
import pytz
import asyncio

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

logging.basicConfig(filename='tadarusku_bot.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')

# Command Handler =======================================================================================
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    check_user = connect.get_tadarus(update.message.from_user.id)

    message = f"Assalamu'alaikum, {update.message.from_user.first_name}!\n\n" \
               "Selamat datang di 📖 Tadarusku Bot. Bot ini akan membantu kamu untuk mengingatkan jadwal tadarus kamu.\n\n" \
               "Pengingat akan diberikan setiap hari dan pengingat akan berhenti apabila kamu sudah checkin pada hari tersebut.\n\n" \
               "Pastikan kamu selalu checkin setelah tadarus ya. Semoga kita semua diberikan kemudahan dalam menjalankan ibadah tadarus.\n\n" \
               "Kamu bisa menggunakan perintah berikut:\n" \
               "/mytadarus - Melihat statistik tadarus kamu\n" \
               "/tips - Untuk mendapatkan tips tadarus\n" \

    if check_user:
        logging.info(f"User {update.message.from_user.id} already registered")
    else:
        logging.info(f"User {update.message.from_user.id} registered")
        connect.add_user(update.message.from_user.id, datetime.date.today().strftime('%d-%m-%Y'), 1)
        connect.new_tadarus(update.message.from_user.id, 0, datetime.date.today().strftime('%d-%m-%Y'))
        
    await update.message.reply_text(message, parse_mode='Markdown') 


async def cmd_check_tadarus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        user = update.message.from_user.id
    elif update.callback_query:
        user = update.callback_query.from_user.id

    stats = connect.get_tadarus(user)
    if stats['rn_date'] == str(datetime.date.today()):
        message = f"Kamu sudah tadarus hari ini kok! 🌟\n" \
    else:
        connect.update_tadarus(user, str(datetime.date.today()))
        message = f"Alhamdulillah kamu sudah tadarus hari ini ! 🌟\n" \
                  f"Kamu sudah tadarus {stats['runtutan']+1} Hari 🔥\n" 
    
    if update.message:
        await update.message.reply_text(message, parse_mode='Markdown')
    elif update.callback_query:
        await update.callback_query.edit_message_text(text=message, parse_mode='Markdown')


async def cmd_mytadarus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        userid = update.message.from_user.id
    elif update.callback_query:
        userid = update.callback_query.from_user.id

    stats = connect.get_tadarus(userid)
    users = connect.get_user_notif()
    status = False

    for user in users:
        logging.info(f"User {userid} notif status: {user}")
        if user[0] == str(userid):
            status = True
            break

    message = f"Berikut runtutan harian tadarus kamu ☺️ \n\n" \
              f"📖 Tadarus Harian: {stats['runtutan']} Hari\n" \
              f"📅 Tanggal Mulai: {stats['start_date']}\n\n" \
              f"Jangan lupa tadarus hari ini ya! Semangat tadarus! 💪🏼\n" \
              f"Status Pengingat : {'Aktif' if status else 'Tidak Aktif'}\n\n"
    
    if status:
        button_label = "Stop Pengingat 🔕"
        alert_data = 'stop_'
    else:
        button_label = "Aktifkan Pengingat 🔔"
        alert_data = 'alert_'

    keyboard = [[InlineKeyboardButton("Sudah Tadarus ✅", callback_data='checkin_'),
                InlineKeyboardButton(button_label, callback_data=alert_data)],
               [InlineKeyboardButton("Riwayat Tadarus 📖", callback_data='stats_')]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    elif update.callback_query:
        await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')


async def cmd_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    history = connect.get_stats(update.callback_query.from_user.id)
    
    message = f"Berikut Riwayat tadarus kamu Sebelumnya ☺️ :\n\n" \
                f"📖 Total Tadarus: {history['runtutan']} Hari\n" \
                f"📅 Tanggal Mulai: {history['start_date']}\n" \
                f"📅 Tanggal Terakhir: {history['last_date']}\n\n" \
                f"Jangan lupa tadarus hari ini ya! Semangat tadarus! 💪🏼"

    keyboard = [[InlineKeyboardButton("Reset History 🔄", callback_data='reset_'),
                 InlineKeyboardButton("Kembali", callback_data='back_')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')


async def cmd_stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = f"apakah kamu yakin ingin menghentikan pengingat tadarus?\n"
    
    keyboard = [[InlineKeyboardButton("Ya", callback_data='yes_stop'),
                 InlineKeyboardButton("Tidak", callback_data='no_stop')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    elif update.callback_query:
        await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')


async def cmd_alert(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = f"apakah kamu yakin ingin mengaktifkan kembali pengingat tadarus?\n"
    
    keyboard = [[InlineKeyboardButton("Ya", callback_data='yes_alert'),
                 InlineKeyboardButton("Tidak", callback_data='no_alert')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    elif update.callback_query:
        await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

# Callback Handler ======================================================================================
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user = query.from_user.id

    if '_' in query.data:
        action, label = query.data.split('_')
    else:
        action = query.data
        return

    if action == 'yes':
        if label == 'stop':
            connect.del_notif(user)
            await query.answer()
            await cmd_mytadarus(update, context)
        elif label == 'reset':
            connect.reset_stats(user)
            message = "Riwayat tadarus kamu sudah direset."
            await query.edit_message_text(message, parse_mode='Markdown')
        elif label == 'alert':
            connect.add_notif(user)
            await query.answer()
            await cmd_mytadarus(update, context)


    elif action == 'no':
        if label == 'stop':
            await query.answer()
            await cmd_mytadarus(update, context)
        elif label == 'reset':
            await query.answer()
            await cmd_history(update, context)
        elif label == 'alert':
            await query.answer()
            await cmd_mytadarus(update, context)

    elif action == 'checkin':
        await query.answer()    
        await cmd_check_tadarus(update, context)

    elif action == 'stop':
        await query.answer()
        await cmd_stop(update, context)
    
    elif action == 'alert':
        await query.answer()
        await cmd_alert(update, context)

    elif action == 'stats':
        await query.answer()
        await cmd_history(update, context)

    elif action == 'reset':
        message = "Apakah kamu yakin ingin mereset riwayat tadarus kamu?\n" \
                  "Data riwayat dan tadarus sekarang akan dihapus dan tidak bisa dikembalikan lagi."

        keyboard = [[InlineKeyboardButton("Ya", callback_data='yes_reset'),
                     InlineKeyboardButton("Tidak", callback_data='no_reset')]]
        keyboard_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(message, reply_markup=keyboard_markup, parse_mode='Markdown')
    
    elif action == 'back':
        await query.answer()
        await cmd_mytadarus(update, context)


# Reminder Handler ======================================================================================
async def send_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    users = connect.get_user_notif()
    message = "Apakah kamu sudah tadarus hari ini ? 📖\n\n" \
  
    keyboard = [[InlineKeyboardButton("Sudah Tadarus ✅", callback_data='checkin_')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    
    logging.info(f"Sending reminder")
    try:
        for user in users:
            user_id = user[0]
            if connect.get_tadarus(user_id)['rn_date'] != str(datetime.date.today()):
                try:
                    await context.bot.send_message(chat_id=user_id, text=message, reply_markup=reply_markup, parse_mode='Markdown')
                    logging.info(f"Reminder sent to user_id: {user_id}")
                except Exception as e:
                    logging.error(f"Failed to send reminder to user_id: {user_id}, error: {e}")

                    try:
                        await context.bot.send_message(chat_id=user_id, text=message, reply_markup=reply_markup, parse_mode='Markdown')
                        logging.info(f"Reminder sent to user_id: {user_id}")
                    except Exception as retry_e:
                        logging.error(f"Failed to send reminder to user_id: {user_id}, error: {retry_e}")
    except Exception as e:
        logging.error(f"Failed to send reminder due to an error: {e}")


def schedule_reminders(application: Application) -> None:
    job_queue = application.job_queue

    timezone = pytz.timezone('Asia/Jakarta')
    logging.info(f"Scheduling reminders")
    times = [
        datetime.time(hour=5, minute=00, tzinfo=timezone),
        datetime.time(hour=12, minute=00, tzinfo=timezone),
        datetime.time(hour=15, minute=30, tzinfo=timezone),
        datetime.time(hour=19, minute=00, tzinfo=timezone)
    ]

    for t in times:
        job_queue.run_daily(send_reminder, time=t)

    job_queue.run_once(send_reminder, when=60)


# Runtime App
def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()


    application.add_handler(CommandHandler('start', cmd_start))
    application.add_handler(CommandHandler('mytadarus', cmd_mytadarus))
    application.add_handler(CallbackQueryHandler(callback_handler))

    schedule_reminders(application)
    
    application.run_polling()


if __name__ == '__main__':
    ascii_art = """

▗▄▄▄▖▗▄▖ ▗▄▄▄  ▗▄▖ ▗▄▄▖ ▗▖ ▗▖ ▗▄▄▖▗▖ ▗▖▗▖ ▗▖
  █ ▐▌ ▐▌▐▌  █▐▌ ▐▌▐▌ ▐▌▐▌ ▐▌▐▌   ▐▌▗▞▘▐▌ ▐▌
  █ ▐▛▀▜▌▐▌  █▐▛▀▜▌▐▛▀▚▖▐▌ ▐▌ ▝▀▚▖▐▛▚▖ ▐▌ ▐▌
  █ ▐▌ ▐▌▐▙▄▄▀▐▌ ▐▌▐▌ ▐▌▝▚▄▞▘▗▄▄▞▘▐▌ ▐▌▝▚▄▞▘
                                                                
    """
    print(ascii_art)
    print("Tadarusku Bot is running...")

    main()


from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv
import connect
import logging
import os
import datetime
import pytz

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
               "Selamat datang di Tadarusku Bot. Bot ini akan membantu kamu untuk mengingatkan jadwal tadarus kamu.\n\n" \
               "Pengingat akan diberikan setiap hari selama tiga kali, yaitu pagi, siang, dan malam.\n\n" \
               "Pengingat akan berhenti apabila kamu sudah checkin pada hari tersebut.\n\n" \
               "Pastikan kamu selalu checkin setelah tadarus ya. Semoga kita semua diberikan kemudahan dalam menjalankan ibadah tadarus.\n\n" \
               "Kamu bisa menggunakan perintah berikut:\n" \
               "/mytadarus - Melihat statistik tadarus kamu\n" \

    if check_user:
        logging.info(f"User {update.message.from_user.id} already registered")
    else:
        logging.info(f"User {update.message.from_user.id} registered")
        connect.add_user(update.message.from_user.id, str(datetime.date.today()), True)
        connect.new_tadarus(update.message.from_user.id, 0, str(datetime.date.today()))
        
    await update.message.reply_text(message, parse_mode='Markdown') 


async def cmd_check_tadarus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user.id
    stats = connect.get_stats(user)
    if stats['rn_date'] == str(datetime.date.today()):
        message = "Kamu sudah check-in tadarus hari ini. Terima kasih!"
    else:
        connect.update_stats(user)
        message = "Check-in tadarus berhasil. Semangat tadarus!"
    
    await update.message.reply_text(text=message, parse_mode='Markdown')


async def cmd_mytadarus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        user = update.message.from_user.id
    elif update.callback_query:
        user = update.callback_query.from_user.id

    stats = connect.get_tadarus(user)

    message = f"Berikut runtutan harian tadarus kamu ☺️ :\n\n" \
              f"📖 Tadarus Harian: {stats['runtutan']} Hari\n" \
              f"📅 Tanggak Mulai: {stats['start_date']}\n\n" \
              f"Jangan lupa tadarus hari ini ya! Semangat tadarus! 💪🏼"
    
    keyboard = [[InlineKeyboardButton("Sudah Tadarus ✅", callback_data='checkin'),
                 InlineKeyboardButton("Stop Pengingat 🛑", callback_data='stop')],[
                 InlineKeyboardButton("Riwatat Tadarus 📖", callback_data='stats')]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    elif update.callback_query:
        await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')


async def cmd_stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = f"apakah kamu yakin ingin menghentikan pengingat tadarus?\n\n" \
               "Kamu bisa memulai lagi dengan menggunakan perintah /start"
    
    keyboard = [[InlineKeyboardButton("Ya", callback_data='yes'),
                 InlineKeyboardButton("Tidak", callback_data='no')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    elif update.callback_query:
        await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')


# Callback Handler ======================================================================================
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user = query.from_user.id

    if query.data == 'yes':
        connect.del_notif(user)
        message = "Pengingat tadarus kamu sudah dihentikan. Kamu bisa memulai lagi dengan menggunakan perintah /start"
        await query.edit_message_text(message, parse_mode='Markdown')
    
    
    elif query.data == 'no':
        message = "Pengingat tadarus kamu masih berjalan. Kamu bisa menghentikannya dengan menggunakan perintah /stop"
        await query.edit_message_text(message, parse_mode='Markdown')


    elif query.data == 'checkin':
        stats = connect.get_tadarus(user)
        if stats['rn_date'] == str(datetime.date.today()):
            message = "Kamu sudah check-in tadarus hari ini. Terima kasih!"
        else:
            connect.update_tadarus(user, str(datetime.date.today()))
            message = "Check-in tadarus berhasil. Semangat tadarus!"
        
        await query.edit_message_text(text=message, parse_mode='Markdown')


    elif query.data == 'stop':
        await query.answer()
        await cmd_stop(update, context)


    elif query.data == 'stats':
        history = connect.get_stats(user)
    
        message = f"Berikut Riwayat tadarus kamu Sebelumnya ☺️ :\n\n" \
                f"📖 Total Tadarus: {history['runtutan']} Hari\n" \
                f"📅 Tanggal Mulai: {history['start_date']}\n" \
                f"📅 Tanggal Terakhir: {history['last_date']}\n\n" \
                f"Jangan lupa tadarus hari ini ya! Semangat tadarus! 💪🏼"

        keyboard = [[InlineKeyboardButton("Reset Tadarus 🔄", callback_data='reset'),
                 InlineKeyboardButton("Kembali", callback_data='back')]]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')


    elif query.data == 'reset':
        connect.reset_stats(user)
        message = "Riwayat tadarus kamu sudah direset. Semangat tadarus!"
        await query.message.reply_text(message, parse_mode='Markdown')
    

    elif query.data == 'back':
        await query.answer()
        await cmd_mytadarus(update, context)


# Reminder Handler ======================================================================================
async def send_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    users = connect.get_user_notif()
    message = "Apakah kamu sudah tadarus hari ini ? 📖\n\n" \
  
    keyboard = [[InlineKeyboardButton("Sudah Tadarus ✅", callback_data='checkin')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    
    logging.info(f"Sending reminder")
    try:
        for user in users:
            if connect.get_tadarus(user)['rn_date'] != str(datetime.date.today()):
                await context.bot.send_message(chat_id=user, text=message, reply_markup=reply_markup, parse_mode='Markdown')
                logging.info(f"Reminder sent to user_id: {user}")
    except Exception as e:
        logging.error(f"Failed to send reminder to user_id: {user}, error: {e}")


def schedule_reminders(application: Application) -> None:
    job_queue = application.job_queue

    timezone = pytz.timezone('Asia/Jakarta')
    logging.info(f"Scheduling reminders")
    times = [
        datetime.time(hour=15, minute=27, tzinfo=timezone),
        datetime.time(hour=15, minute=30, tzinfo=timezone),
        # datetime.time(hour=14, minute=40, tzinfo=datetime.timezone.utc)
    ]

    for t in times:
        job_queue.run_daily(send_reminder, time=t)

    job_queue.run_once(send_reminder, when=60)


# Runtime App
def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()


    application.add_handler(CommandHandler('start', cmd_start))
    application.add_handler(CommandHandler('stop', cmd_stop))
    application.add_handler(CommandHandler('mytadarus', cmd_mytadarus))
    application.add_handler(CommandHandler('checkin', cmd_check_tadarus))
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


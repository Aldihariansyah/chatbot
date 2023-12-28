
import signal
import logging
import sys
import time
from datetime import datetime
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatAction
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters, CallbackQueryHandler, ConversationHandler
from dotenv import load_dotenv
import os
import mysql.connector
import random
import string

#menghubungkan dengan database
mydb = mysql.connector.connect(
    host ='localhost',
    user = 'root',
    password = '',
    database ='madani'
)

#cek apakah database sudah terhubung atau belum
# print (mydb)
sql = mydb.cursor()

# Load variabel dari file .env
load_dotenv()

# Mendapatkan nilai token dari variabel lingkungan
token = os.getenv('TOKEN')
queue = []
counter = 1
last_reset_time = datetime.now()  # Waktu terakhir reset


# Daftar jadwal praktik dokter


# Daftar pasien
patients = {}
# nomor antrian
registered_patients = {}

REGISTRATION_CHOICE = 1
def choose_registration_path(update: Update, context: CallbackContext):
    user = update.message.from_user
    context.user_data['registration_choice'] = None  # Inisialisasi pilihan pendaftaran  # Kirim pesan dengan opsi pendaftaran
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("UMUM", callback_data="UMUM")],
        [InlineKeyboardButton("BPJS", callback_data="BPJS")],
        [InlineKeyboardButton("UHC", callback_data="UHC")],
    ])
    update.message.reply_text("Jalur UMUM adalah Diperuntukan Untuk Masyarakat Umum.")
    update.message.reply_text("Jalur BPJS adalah Diperuntukan Untuk Masyarakat Yang Terdaftar Di Bpjs.")
    update.message.reply_text("Jalur UHC adalah Jalur Khusus Domisili Kota Pekanbaru.")
    update.message.reply_text("Silakan pilih jalur pendaftaran:", reply_markup=reply_markup)
    return REGISTRATION_CHOICE
BPJS_PATIENT_STATUS = 6
def registration_option(update: Update, context: CallbackContext):
    query = update.callback_query
    choice = query.data.replace("registration_option_", "")  # Dapatkan pilihan dari callback_data
    context.user_data['registration_choice'] = choice

    # Jika pengguna memilih "UMUM," alihkan ke langkah meminta foto surat rujukan
    if choice == "UMUM":
        query.message.reply_text("Terimakasih Telah Memilih Jalur umum, Silakan kirim foto Kartu Keluarga:\n\n Klik /selesai untuk mengakhiri pendaftaran dan kembali ke menu home")
        return SEND_KK_PHOTO

    # Jika pengguna memilih "BPJS," tanyakan apakah mereka pasien lama atau baru
    elif choice == "BPJS":
        query.message.reply_text("Apakah Anda pasien lama atau baru?\nPilih salah satu:\nketik '1' Jika Anda Pasien Lama\nKetik '2' Jika Anda Pasien Baru")
        query.message.reply_text("Klik /selesai untuk mengakhiri pendaftaran dan kembali ke menu home")
        return BPJS_PATIENT_STATUS
    
    elif choice == "UHC":
        query.message.reply_text("untuk jalur ini pasien harus mendaftar UHC di puskesmas terdekat, dan program ini hanya diperuntukan untuk warga berKTP Kota Pekanbaru")
        query.message.reply_text("Klik /start untuk menjalankan perintah lain")

    return ConversationHandler.END

SEND_REFERRAL_LETTER = 2
def send_referral_letter(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = update.message

    # Pastikan foto surat rujukan sudah dikirim
    if message.photo:
        # Simpan foto surat rujukan (ambil yang paling besar)
        referral_letter_photo = message.photo[-1].file_id
        context.user_data['referral_letter'] = referral_letter_photo

        # Kirim pesan untuk meminta foto KK
        update.message.reply_text("Foto surat kontrol berhasil diterima. Sekarang kirim Foto Bpjs Anda)")
        return SEND_BPJS_PHOTO  # Pindah ke langkah pengiriman foto KK

    else:
        update.message.reply_text("Anda harus mengirim foto surat rujukan. Silakan kirim lagi.")
        return SEND_REFERRAL_LETTER  # Tetap di langkah ini sampai foto surat rujukan diterima

SEND_KK_PHOTO = 5
def send_kk_photo(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = update.message

    # Pastikan foto KK sudah dikirim
    if message.photo:
        # Simpan foto KK (ambil yang paling besar)
        kk_photo = message.photo[-1].file_id
        context.user_data['kk_photo'] = kk_photo

        # Setelah mendapatkan kedua foto, lanjutkan ke langkah pemilihan spesialis
        update.message.reply_text("Foto Kartu Keluarga (KK) berhasil diterima. Silakan pilih spesialis:")
        return select_specialization(update, context)

    else:
        update.message.reply_text("Anda harus mengirim foto Kartu Keluarga (KK). Silakan kirim lagi.")
        return SEND_KK_PHOTO  # Tetap di langkah ini sampai foto KK diterima
    
SEND_BPJS_PHOTO = 3
def send_bpjs_photo(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = update.message


    if message.photo:
        
        bpjs_photo = message.photo[-1].file_id
        context.user_data['bpjs_photo'] = bpjs_photo
        print("File ID Foto BPJS:", bpjs_photo)
        # Kirim pesan untuk meminta foto KK
        update.message.reply_text("Foto BPJS berhasil diterima. Sekarang kirim foto KTP (Kartu Tanda Penduduk):")
        return SEND_KTP_PHOTO  # Pindah ke langkah pengiriman foto KK

    else:
        update.message.reply_text("Anda harus mengirim foto surat rujukan. Silakan kirim lagi.")
        return SEND_BPJS_PHOTO  
    
SEND_KTP_PHOTO = 4
def send_ktp_photo(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = update.message

    # Pastikan foto KK sudah dikirim
    if message.photo:
        # Simpan foto KK (ambil yang paling besar)
        ktp_photo = message.photo[-1].file_id
        context.user_data['ktp_photo'] = ktp_photo

        # Setelah mendapatkan kedua foto, lanjutkan ke langkah pemilihan spesialis
        update.message.reply_text("Foto KTP berhasil diterima. Silakan kirim Foto KK (Kartu Keluarga):")
        return SEND_KK_PHOTO

    else:
        update.message.reply_text("Anda harus mengirim foto Kartu Keluarga (KK). Silakan kirim lagi.")
        return SEND_KTP_PHOTO  # Tetap di langkah ini sampai foto KK diterima
    
def bpjs_patient_status(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = update.message.text

    if message == "1":
        # Pengguna adalah pasien lama, minta foto surat kontrol
        context.user_data['bpjs_patient_status'] = "lama"
        update.message.reply_text("Anda adalah pasien lama. Silakan kirim foto surat kontrol:")
        return SEND_REFERRAL_LETTER

    elif message == "2":
        # Pengguna adalah pasien baru, minta foto BPJS
        context.user_data['bpjs_patient_status'] = "baru"
        update.message.reply_text("Anda adalah pasien baru. Silakan kirim foto BPJS:")
        return SEND_BPJS_PHOTO

    else:
        update.message.reply_text("Mohon pilih opsi yang valid (1 untuk pasien lama, 2 untuk pasien baru).")
        return BPJS_PATIENT_STATUS


def get_specializations():
    sql.execute("SELECT DISTINCT specialization FROM doctor_schedule")
    result = sql.fetchall()
    return [specialization[0] for specialization in result]



# Fungsi untuk menampilkan pilihan spesialis kepada pengguna
def select_specialization(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    specializations = get_specializations()

    if not specializations:
        context.bot.send_message(chat_id=chat_id, text="Mohon maaf, belum ada jadwal dokter yang tersedia.")
        return

    keyboard = [[InlineKeyboardButton(specialization, callback_data=f"spesialis_{specialization.lower()}")]
                for specialization in specializations]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=chat_id, text="Silakan pilih spesialis:", reply_markup=reply_markup)



# Fungsi untuk mengambil data hari berdasarkan spesialis dari database



# Fungsi pendaftaran pasien
def start_registration(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    # Periksa apakah spesialis dan hari sudah dipilih oleh pengguna
    selected_specialization = context.user_data.get('selected_specialization')
    selected_day = context.user_data.get('selected_day')

    if not selected_specialization or not selected_day:
        context.bot.send_message(chat_id=chat_id, text="Anda harus memilih spesialis dan hari terlebih dahulu.")
        return

    context.bot.send_message(chat_id=chat_id, text="Silakan kirim data diri pendaftaran pasien dalam format berikut:\n\n"
                                                "Nama, NIK, Tgl Lahir, Alamat, Nomor telepon, Tanggal Kunjungan\n\n"
                                                "Contoh: John Doe, 1234567890123456, 30-10-2001, Jl. Raya No. 123, 08123456789, 01-08-2023\n\n"
                                                "~Note: 1.maksimal tanggal boking H-1~\n\n", parse_mode="Markdown")
                                                   



# Fungsi penanganan pemilihan spesialis
def select_specialization_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat_id
    specialization = query.data.replace("spesialis_", "")

    # Simpan spesialis yang dipilih ke dalam user_data
    context.user_data['selected_specialization'] = specialization

    # Dapatkan daftar hari berdasarkan spesialis yang dipilih
    available_days = get_available_days(specialization)  # Gantilah ini dengan fungsi yang sesuai

    if available_days:
        keyboard = [
            [InlineKeyboardButton(day, callback_data=f"day_{day.lower()}")]
            for day in available_days
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=chat_id, text="NOTE:Mendaftar Hanya diperuntukan Besok atau H-1 sebelum membuat janji dengan dokter")
        context.bot.send_message(chat_id=chat_id, text="Silakan pilih hari:", reply_markup=reply_markup)
    else:
        context.bot.send_message(chat_id=chat_id, text="Tidak ada jadwal yang tersedia untuk spesialis ini.")

def select_day_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat_id
    selected_day = query.data.replace("day_", "")

    # Simpan hari yang dipilih ke dalam user_data
    context.user_data['selected_day'] = selected_day

    # Dapatkan spesialisasi yang telah dipilih sebelumnya
    selected_specialization = context.user_data.get('selected_specialization')

    # Dapatkan daftar dokter yang tersedia berdasarkan spesialisasi dan hari yang dipilih
    available_doctors = get_available_doctors(selected_specialization, selected_day)  # Gantilah ini dengan fungsi yang sesuai

    if available_doctors:
        keyboard = [
            [InlineKeyboardButton(doctor, callback_data=f"doctor_{doctor.lower()}")]
            for doctor in available_doctors
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=chat_id, text="Silakan pilih dokter:", reply_markup=reply_markup)
    else:
        context.bot.send_message(chat_id=chat_id, text="Tidak ada dokter yang tersedia untuk spesialis ini pada hari yang dipilih.")

def get_available_days(specialization):

    # Contoh:
    sql.execute("SELECT DISTINCT day FROM doctor_schedule WHERE specialization = %s", (specialization,))
    result = sql.fetchall()
    
    # Mengembalikan daftar hari
    return [day[0] for day in result]

def get_available_doctors(specialization, day):
  
    sql.execute("SELECT DISTINCT nama_dokter FROM doctor_schedule WHERE specialization = %s AND day = %s", (specialization, day))
    result = sql.fetchall()

    # Mengembalikan daftar nama dokter
    return [doctor[0] for doctor in result]

def select_doctor_callback(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    selected_doctor = query.data.replace("doctor_", "")

    # Simpan dokter yang dipilih ke dalam user_data
    context.user_data['selected_doctor'] = selected_doctor

    # Dapatkan spesialisasi, hari, dan dokter yang telah dipilih sebelumnya
    selected_specialization = context.user_data.get('selected_specialization')
    selected_day = context.user_data.get('selected_day')

    # Dapatkan daftar sesi dari database atau sumber lain
    available_sessions = ["Sesi 1", "Sesi 2", "Sesi 3"]  # Gantilah ini dengan daftar sesi yang sesuai

    if available_sessions:
        keyboard = [
            [InlineKeyboardButton(session, callback_data=f"session_{session}")]
            for session in available_sessions
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=chat_id, text="Silakan pilih sesi kunjungan pada tombol dibawah ini:\n\nSesi 1 : 07:30-09:00\nSesi 2 : 09:00-11:30\nSesi 3 : 12:30-14:00", reply_markup=reply_markup)
    else:
        context.bot.send_message(chat_id=chat_id, text="Tidak ada sesi yang tersedia untuk dokter ini pada hari yang dipilih.")

def session_callback(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    selected_session = query.data.replace("session_", "")
    selected_doctor = context.user_data.get('selected_doctor')

    # Buat kunci sesi dan dokter
    session_key = f"{selected_session}_{selected_doctor}"

    if session_key in registered_patients and registered_patients[session_key] >= 3:
        context.bot.send_message(chat_id=chat_id, text="Maaf, sesi ini sudah penuh. Silakan pilih sesi lain atau dokter lain.")
        return

    # Jika sesi belum penuh, biarkan pengguna melanjutkan dengan pendaftaran
    context.user_data['selected_session'] = selected_session
    return start_registration(update, context)
    

    # Sisipkan logika lanjutan pendaftaran di sini, seperti mengirim pesan untuk memasukkan data diri pasien.



def get_available_hours(specialization, day, doctor):

    sql.execute("SELECT jam_awal, jam_akhir FROM doctor_schedule WHERE specialization = %s AND day = %s AND nama_dokter = %s",
                (specialization, day, doctor))
    result = sql.fetchone()

    # Mengembalikan tuple (jam_awal, jam_akhir)
    return result if result else (None, None)


def save_patient_to_database(patient_info, referral_letter, kk_photo, bpjs_photo, ktp_photo):
    # Query SQL untuk insert data pasien ke dalam tabel patient
    sql_query = "INSERT INTO patient (name, nik, address, tgl_lahir, phone, specialization, dokter, day, sesi, tanggal, booking_code, referral_letter, kk_photo, bpjs_photo, ktp_photo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    values = (
        patient_info["name"],
        patient_info["nik"],
        patient_info["address"],
        patient_info["tgl_lahir"],
        patient_info["phone"],
        patient_info["specialization"],
        patient_info["dokter"],  # Menyimpan nama dokter yang dipilih
        patient_info["day"],
        patient_info["sesi"],  # Kolom jam kunjungan
        patient_info["tanggal"],  # Kolom tanggal kunjungan
        patient_info["booking_code"],  # Kolom kode booking
        referral_letter,  # Foto surat rujukan
        kk_photo,
        bpjs_photo,
        ktp_photo
    )

    try:
        sql.execute(sql_query, values)
        mydb.commit()
        print("Data pasien dan foto berhasil disimpan ke database.")
    except Exception as e:
        mydb.rollback()
        print("Terjadi kesalahan saat menyimpan data pasien dan foto:", e)


def check_existing_data(specialization, day, sesi, tanggal_kunjungan):
    # Menggunakan koneksi database yang sudah ada (sql)
    sql.execute("SELECT COUNT(*) FROM patient WHERE specialization = %s AND day = %s AND sesi = %s AND tanggal = %s",
                (specialization, day, sesi, tanggal_kunjungan))
    
    result = sql.fetchone()
    count = result[0]
    
    if count > 0:
        return True  # Data sudah ada
    else:
        return False  # Data belum ada


def generate_booking_code():
    # Generate a random code using uppercase letters and digits
    characters = string.ascii_uppercase + string.digits
    booking_code = ''.join(random.choice(characters) for _ in range(6))  # You can adjust the length of the code
    return booking_code 

def handle_message(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = update.message

    # Memisahkan informasi pendaftaran dari pesan
    registration_data = message.text.split(', ')
    if len(registration_data) != 6:  # Hapus validasi jam, sehingga hanya 6 elemen
        context.bot.send_message(chat_id=chat_id, text="Maaf saya tidak mengerti apa yang anda maksud.\n"
                                 "Klik /selesai untuk mengakhiri pendaftaran")
        return

    name, nik, tgl_lahir, address, phone, tanggal_kunjungan = registration_data

    # Validasi format tanggal lahir (DD-MM-YYYY) dan tanggal kunjungan (DD-MM-YYYY)
    try:
        datetime.strptime(tgl_lahir, '%d-%m-%Y')
        tanggal_kunjungan_obj = datetime.strptime(tanggal_kunjungan, '%d-%m-%Y')  # Objek tanggal kunjungan
        tgl_lahir_mysql = datetime.strptime(tgl_lahir, '%d-%m-%Y').strftime('%Y-%m-%d')  # Konversi ke format MySQL
        tanggal_kunjungan_mysql = tanggal_kunjungan_obj.strftime('%Y-%m-%d')  # Konversi ke format MySQL
    except ValueError:
        context.bot.send_message(chat_id=chat_id, text="Format yang anda kirim salah, pastikan terdapat spasi setelah tanda koma [,].")
        return

    # Validasi tanggal kunjungan
    current_date = datetime.now().date()  # Objek datetime.date

    # Dapatkan tanggal besok
    tomorrow = current_date + timedelta(days=1)

    if tanggal_kunjungan_obj.date() != tomorrow:
        context.bot.send_message(chat_id=chat_id, text="Anda hanya dapat mendaftar untuk tanggal kunjungan besok.")
        return

    selected_specialization = context.user_data.get('selected_specialization')
    selected_day = context.user_data.get('selected_day')
    selected_session = context.user_data.get('selected_session')

    if not selected_specialization or not selected_day or not selected_session:
        context.bot.send_message(chat_id=chat_id, text="Anda harus memilih spesialis, hari, dan sesi terlebih dahulu.")
        return

    # Cek apakah hari kunjungan sesuai dengan hari yang dipilih sebelumnya
    if selected_day.lower() != get_day_name(tanggal_kunjungan_obj).lower():
        context.bot.send_message(chat_id=chat_id, text="Hari yang Anda pilih tidak sesuai dengan tanggal kunjungan yang Anda masukkan.")
        return

    # Cek apakah ada data kunjungan pada tanggal dan sesi tertentu dalam database
    existing_data = check_existing_data(selected_specialization, selected_day, tanggal_kunjungan_mysql, selected_session)

    if existing_data:
        context.bot.send_message(chat_id=chat_id, text="Maaf, data kunjungan pada tanggal dan sesi tersebut sudah ada dalam database. Silakan pilih tanggal dan sesi lain.")
        return
    
    # Set data pendaftaran pasien ke dalam user_data
    context.user_data['patient_info'] = {
        "name": name,
        "nik": nik,
        "address": address,
        "tgl_lahir": tgl_lahir_mysql,
        "phone": phone,
        "specialization": selected_specialization,
        "dokter": context.user_data['selected_doctor'],  # Menyimpan nama dokter yang dipilih
        "day": selected_day,
        "sesi": selected_session,
        "tanggal": tanggal_kunjungan_mysql,
        "booking_code": generate_booking_code()  # Generate a booking code
        }

    # Tampilkan konfirmasi dengan tombol inline
    confirmation_message = (
        f"Data pendaftaran:\n\n"
        f"Nama: {name}\n"
        f"NIK: {nik}\n"
        f"Tanggal Lahir: {tgl_lahir}\n"
        f"Alamat: {address}\n"
        f"Nomor Telepon: {phone}\n"
        f"Tanggal Kunjungan: {tanggal_kunjungan_mysql}\n"
        f"Spesialisasi: {selected_specialization}\n"
        f"Hari: {selected_day}\n"
        f"Jam: {selected_session}\n\n"
        f"Apakah data di atas sudah benar?\n"
        f"Klik tombol 'Ya' atau 'Tidak' di bawah ini."
    )

    keyboard = [
        [InlineKeyboardButton("Ya", callback_data="confirm_registration"),
         InlineKeyboardButton("Tidak", callback_data="cancel_registration")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(chat_id=chat_id, text=confirmation_message, reply_markup=reply_markup)



def get_day_name(date_obj):
    days = ["senin", "selasa", "rabu", "kamis", "jumat", "sabtu", "minggu"]
    return days[date_obj.weekday()]

def confirm_registration_callback(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    data = query.data

    if data == "confirm_registration":
        # Mengambil kembali patient_info dari context.user_data
        patient_info = context.user_data.get('patient_info')
        referral_letter = context.user_data.get('referral_letter')
        kk_photo = context.user_data.get('kk_photo')
        bpjs_photo = context.user_data.get('bpjs_photo')
        ktp_photo = context.user_data.get('ktp_photo')

        if patient_info:
            # Menambahkan satu ke jumlah pasien yang terdaftar untuk sesi dan dokter yang dipilih
            session_key = f"{patient_info['sesi']}_{patient_info['dokter']}"
            registered_patients[session_key] = registered_patients.get(session_key, 0) + 1

            save_patient_to_database(patient_info, referral_letter, kk_photo, bpjs_photo, ktp_photo)  # Simpan data ke database
            booking_code = patient_info["booking_code"]  # Mengambil kode booking dari patient_info
            context.bot.send_message(chat_id=chat_id, text=f"Pendaftaran berhasil! Kode booking Anda: {booking_code}")
            context.bot.send_message(chat_id=chat_id, text="Terimakasih telah mendaftar sebagai pasien kami.klik /start untuk kembali ke menu awal")
            context.bot.send_message(chat_id=chat_id, text=f"jika ingin membatalkan silahkan ketikan /batal (kode booking)")
        else:
            context.bot.send_message(chat_id=chat_id, text="Terjadi kesalahan saat memproses pendaftaran.")
    elif data == "cancel_registration":
        context.bot.send_message(chat_id=chat_id, text="Pendaftaran dibatalkan.")
    else:
        context.bot.send_message(chat_id=chat_id, text="Tombol tidak dikenali.")

    # Hapus pesan konfirmasi setelah tombol ditekan
    context.bot.delete_message(chat_id=chat_id, message_id=query.message.message_id)
    return ConversationHandler.END



def cancel_registration(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = update.message

    if len(message.text.split()) != 2:
        context.bot.send_message(chat_id=chat_id, text="Format penggunaan perintah salah. Gunakan /batal [Kode Booking].")
        return

    _, booking_code = message.text.split()

    # Cek keberadaan data kunjungan berdasarkan kode booking
    sql.execute("SELECT * FROM patient WHERE booking_code = %s", (booking_code,))
    result = sql.fetchone()

    if not result:
        context.bot.send_message(chat_id=chat_id, text="Tidak ada pendaftaran ditemukan dengan kode booking tersebut.")
        return

    # Hapus data kunjungan berdasarkan kode booking
    sql.execute("DELETE FROM patient WHERE booking_code = %s", (booking_code,))
    mydb.commit()

    context.bot.send_message(chat_id=chat_id, text="Pendaftaran dengan kode booking {} berhasil dibatalkan.".format(booking_code))
    start_bot(update, context)
def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("terimakasih")
    context.user_data.clear()
    start_bot(update, context)
    return ConversationHandler.END 

def view_schedule_by_booking_code(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = update.message

    if len(message.text.split()) != 2:
        context.bot.send_message(chat_id=chat_id, text="Format penggunaan perintah salah. Gunakan /Jadwal_Pasient [Kode Booking]\nContoh: /Jadwal_Pasient xxxxx.")
        return

    _, booking_code = message.text.split()

    # Cek keberadaan data kunjungan berdasarkan kode booking
    sql.execute("SELECT * FROM patient WHERE booking_code = %s", (booking_code,))
    result = sql.fetchone()

    if not result:
        context.bot.send_message(chat_id=chat_id, text="Tidak ada data kunjungan ditemukan dengan kode booking tersebut.")
        return

    specialization = result[6]
    sesi = result[10]
    day = result[8]
    name = result[1]
    dokter = result [7]


    # ...

    schedule_text = "Jadwal kunjungan dengan Kode Booking {}:\n\n".format(booking_code)
    schedule_text += "Nama Pasien : {}\n".format(name)
    schedule_text += "Nama Dokter: {}\n".format(dokter)
    schedule_text += "Spesialis: {}\n".format(specialization)
    schedule_text += "Hari: {}\n".format(day)
    schedule_text += "Jam: {}\n".format(sesi)
    schedule_text += "Tanggal: {}\n".format(result[9])  # Tanggal kunjungan

    context.bot.send_message(chat_id=chat_id, text=schedule_text)
    context.bot.send_message(chat_id=chat_id, text="Terimakasih telah menggunjungi Madanibot untuk meilhat jadawal pasient: \nKetik /start untuk kembali ke home")


def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Perintah tidak dikenali.")

def get_specialization_ids():
    sql.execute("SELECT DISTINCT id_spesialis FROM doctor_schedule")
    result = sql.fetchall()
    return [str(specialization_id[0]) for specialization_id in result]

def get_specialization_names():
    sql.execute("SELECT DISTINCT id_spesialis, specialization FROM doctor_schedule")
    result = sql.fetchall()
    return {str(specialization_id): specialization_name for specialization_id, specialization_name in result}

def show_specialization_id_buttons(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    specialization_ids = get_specialization_ids()
    specialization_names = get_specialization_names()

    if not specialization_ids:
        context.bot.send_message(chat_id=chat_id, text="Tidak ada ID spesialisasi yang tersedia.")
        return

    keyboard = [[InlineKeyboardButton(f"\u200B{id_}.{specialization_names[id_]}", callback_data=f"select_specialization_id_{id_}")]
            for id_ in specialization_ids]
    reply_markup = InlineKeyboardMarkup(keyboard, align="left")
    context.bot.send_message(chat_id=chat_id, text="Silakan pilih ID spesialisasi:", reply_markup=reply_markup)

def get_specialization_name_by_id(specialization_id):
    # Query database untuk mendapatkan nama spesialisasi berdasarkan ID
    sql.execute("SELECT specialization FROM doctor_schedule WHERE id_spesialis = %s", (specialization_id,))
    result = sql.fetchone()
    if result:
        return result[0]
    return "Spesialisasi tidak ditemukan"


def select_specialization_id_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    specialization_id = query.data.replace("select_specialization_id_", "")

    # Panggil fungsi untuk menampilkan data jadwal dokter berdasarkan ID spesialisasi
    show_selected_schedule_by_id(update, context, specialization_id)


# Fungsi untuk menampilkan jadwal dokter berdasarkan ID spesialisasi
def show_selected_schedule_by_id(update: Update, context: CallbackContext, specialization_id):
    chat_id = update.effective_chat.id

    # Query database untuk mendapatkan data jadwal dokter berdasarkan ID spesialisasi
    sql.execute("SELECT nama_dokter, day, jam_awal, jam_akhir FROM doctor_schedule WHERE id_spesialis = %s", (specialization_id,))
    result = sql.fetchall()

    if not result:
        context.bot.send_message(chat_id=chat_id, text="Tidak ada data jadwal dokter untuk ID spesialisasi tersebut.")
        return

    # Struktur data untuk menyimpan jadwal dokter
    doctor_schedules = {}

    # Proses hasil query
    for row in result:
        nama_dokter = row[0]
        day = row[1]
        jam_awal = row[2]
        jam_akhir = row[3]

        if (nama_dokter, day) not in doctor_schedules:
            doctor_schedules[(nama_dokter, day)] = []
        doctor_schedules[(nama_dokter, day)].append((jam_awal, jam_akhir))

    schedule_text = "Data jadwal dokter untuk ID spesialisasi {}:\n\n".format(specialization_id)

    # Format dan tampilkan jadwal dokter
    for (nama_dokter, day), jams in doctor_schedules.items():
        schedule_text += "Nama: {}\nHari: {}\n".format(nama_dokter, day)
        for jam_awal, jam_akhir in jams:
            schedule_text += "Jam: {} - {}\n".format(jam_awal, jam_akhir)
        schedule_text += "\n"

    context.bot.send_message(chat_id=chat_id, text=schedule_text)
    context.bot.send_message(chat_id=chat_id, text="Terimakasih telah mengunjungi Madanibot untuk melihat jadwal dokter. \nKetik /start untuk kembali ke home")



# Fungsi untuk mendapatkan informasi lokasi rumah sakit 
def get_hospital_location(update: Update, context):
    chat_id = update.effective_chat.id
    bot = context.bot

    # Mengirim foto
    with open('image/madani.jpeg', 'rb') as photo_file:
        bot.send_photo(chat_id=chat_id, photo=photo_file)
        
    context.bot.send_message(chat_id=chat_id, text="Lokasi rumah sakit: Jl. Garuda Sakti No.KM.2, Simpang Baru, Kec. Tampan, Kota Pekanbaru, Riau 28291 https://goo.gl/maps/2imn6EFfBuSLAu3M6")
    # Mengirim informasi lokasi rumah sakit
    
    #fungsi igd rumah sakit
def get_hospital_IGD(update: Update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text="Rumah Sakit Madani: Jl. Garuda Sakti No.KM.2,dengan mehubungi: \nTelepon : 0822-6969-6060 \nE-mail : rsd.madani.2018@gmail.com \nWebsite : https://rsdmadani.pekanbaru.go.id/ ")

# Memuat data registrasi saat bot pertama kali dijalankan

# Fungsi untuk memulai bot
def start_bot(update: Update, context):
    chat_id = update.effective_chat.id
    bot = context.bot
   
    
    # Mengirim foto
    with open('image/logo1.jpeg', 'rb') as photo_file:
        bot.send_photo(chat_id=chat_id, photo=photo_file)
        
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    user = update.effective_user
    name = user.first_name
    update.message.reply_text(f"Halo {name} selamat datang di layanan madanibot , saya adalah madanibot siap membantu anda untuk memberikan informasi: \n\nSilakan pilih perintah sesuai yang anda butuhkan:")
    update.message.reply_text("/Jadwal_Dokter : melihat jadwal dokter.")
    update.message.reply_text("/Pendaftaran : Buat Janji Dengan Dokter." )
    update.message.reply_text("/Jadwal_Pasient [kode booking] : Melihat jadwal pasient.")
    update.message.reply_text("/Lokasi : Mendapatkan Lokasi Rumah Sakit.")
    update.message.reply_text("/informasi_UGD : Informasi Mengenai UGD.")
    # Inisialisasi updater

# Fungsi penanganan KeyboardInterrupt
def stop_bot(signal, frame):
    print("Bot berhenti.")
    updater.stop()
    sys.exit(0)

# Menghubungkan penanganan KeyboardInterrupt ke fungsi stop_bot

def main():
    signal.signal(signal.SIGINT, stop_bot)

    updater = Updater(token=token, use_context=True)

    # Mendapatkan dispatcher dari updater
    dispatcher = updater.dispatcher
    
    conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler("start", start_bot),
        CommandHandler("Pendaftaran", choose_registration_path),
    ],
    states={
        REGISTRATION_CHOICE: [
            CallbackQueryHandler(registration_option, pattern='^UMUM$|^BPJS$|^UHC$'),
        ],
        SEND_REFERRAL_LETTER: [
            MessageHandler(Filters.photo, send_referral_letter),
        ],
        SEND_KK_PHOTO: [
            MessageHandler(Filters.photo, send_kk_photo),
        ],
        SEND_BPJS_PHOTO: [
            MessageHandler(Filters.photo, send_bpjs_photo),
        ],
        SEND_KTP_PHOTO: [
            MessageHandler(Filters.photo, send_ktp_photo),
        ],
        BPJS_PATIENT_STATUS: [
            MessageHandler(Filters.text, bpjs_patient_status),
        ],
        # Anda dapat menambahkan langkah-langkah lain sesuai kebutuhan Anda di sini
    },
    fallbacks=[CommandHandler('selesai', cancel)],    
    )

    # Menambahkan handler untuk perintah-perintah
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CommandHandler("Lokasi", get_hospital_location))
    dispatcher.add_handler(CommandHandler("Jadwal_Pasient", view_schedule_by_booking_code))
    dispatcher.add_handler(CommandHandler("Jadwal_Dokter", show_specialization_id_buttons))
    dispatcher.add_handler(CallbackQueryHandler(select_specialization_id_callback, pattern='^select_specialization_id_'))
    dispatcher.add_handler(CommandHandler("Informasi_UGD", get_hospital_IGD))
    dispatcher.add_handler(CommandHandler("Batal", cancel_registration))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_message))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))
    dispatcher.add_handler(CallbackQueryHandler(select_specialization_callback, pattern='^spesialis_'))
    dispatcher.add_handler(CallbackQueryHandler(select_day_callback, pattern='^day_'))
    dispatcher.add_handler(CallbackQueryHandler(select_doctor_callback, pattern='^doctor_'))
    dispatcher.add_handler(CallbackQueryHandler(session_callback, pattern='^session_'))
    dispatcher.add_handler(CallbackQueryHandler(confirm_registration_callback, pattern='^confirm_registration$|^cancel_registration$'))


    
    
    updater.start_polling()
    print ("sedang berjalan....")
    updater.idle()
    print("Bot berhenti.")

if __name__ == '__main__':
    main()
 
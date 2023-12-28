import mysql.connector
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, CallbackQueryHandler
import pandas as pd
from openpyxl import Workbook
import xlsxwriter
from io import BytesIO
from openpyxl.styles import Alignment
from datetime import datetime
import logging
from PIL import Image
import os


# Inisialisasi bot dengan token
updater = Updater(token='6131224960:AAGst_up8pD-ARFV1ppy1MTDsZY3KH3BV4k', use_context=True)
dispatcher = updater.dispatcher
# Membuat koneksi ke database MySQL
mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='madani'
)
sql = mydb.cursor()


LOGIN, AUTHENTICATED, INPUT_INFO, INPUT_TIME, UBAH_JADWAL_BY_NAME,UBAH_JADWAL,UBAH_JADWAL_BY_BOOKING, UBAH_JADWAL_PASIENT = range(8)

def login(update: Update, context: CallbackContext):
    update.message.reply_text("Silakan masukkan username admin:")
    return LOGIN

def authenticate_admin(update: Update, context: CallbackContext):
    user_input = update.message.text
    context.user_data['username'] = user_input  # Simpan username dalam user_data

    update.message.reply_text("Silakan masukkan password admin:")
    return AUTHENTICATED

def check_admin_credentials(update: Update, context: CallbackContext):
    admin_username = context.user_data.get('username')
    admin_password = update.message.text

    # Lakukan pengecekan dalam database untuk username dan password
    query = "SELECT username, password FROM admin WHERE username = %s AND password = %s"
    sql.execute(query, (admin_username, admin_password))
    result = sql.fetchone()

    if result:
        # Jika pasangan username dan password ditemukan dalam database
        username, password = result
        update.message.reply_text("Login berhasil sebagai admin.")
        context.user_data['admin_authenticated'] = True
        show_admin_menu(update, context)
        return ConversationHandler.END
    else:
        update.message.reply_text("Username atau password salah. Silakan coba lagi.")
        return LOGIN

    
def show_admin_menu(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("JADWAL DOKTER", callback_data="DOKTER")],
        [InlineKeyboardButton("JADWAL PASIENT", callback_data="PASIENT")],
        [InlineKeyboardButton("REKAP", callback_data="REKAP")],
        [InlineKeyboardButton("CREATE AKUN", callback_data="CREATE")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Selamat datang di Chatbot. Silakan pilih aksi yang ingin Anda lakukan:", reply_markup=reply_markup)

    
def handle_admin_actions(update: Update, context: CallbackContext):
    query = update.callback_query
    action = query.data

    if action == "DOKTER":
        query.message.reply_text("Selamat datang di manipulasi jadwal dokter \n/tambah_jadwal_dokter \n/update_jadwal_dokter \n/delete_jadwal_dokter")
        return INPUT_INFO
    elif action == "PASIENT":
        query.message.reply_text("Selamat datang di manipulasi jadwal pasient \n/update_jadwal_Pasien \n/delete_jadwal_Pasien")
        # Tambahkan logika untuk mengupdate jadwal dokter
        return INPUT_INFO
    elif action == "REKAP":
        query.message.reply_text("Anda memilih untuk \n/Rekap_Data_Pasient : merekap data pasien yang daftar \n /verifikasi_pasien:verifikasi pasien \n/data_pendaftar_harian: melihat data pasien sesuai tanggal")
        # Tambahkan logika untuk menghapus jadwal dokter
        return INPUT_INFO
    elif action == "CREATE":
        query.message.reply_text("Silahkan klik \n/Tambah_Akun untuk mendaftarkan admin baru.\n/delete_akun: untuk menghapus akun admin ")
        # Tambahkan logika untuk menghapus jadwal dokter



def tambah_jadwal_dokter(update: Update, context: CallbackContext):
    if context.user_data.get('admin_authenticated'):
        update.message.reply_text("Masukkan data jadwal dokter dalam format berikut:\n"
                                  "ID Spesialis, Nama Dokter, Spesialis, Hari, Jam Awal, Jam Akhir (Contoh: 1, Dr. John, SPESIALIS MATA, SENIN, 08:00, 10:00):")

        return INPUT_INFO
    else:
        update.message.reply_text("Anda harus login sebagai admin terlebih dahulu. Ketik /start untuk login.")
        return ConversationHandler.END  # Putuskan percakapan jika bukan super admin


def input_info(update: Update, context: CallbackContext):
    data_input = update.message.text

    try:
        # Membagi data input menjadi komponen-komponen yang sesuai
        id_spesialis, nama_dokter, specialization, day, jam_awal, jam_akhir = map(str.strip, data_input.split(','))

        # Menambahkan data jadwal dokter ke database
        query = "INSERT INTO doctor_schedule (id_spesialis, nama_dokter, specialization, day, jam_awal, jam_akhir) VALUES (%s, %s, %s, %s, %s, %s)"
        sql.execute(query, (id_spesialis, nama_dokter, specialization, day, jam_awal, jam_akhir))
        mydb.commit()

        update.message.reply_text(f"Data jadwal dokter telah berhasil ditambahkan ke database. \n klik /menu untuk kembali ke menu admin")
    except Exception as e:
        update.message.reply_text("Terjadi kesalahan: " + str(e))
    return ConversationHandler.END
    

UPDATE_JADWAL_DOKTER = range(7)
def update_jadwal_dokter(update: Update, context: CallbackContext):
    if context.user_data.get('admin_authenticated'):
        update.message.reply_text("Masukkan nama dokter dan hari dalam format berikut:\n"
                                  "Nama Dokter,Hari  (Contoh: Dr. John, SENIN):")

        return UBAH_JADWAL_BY_NAME
    else:
        update.message.reply_text("Anda harus login sebagai admin terlebih dahulu. Ketik /start untuk login.")

def ubah_jadwal_by_name(update: Update, context: CallbackContext):
    data_input = update.message.text

    try:
        nama_dokter, day = map(str.strip, data_input.split(','))

        # Simpan nama dokter dan hari dalam user_data untuk digunakan pada langkah selanjutnya
        context.user_data['nama_dokter'] = nama_dokter
        context.user_data['day'] = day

        update.message.reply_text(f"Masukkan data jadwal dokter yang baru dalam format berikut:\nNama Dokter, Day, Jam Awal, Jam Akhir (Contoh: Dr. John, Monday, 08:00, 10:00)")
        return UBAH_JADWAL
    except Exception as e:
        update.message.reply_text("Terjadi kesalahan: " + str(e))
        return ConversationHandler.END

def ubah_jadwal(update: Update, context: CallbackContext):
    data_input = update.message.text

    try:
        # Memisahkan data input menjadi nama dokter, hari, jam_awal_baru, dan jam_akhir_baru
        nama_dokter, day, jam_awal_baru, jam_akhir_baru = map(str.strip, data_input.split(','))

        # Menghubungkan ke database MySQL
        connection = mysql.connector.connect(
            host='localhost',
            database='madani',
            user='root',
            password=''
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Perbarui semua informasi dalam database
            query = "UPDATE doctor_schedule SET day = %s, jam_awal = %s, jam_akhir = %s WHERE nama_dokter = %s"
            values = (day, jam_awal_baru, jam_akhir_baru, nama_dokter)
            cursor.execute(query, values)

            connection.commit()
            cursor.close()
            connection.close()

            update.message.reply_text(f"Jadwal dokter {nama_dokter} pada hari {day} telah berhasil diperbarui.\n klik /menu untuk kembali ke menu admin")
        else:
            update.message.reply_text("Tidak dapat terhubung ke database MySQL.")
    except Exception as e:
        update.message.reply_text("Terjadi kesalahan dalam menghubungkan ke database MySQL atau dalam mengubah jadwal dokter.")

    # Bersihkan user_data setelah selesai
    context.user_data.clear()
    return ConversationHandler.END


HAPUS_JADWAL = range(8)
def delete_jadwal_dokter(update: Update, context: CallbackContext):
    if context.user_data.get('admin_authenticated'):
        update.message.reply_text("Masukkan nama dokter dan hari mana yang akan di hapus:\n"
                                  "Nama Dokter, Hari (Contoh: Dr. John, SENIN):")

        return HAPUS_JADWAL  
    else:
        update.message.reply_text("Anda harus login sebagai admin terlebih dahulu. Ketik /start untuk login.")
# Buat fungsi untuk menghapus jadwal dokter berdasarkan nama dan hari (day)
def hapus_jadwal(update: Update, context: CallbackContext):
    data_input = update.message.text

    try:
        nama_dokter, day = map(str.strip, data_input.split(','))

        # Menghapus data jadwal dokter berdasarkan nama dan hari
        query = "DELETE FROM doctor_schedule WHERE nama_dokter = %s AND day = %s"
        sql.execute(query, (nama_dokter, day))
        mydb.commit()

        update.message.reply_text(f"Data jadwal dokter {nama_dokter} pada hari {day} telah berhasil dihapus.\n klik /menu untuk kembali ke menu admin")
    except Exception as e:
        update.message.reply_text("Terjadi kesalahan: " + str(e))

    # Bersihkan user_data setelah selesai
    context.user_data.clear()
    return ConversationHandler.END


# Fase dalam proses konversasi
ENTER_BOOKING_CODE = 34
ENTER_NEW_DATA = 35  # Tambahkan state UPDATE_PASIEN
def update_pasien_by_booking(update: Update, context: CallbackContext):
    if context.user_data.get('admin_authenticated'):
        # Admin sudah terotentikasi, lanjutkan ke fungsi ini
        update.message.reply_text("Silakan masukkan kode booking pasien yang akan diupdate:")
        return ENTER_BOOKING_CODE
    else:
        update.message.reply_text("Anda harus login sebagai admin terlebih dahulu. Ketik /start untuk login.")
# Fungsi untuk memproses booking code
def enter_booking_code(update: Update, context: CallbackContext):
    booking_code = update.message.text
    context.user_data['booking_code'] = booking_code

    try:
        # Menghubungkan ke database MySQL
        connection = mysql.connector.connect(
            host='localhost',
            database='madani',
            user='root',
            password=''
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Mengeksekusi query untuk mengambil data pasien berdasarkan booking code
            query = "SELECT * FROM patient WHERE booking_code = %s"
            cursor.execute(query, (booking_code,))
            result = cursor.fetchone()

            if result:
                # Menampilkan data pasien kepada pengguna
                nama_pasien, nik_pasien, alamat, no_hp, tgl_lahir = result[1], result[2], result[3], result[4], result[5]
                response = (
                    f"Data pasien dengan booking code {booking_code}:\n"
                    f"Nama Pasien: {nama_pasien}\n"
                    f"NIK Pasien: {nik_pasien}\n"
                    f"Alamat: {alamat}\n"
                    f"Nomor Telepon: {no_hp}\n"
                    f"Tanggal Lahir: {tgl_lahir}"
                )
                update.message.reply_text(f"Ini adalah data pasien yang akan diperbarui:\n\n{response}\n\n"
                                      "Masukkan data pasien yang baru dalam format berikut:\n"
                                      "Nama, NIK, Alamat, Nomor Telepon, Tanggal Lahir (YYYY-MM-DD)")
            else:
                update.message.reply_text(f"Tidak ada data pasien dengan booking code {booking_code}.")

            cursor.close()
            connection.close()
        else:
            update.message.reply_text("Tidak dapat terhubung ke database MySQL.")
    except Exception as e:
        update.message.reply_text("Terjadi kesalahan dalam menghubungkan ke database MySQL atau dalam mengambil data pasien.")

    return ENTER_NEW_DATA

# Fungsi untuk mengubah data pasien dalam database MySQL
def enter_new_data(update: Update, context: CallbackContext):
    new_data = update.message.text
    booking_code = context.user_data['booking_code']

    try:
        # Memisahkan data input menjadi nama pasien dan NIK pasien
        nama_pasien, nik_pasien, alamat, no_hp, tgl_lahir = map(str.strip, new_data.split(','))

        # Menghubungkan ke database MySQL
        connection = mysql.connector.connect(
            host='localhost',
            database='madani',
            user='root',
            password=''
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Mengubah data pasien dalam database MySQL
            query = "UPDATE patient SET name = %s, nik = %s, address = %s, phone = %s, tgl_lahir = %s WHERE booking_code = %s"
            values = (nama_pasien, nik_pasien, alamat, no_hp, tgl_lahir,  booking_code)
            cursor.execute(query, values)

            connection.commit()
            cursor.close()
            connection.close()

            update.message.reply_text(f"Data pasien dengan booking code {booking_code} telah diubah.\n klik /menu untuk kembali ke menu admin")
            return ConversationHandler.END
    except Exception as e:
        update.message.reply_text("Terjadi kesalahan dalam menghubungkan ke database MySQL atau dalam mengubah data pasien.")
    context.user_data.clear()

HAPUS_JADWAL_PASIEN = range(9)
def delete_jadwal_pasien(update: Update, context: CallbackContext):
    if context.user_data.get('admin_authenticated'):
        update.message.reply_text("Masukkan booking code pasien yang akan dihapus:")
        return HAPUS_JADWAL_PASIEN
    else:
        update.message.reply_text("Anda harus login sebagai admin terlebih dahulu. Ketik /start untuk login.")

# Fungsi untuk menghapus jadwal pasien dari database berdasarkan booking code
def hapus_jadwal_pasien(update: Update, context: CallbackContext):
    booking_code = update.message.text

    try:
        # Menghapus data jadwal pasien berdasarkan booking code
        query = "DELETE FROM patient WHERE booking_code = %s"
        sql.execute(query, (booking_code,))
        mydb.commit()

        update.message.reply_text(f"Data jadwal pasien dengan booking code {booking_code} telah berhasil dihapus.\n klik /menu untuk kembali ke menu admin")
        return ConversationHandler.END
    except Exception as e:
        update.message.reply_text("Terjadi kesalahan: " + str(e))

    # Bersihkan user_data setelah selesai
    context.user_data.clear()
    

# Handler untuk perintah /daftar_pasien_tanggal
def Rekap_Data_Pasient(update: Update, context: CallbackContext):
    if context.user_data.get('admin_authenticated'):
        update.message.reply_text("Masukkan tanggal awal (format: YYYY-MM-DD):")
        return INPUT_TIME
    else:
        update.message.reply_text("Anda harus login sebagai admin terlebih dahulu. Ketik /start untuk login.")

# Handler untuk memproses tanggal awal yang dimasukkan
def input_time(update: Update, context: CallbackContext):
    context.user_data['tanggal_awal'] = update.message.text
    update.message.reply_text("Masukkan tanggal akhir (format: YYYY-MM-DD):")
    return UBAH_JADWAL_PASIENT  # Ganti state ini sesuai dengan state yang sesuai

# Handler untuk memproses tanggal akhir yang dimasukkan
# Handler untuk memproses tanggal akhir yang dimasukkan
def rekap_jadwal_pasien(update: Update, context: CallbackContext):
    tanggal_awal = context.user_data.get('tanggal_awal')
    tanggal_akhir = update.message.text

    try:
        # Query the database to get patient data within the specified date range and with 'verif' set to True
        query = "SELECT name, nik, address, DATE_FORMAT(tgl_lahir, '%d-%m-%Y'), phone, specialization, dokter, day, DATE_FORMAT(tanggal, '%d-%m-%Y'), sesi FROM patient WHERE tanggal BETWEEN %s AND %s AND verif = TRUE"
        sql.execute(query, (tanggal_awal, tanggal_akhir, ))
        results = sql.fetchall()

        if results:
            # Create an Excel file with patient data and column headers
            output = BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet()

            # Column headers
            columns = ['Nama Pasien', 'NIK', 'Alamat', 'Tanggal Lahir', 'Nomor Telepon', 'Spesialisasi', 'Dokter', 'Hari', 'Tanggal', 'Sesi']
            for col_num, col_name in enumerate(columns):
                worksheet.write(0, col_num, col_name)

            # Write patient data to the Excel file
            for row_num, data_pasien in enumerate(results, start=1):
                for col_num, data in enumerate(data_pasien):
                    if col_num == 9:  # Assuming 'sesi' column is at index 9
                        # Change the column index to match the 'sesi' column
                        worksheet.write(row_num, col_num, data)
                    else:
                        worksheet.write(row_num, col_num, data)

            workbook.close()
            output.seek(0)

            # Send the Excel file to the user
            update.message.reply_document(document=output, filename='daftar_pasien.xlsx')
            update.message.reply_text(f"klik /menu untuk kembali ke menu admin")
        else:
            update.message.reply_text("Tidak ada pasien yang mendaftar dalam rentang tanggal tersebut atau data pasien belum diverifikasi.")
    except Exception as e:
        update.message.reply_text("Terjadi kesalahan: " + str(e))

    # Clear user_data after finishing
    context.user_data.clear()
    return ConversationHandler.END


KONFIRMASI_VERIFIKASI, TAMPILKAN_DATA_PASIEN = range(9, 11)
def verifikasi_pasien(update: Update, context: CallbackContext):
    if context.user_data.get('admin_authenticated'):
        update.message.reply_text("Masukkan kode booking pasien yang akan diverifikasi:")
        return TAMPILKAN_DATA_PASIEN
    else:
        update.message.reply_text("Anda harus login sebagai admin terlebih dahulu. Ketik /start untuk login.")

def tampilkan_data_pasien(update: Update, context: CallbackContext):
    booking_code = update.message.text

    try:
        # Menghubungkan ke database MySQL
        connection = mysql.connector.connect(
            host='localhost',
            database='madani',
            user='root',
            password=''
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Mengeksekusi query untuk mengambil data pasien berdasarkan booking code
            query = "SELECT * FROM patient WHERE booking_code = %s"
            cursor.execute(query, (booking_code,))
            result = cursor.fetchone()

            if result:
                # Menampilkan data pasien kepada pengguna
                nama_pasien, nik_pasien, alamat, no_hp, tgl_lahir = result[1], result[2], result[3], result[4], result[5]
                response = (
                    f"Data pasien dengan booking code {booking_code}:\n"
                    f"Nama Pasien: {nama_pasien}\n"
                    f"NIK Pasien: {nik_pasien}\n"
                    f"Alamat: {alamat}\n"
                    f"Nomor Telepon: {no_hp}\n"
                    f"Tanggal Lahir: {tgl_lahir}"
                )
                update.message.reply_text(response)
                
                # Tanyakan konfirmasi verifikasi kepada admin
                update.message.reply_text("Apakah Anda ingin mengonfirmasi verifikasi pasien ini? (Ya/Tidak)")
                
                context.user_data['booking_code'] = booking_code  # Simpan kode booking dalam user_data
                return KONFIRMASI_VERIFIKASI
            else:
                update.message.reply_text(f"Tidak ada data pasien dengan booking code {booking_code}.")

            cursor.close()
            connection.close()
        else:
            update.message.reply_text("Tidak dapat terhubung ke database MySQL.")
    except Exception as e:
        update.message.reply_text("Terjadi kesalahan dalam menghubungkan ke database MySQL atau dalam mengambil data pasien.")
    return ConversationHandler.END

def konfirmasi_verifikasi(update: Update, context: CallbackContext):
    user_input = update.message.text.lower()

    if user_input == 'ya':
        booking_code = context.user_data.get('booking_code')
        
        try:
            # Menghubungkan ke database MySQL
            connection = mysql.connector.connect(
                host='localhost',
                database='madani',
                user='root',
                password=''
            )

            if connection.is_connected():
                cursor = connection.cursor()

                # Mengeksekusi query untuk mengubah kolom 'verif' menjadi True
                query = "UPDATE patient SET verif = TRUE WHERE booking_code = %s"
                cursor.execute(query, (booking_code,))
                connection.commit()

                # Periksa apakah ada baris yang terpengaruh (data ditemukan)
                if cursor.rowcount > 0:
                    update.message.reply_text(f"Verifikasi pasien dengan booking code {booking_code} berhasil.")
                else:
                    update.message.reply_text(f"Tidak ada pasien dengan booking code {booking_code} yang ditemukan.")

                cursor.close()
                connection.close()
            else:
                update.message.reply_text("Tidak dapat terhubung ke database MySQL.")
        except Exception as e:
            update.message.reply_text("Terjadi kesalahan dalam menghubungkan ke database MySQL atau dalam verifikasi pasien.")
            return ConversationHandler.END
    else:
        update.message.reply_text("Verifikasi pasien dibatalkan.")
    return ConversationHandler.END
ADD_ADMIN_INFO = range(20)
def add_admin(update: Update, context: CallbackContext):
    if context.user_data.get('admin_authenticated'):
        update.message.reply_text("Masukkan data admin dalam format berikut:\n"
                                  "Nama, Phone, Username, Password:")
        return ADD_ADMIN_INFO
    else:
        update.message.reply_text("Hanya admin yang dapat menambahkan admin. silahkan klik /start untuk login")
        return ConversationHandler.END

def add_admin_info(update: Update, context: CallbackContext):
    data_input = update.message.text

    try:
        nama, phone, username, password = map(str.strip, data_input.split(','))

        # Masukkan data admin ke dalam tabel admin (tanpa kolom super_admin)
        query = "INSERT INTO admin (nama, phone, username, password) VALUES (%s, %s, %s, %s)"
        sql.execute(query, (nama, phone, username, password))
        mydb.commit()  # Commit transaksi

        update.message.reply_text(f"Admin dengan username {username} telah berhasil ditambahkan ke dalam database.klik /menu untuk kembali ke menu admin")
    except Exception as e:
        update.message.reply_text("Terjadi kesalahan: " + str(e))
    finally:
        sql.close()  # Tutup kursor
    return ConversationHandler.END

CONFIRM_DELETE_ADMIN_BY_NAME = range(50, 51)  # Gunakan range yang belum digunakan

def delete_admin_by_name(update: Update, context: CallbackContext):
    if context.user_data.get('admin_authenticated'):
        update.message.reply_text("Masukkan nama admin yang akan dihapus:")
        return CONFIRM_DELETE_ADMIN_BY_NAME
    else:
        update.message.reply_text("Anda harus login sebagai admin terlebih dahulu. Ketik /start untuk login.")

def confirm_delete_admin_by_name(update: Update, context: CallbackContext):
    admin_name = update.message.text

    try:
        # Menghubungkan ke database MySQL
        connection = mysql.connector.connect(
            host='localhost',
            database='madani',
            user='root',
            password=''
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Mengeksekusi query untuk menghapus admin berdasarkan nama
            query = "DELETE FROM admin WHERE nama = %s"
            cursor.execute(query, (admin_name,))
            connection.commit()

            update.message.reply_text(f"Data admin dengan nama {admin_name} telah berhasil dihapus. klik /menu untuk kembali ke menu admin")
        else:
            update.message.reply_text("Tidak dapat terhubung ke database MySQL.")
    except Exception as e:
        update.message.reply_text("Terjadi kesalahan: " + str(e))
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    # Bersihkan user_data setelah selesai
    context.user_data.clear()
    return ConversationHandler.END
 
REKAP_PASIEN_TANGGAL= range(11) 
def rekap_pasien_tanggal(update: Update, context: CallbackContext):
    if context.user_data.get('admin_authenticated'):
        update.message.reply_text("Masukkan tanggal (format: YYYY-MM-DD):")
        return REKAP_PASIEN_TANGGAL
    else:
        update.message.reply_text("Anda harus login sebagai admin terlebih dahulu. Ketik /start untuk login.")
       

def input_tanggal(update: Update, context: CallbackContext):
    context.user_data['tanggal'] = update.message.text
    tanggal = context.user_data['tanggal']

    try:
        # Query the database to get patient data within the specified date and with 'verif' set to True
        query = "SELECT name, nik, address, DATE_FORMAT(tgl_lahir, '%d-%m-%Y'), phone, specialization, dokter, day, DATE_FORMAT(tanggal, '%d-%m-%Y'), " \
                "referral_letter, kk_photo, bpjs_photo, ktp_photo FROM patient WHERE tanggal = %s "
        sql.execute(query, (tanggal,))
        results = sql.fetchall()

        if results:
            for patient_data in results:
                name, nik, address, dob, phone, specialization, dokter, day, appointment_date, referral_letter, kk_photo, bpjs_photo, ktp_photo = patient_data

                # Send patient data
                response = (
                    f"Nama Pasien: {name}\n"
                    f"NIK: {nik}\n"
                    f"Alamat: {address}\n"
                    f"Tanggal Lahir: {dob}\n"
                    f"Nomor Telepon: {phone}\n"
                    f"Spesialisasi: {specialization}\n"
                    f"Dokter: {dokter}\n"
                    f"Hari: {day}\n"
                    f"Tanggal: {appointment_date}\n"
                    
                )

                # Send referral letter image
                send_image(update, context, referral_letter, f"{nik}_referral_letter.jpg")

                # Send KK photo image
                send_image(update, context, kk_photo, f"{nik}_kk_photo.jpg")

                # Send BPJS photo image
                send_image(update, context, bpjs_photo, f"{nik}_bpjs_photo.jpg")

                # Send KTP photo image
                send_image(update, context, ktp_photo, f"{nik}_ktp_photo.jpg")

                update.message.reply_text(response)
                update.message.reply_text("klik /menu untuk kembali ke menu admin")
                return ConversationHandler.END

        else:
            update.message.reply_text("Tidak ada pasien yang mendaftar pada tanggal tersebut atau data pasien belum diverifikasi.")
            
    except Exception as e:
        update.message.reply_text(" ")
        return ConversationHandler.END

# Helper function to send an image
# Fungsi pembantu untuk mengirim gambar
def send_image(update, context, image_data, filename):
    if image_data is not None:
        # Simpan gambar ke file sementara
        with open(filename, 'wb') as file:
            file.write(image_data)

        # Kirim gambar sebagai foto
        update.message.reply_photo(photo=open(filename, 'rb'))

        # Hapus file sementara
        os.remove(filename)
        return ConversationHandler.END
    else:
        update.message.reply_text(" ")
    return ConversationHandler.END



def unknown(update: Update, context: CallbackContext):
    update.message.reply_text("Maaf, saya tidak mengerti pesan Anda. Ketik /start untuk memulai atau gunakan perintah yang valid.")

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("Percakapan dibatalkan.")
    context.user_data.clear()
    return ConversationHandler.END


def main():
    updater.start_polling()
    updater.idle()
    # Menutup koneksi ke database
    mydb.close()

if __name__ == "__main__":
    conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler('start', login),
        CommandHandler('tambah_jadwal_dokter', tambah_jadwal_dokter),  # Tambahkan perintah tambah data jadwal dokter
        CommandHandler('update_jadwal_dokter', update_jadwal_dokter),
        CommandHandler('delete_jadwal_dokter', delete_jadwal_dokter),
        CommandHandler('update_jadwal_pasien', update_pasien_by_booking),
        CommandHandler('delete_jadwal_pasien', delete_jadwal_pasien),
        CommandHandler('Rekap_Data_Pasien', Rekap_Data_Pasient),
        CommandHandler('verifikasi_pasien', verifikasi_pasien),
        CommandHandler('data_pendaftar_harian', rekap_pasien_tanggal),
        CommandHandler('Tambah_Akun', add_admin),
        CommandHandler('Delete_Akun', delete_admin_by_name),
        CommandHandler('Menu', show_admin_menu),
        # CommandHandler('verifikasi_pasien', verifikasi_pasien),  # Menambahkan perintah verifikasi pasien


    ],
    states={
        LOGIN: [MessageHandler(Filters.text & ~Filters.command, authenticate_admin)],
        AUTHENTICATED: [MessageHandler(Filters.text & ~Filters.command, check_admin_credentials)],
        HAPUS_JADWAL: [MessageHandler(Filters.text & ~Filters.command, hapus_jadwal)],
        INPUT_INFO: [MessageHandler(Filters.text & ~Filters.command, input_info)],
        UPDATE_JADWAL_DOKTER: [MessageHandler(Filters.text & ~Filters.command, update_jadwal_dokter)],
        UBAH_JADWAL_BY_NAME: [MessageHandler(Filters.text & ~Filters.command, ubah_jadwal_by_name)],
        UBAH_JADWAL: [MessageHandler(Filters.text & ~Filters.command, ubah_jadwal)],
        ENTER_BOOKING_CODE: [MessageHandler(Filters.text & ~Filters.command, enter_booking_code)],
        ENTER_NEW_DATA: [MessageHandler(Filters.text & ~Filters.command, enter_new_data)],
        HAPUS_JADWAL_PASIEN: [MessageHandler(Filters.text & ~Filters.command, hapus_jadwal_pasien)],
        UBAH_JADWAL_PASIENT: [MessageHandler(Filters.text & ~Filters.command, rekap_jadwal_pasien)],
        INPUT_TIME: [MessageHandler(Filters.text & ~Filters.command, input_time)],
        KONFIRMASI_VERIFIKASI: [MessageHandler(Filters.text & ~Filters.command, konfirmasi_verifikasi)],
        TAMPILKAN_DATA_PASIEN: [MessageHandler(Filters.text & ~Filters.command, tampilkan_data_pasien)],
        REKAP_PASIEN_TANGGAL: [MessageHandler(Filters.text & ~Filters.command, input_tanggal)],
        ADD_ADMIN_INFO: [MessageHandler(Filters.text & ~Filters.command, add_admin_info)],
        CONFIRM_DELETE_ADMIN_BY_NAME: [MessageHandler(Filters.text & ~Filters.command, confirm_delete_admin_by_name)],


       

        # Menambahkan state VERIFIKASI_PASIEN

    },
    fallbacks=[CommandHandler('cancel', cancel)],)
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CallbackQueryHandler(handle_admin_actions))
    unknown_handler = MessageHandler(Filters.text & ~Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    
    main()
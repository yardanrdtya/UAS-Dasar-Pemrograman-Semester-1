import time
import os
import json
import sys
import pwinput
import re
from datetime import datetime

os.system("cls")

# File untuk menyimpan data akun dan barang
USERS_FILE = "user.json"
ITEMS_FILE = "item.json"

# Fungsi untuk memuat data dari file JSON
def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return json.load(file)
    return {}

# Fungsi untuk menyimpan data ke file JSON
def save_json(data, file_path):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

# Memuat data akun dan item dari file JSON
accounts = load_json(USERS_FILE).get("accounts", {})
data_items = load_json(ITEMS_FILE)
items = data_items.get("items", {})
vouchers = data_items.get("vouchers", {})

# Fungsi menampilkan item yang berbeda berdasarkan waktu
def get_time_period():
    waktu_sekarang = time.localtime().tm_hour
    if 6 <= waktu_sekarang < 12:
        return "pagi"
    elif 12 <= waktu_sekarang < 18:
        return "siang"
    else:
        return "malam"

# Fungsi Login
def login():
    for attempt in range(3):
        try:
            username = input("Masukkan Username: ")
            password = pwinput.pwinput("Masukkan Password: ")
            account = accounts.get(username)

            if account and not account["locked"]:
                if account["password"] == password:
                    print("------------------------------------------------")
                    print(f"Login Berhasil! Anda masuk sebagai Member {account['role']}")
                    print("------------------------------------------------")
                    return account
                else:
                    print("------------------------------------------------")
                    print("Password salah! Silahkan coba lagi.")
                    print("------------------------------------------------")
                    account["attempts"] += 1
            else:
                print("------------------------------------------------")
                print("Username akun tidak ditemukan!")
                print("------------------------------------------------")

            if account and account["attempts"] >= 3:
                account["locked"] = True
                print("Login gagal! Anda telah mencapai batas percobaan login.")
                save_json({"accounts": accounts}, USERS_FILE)
        except KeyboardInterrupt:
            print("\n-> Terjadi kesalahan input! Kembali ke menu login.")
            return None
    return None

# Fungsi Daftar Akun
def daftar_akun():
    print("\n|==============================================|")
    print("|                Daftar Akun Baru              |")
    print("|==============================================|")
    while True:
        try:
            username = input("Masukkan Username baru: ")
            if username == "":
                print("-> Username harus diisi! Silahkan coba lagi.")
                continue
            elif username in accounts:
                print("-> Username sudah digunakan. Silakan coba lagi.")
            else:
                break
        except KeyboardInterrupt:
            print("\n-> Terjadi kesalahan input! Kembali ke menu login.")
            return None

    while True:
        try:
            password = pwinput.pwinput("Masukkan Password baru: ")
            if password == "":
                print("-> Password harus diisi! Silahkan coba lagi.")
                continue
            if not re.match(r'^(?=.*[a-zA-Z])(?=.*\d)', password):  # Password harus ada angka dan hurufnya
                print("-> Password harus diisi menggunakan angka dan huruf.")
                continue

            break
        except KeyboardInterrupt:
            print("\nTerjadi kesalahan input! Program telah dihentikan.")
            sys.exit(0)

    while True:
        try:
            role = input("Pilih role (Biasa/VIP): ").strip()
            if role == "Biasa" or role == "VIP":
                break
            else:
                print("Role tidak valid. Pilih antara 'Biasa' atau 'VIP'.")
        except KeyboardInterrupt:
            print("\n-> Terjadi kesalahan input! Kembali ke menu login.")
            return None

    # Tambahkan gold dan gems ke akun
    gems = 100  # Gems awal untuk setiap akun baru
    gold = 5000  # Gold awal untuk setiap akun baru

    accounts[username] = {"password": password, "role": role, "locked": False, "attempts": 0, "gems": gems, "gold": gold}
    save_json({"accounts": accounts}, USERS_FILE)
    print("------------------------------------------------")
    print("Akun berhasil didaftarkan!")
    print("------------------------------------------------")

from prettytable import PrettyTable

# Fungsi untuk menampilkan item
def lihat_item(role):
    period = get_time_period()
    print(f"\nItem yang tersedia {period} ini:")

    table = PrettyTable()
    table.field_names = ["No.", "Item", "Harga Gold", "Harga Gems"]

    item_tersedia = items[period][role]
    for i, (item, prices) in enumerate(item_tersedia.items(), 1):
        table.add_row([i, item, prices["gold"], prices["gems"]])

    print(table)  # Menampilkan tabel

# Fungsi untuk membeli item
def beli_item(account, role, balance, gems):
    period = get_time_period()
    item_tersedia = items.get(period, {}).get(role, {})

    if not item_tersedia:
        print("Tidak ada item yang tersedia saat ini.")
        return account["gold"], account["gems"]

    # Menampilkan daftar item
    table = PrettyTable()
    table.field_names = ["No.", "Item", "Harga Gold", "Harga Gems"]
    for i, (item, prices) in enumerate(item_tersedia.items(), 1):
        table.add_row([i, item, prices["gold"], prices["gems"]])

    print("\nPilih item yang ingin dibeli:")
    print(table)
    while True:
        try:
            # Memilih item
            pilihan = int(input("Masukkan nomor item: ")) - 1
            if pilihan < 0 or pilihan >= len(item_tersedia):
                raise ValueError("Pilihan item tidak valid.")

            nama_item = list(item_tersedia.keys())[pilihan]
            harga_item_gold = list(item_tersedia.values())[pilihan]["gold"]
            harga_item_gems = list(item_tersedia.values())[pilihan]["gems"]

            # Fungsi diskon voucher
            diskon = 0
            while True:
                try:
                    gunakan_voucher = input("Gunakan voucher? (ya/tidak): ").strip().lower()
                    if gunakan_voucher == "ya":
                        while True:
                            kode_voucher = input("Masukkan kode voucher: ").strip()
                            if kode_voucher:
                                diskon, valid = terapkan_voucher(kode_voucher)
                                if valid:
                                    print(f"-> Voucher diterima. Diskon: {diskon}.")
                                    break
                                else:
                                    print("-> Pembayaran telah dibatalkan.")
                                    return account["gold"], account["gems"]
                            else:
                                print("-> Kode voucher harus diisi! Silahkan coba lagi")
                        break
                    elif gunakan_voucher == "tidak":
                        break
                    else:
                        print("-> Input tidak valid! Masukkan 'ya' atau 'tidak'.")
                except KeyboardInterrupt:
                    print("\n-> Terjadi kesalahan input! Kembali ke menu utama.")
                    return account["gold"], account["gems"] 

            # Pilih metode pembayaran (Gold atau Gems)
            while True:
                try:
                    metode_pembayaran = input(f"Pilih metode pembayaran untuk {nama_item}: [1] Gold, [2] Gems: ").strip()
                    if metode_pembayaran == "1":
                        harga_akhir = max(0, harga_item_gold - diskon)  # Harga tidak boleh negatif
                        print(f"-> Harga akhir item sebesar: {harga_akhir} Gold.")
                        if harga_akhir <= account["gold"]:
                            account["gold"] -= harga_akhir
                            print("-------------------------------------------------------------------------")
                            print(f"Pembelian Berhasil! Anda membeli {nama_item} seharga {harga_akhir} Gold.")
                            print("-------------------------------------------------------------------------")
                            print(f"-> Sisa saldo anda: {account["gold"]} Gold")

                            # Menandakan voucher hanya bisa dipakai sekali saja
                            if diskon > 0:
                                voucher = vouchers.get(kode_voucher)
                                if voucher:
                                    voucher["valid"] = False
                                    save_json({"vouchers": vouchers, "items": data_items["items"]}, ITEMS_FILE)

                        else:
                            print("-> Gold anda tidak cukup untuk membeli item ini.")
                            
                    elif metode_pembayaran == "2":
                        harga_akhir = max(0, harga_item_gems - diskon)  # Harga tidak boleh negatif
                        print(f"-> Harga akhir item sebesar: {harga_akhir} Gems.")
                        if harga_akhir <= account["gems"]:
                            account["gems"] -= harga_akhir
                            print("--------------------------------------------------------------")
                            print(f"Pembelian berhasil! Anda membeli {nama_item} seharga {harga_akhir} Gems.")
                            print("--------------------------------------------------------------")
                            print(f"-> Sisa gems anda: {account["gems"]} Gems")

                            # Menandakan voucher hanya bisa dipakai sekali saja
                            if diskon > 0:
                                voucher = vouchers.get(kode_voucher)
                                if voucher:
                                    voucher["valid"] = False
                                    save_json({"vouchers": vouchers, "items": data_items["items"]}, ITEMS_FILE)

                        else:
                            print("-> Gems anda tidak cukup untuk membeli item ini.")
                            
                    else:
                        print("-> Metode pembayaran tidak valid! Silahkan pilih [1] Gold atau [2] Gems.")
                        continue

                    # Simpan perubahan
                    save_json({"accounts": accounts}, USERS_FILE)
                    break
                except KeyboardInterrupt:
                    print("\n-> Terjadi kesalahan input! Kembali ke menu utama.")
                    break

            break # Keluar dari loop pembelian setelah berhasil

        except ValueError:
            print("-> Input tidak valid. Harap pilih nomor item yang tersedia.")
        except KeyboardInterrupt:
            print("\n-> Terjadi kesalahan input! Kembali ke menu utama.")
            break
        except Exception as e:
            print(f"Terjadi kesalahan: {e}")

    # # Perbarui data akun
    # account["gems"] = gems
    # account["gold"] = balance
    # save_json({"accounts": accounts}, USERS_FILE)
    return account["gold"], account["gems"]

# Fungsi menerapkan voucher
def terapkan_voucher(voucher_code):
    voucher = vouchers.get(voucher_code)
    if not voucher:
        print(f"-> Voucher dengan kode {voucher_code} tidak ditemukan.")
        return 0, False

    if not voucher["valid"]:
        print(f"-> Voucher dengan kode {voucher_code} sudah digunakan.")
        return 0, False

    # Validasi tanggal kedaluwarsa
    try:
        tanggal_kadaluwarsa = datetime.strptime(voucher["kadaluwarsa"], "%Y-%m-%d")
        if tanggal_kadaluwarsa <= datetime.now():
            print(f"-> Voucher dengan kode {voucher_code} sudah kedaluwarsa.")
            return 0, False
    except ValueError:
        print(f"-> Format tanggal kedaluwarsa untuk voucher {voucher_code} tidak valid.")
        return 0, False

    # Tandai voucher sebagai sudah digunakan
    # voucher["valid"] = False
    # save_json({"vouchers": vouchers, "items": data_items["items"]}, ITEMS_FILE)
    return voucher["discount"], True

# Fungsi untuk top up (menambahkan gold atau gems)
def top_up(account):
    while True:
        try:
            print("\n|==============================================|")
            print("|             Top Up Gems dan Gold             |")
            print("|==============================================|")
            print("| [1]. Top Up Gold                             |")
            print("| [2]. Top Up Gems                             |")
            print("| [3]. Kembali                                 |")
            print("|==============================================|")
            pilihan = int(input("Pilih menu (1/2/3): "))

            if pilihan == 1:
                while True:
                    try:
                        jumlah = int(input("Masukkan jumlah Gold yang ingin ditambahkan: "))
                        if jumlah > 0:
                            account["gold"] += jumlah
                            print("------------------------------------------------")
                            print("Top up Gold berhasil!")
                            print("------------------------------------------------")
                            print(f"-> Gold Anda sekarang: {account['gold']} Gold.")
                            save_json({"accounts": accounts}, USERS_FILE)
                            break
                        else:
                            print("-> Jumlah Gold harus lebih dari 0.")
                    except ValueError:
                        print("-> Jumlah harus diisi berupa angka! Silahkan coba lagi.")
                    except KeyboardInterrupt:
                        print("\n-> Terjadi kesalahan input! Kembali ke menu Top Up.")
                        break
            elif pilihan == 2:
                while True:
                    try:
                        jumlah = int(input("Masukkan jumlah Gems yang ingin ditambahkan: "))
                        if jumlah > 0:
                            account["gems"] += jumlah
                            print("------------------------------------------------")
                            print("Top up Gems berhasil!")
                            print("------------------------------------------------")
                            print(f"-> Gems Anda sekarang: {account['gems']} Gems.")
                            save_json({"accounts": accounts}, USERS_FILE)
                            break
                        else:
                            print("-> Jumlah Gems harus lebih dari 0.")
                    except ValueError:
                        print("-> Jumlah harus diisi berupa angka! Silahkan coba lagi.")
                    except KeyboardInterrupt:
                        print("\n-> Terjadi kesalahan input! Kembali ke menu Top Up.")
                        break
            elif pilihan == 3:
                break
            else:
                print("-> Nomor pilihan tidak ada. Silahkan coba lagi.")
        except ValueError:
            print("-> Input tidak valid! Pilihan harus berupa angka 1-3.")
        except KeyboardInterrupt:
            print("\nTerjadi kesalahan input! Kembali ke menu utama.")
            break

# Fungsi upgrade akun ke member VIP
def upgrade_akun(account):
    if account["role"] == "VIP":
        print("-> Akun anda sudah member VIP, tidak perlu melakukan upgrade.")
        return
    
    # Harga upgrade member VIP (menggunakan gold dan gems)
    harga_upgrade_gold = 10000
    harga_upgrade_gems = 1000

    print("\n|==============================================|")
    print("|          Biaya untuk upgrade ke VIP          |")
    print("|==============================================|")
    print(f"|[1]. {harga_upgrade_gold} Gold                               |")
    print(f"|[2]. {harga_upgrade_gems} Gems                                |")
    print("|[3]. kembali                                  |")
    print("|==============================================|")

    # Menawarkan opsi pembayaran untuk upgrade
    while True:
        try:
            metode_pembayaran = int(input("Pilih metode pembayaran untuk upgrade (1/2/3): "))

            if metode_pembayaran == 1:
                if account["gold"] >= harga_upgrade_gold:
                    account["gold"] -= harga_upgrade_gold
                    account["role"] = "VIP"
                    print("--------------------------------------------------")
                    print("Upgrade berhasil! Anda sekarang adalah member VIP.")
                    print("--------------------------------------------------")
                    print(f"-> Sisa Gold Anda: {account['gold']} Gold.")

                    # Simpan perubahan pada akun
                    save_json({"accounts": accounts}, USERS_FILE)
                    break
                else:
                    print("-> Gold Anda tidak cukup untuk melakukan upgrade.")
                    break
            elif metode_pembayaran == 2:
                if account["gems"] >= harga_upgrade_gems:
                    account["gems"] -= harga_upgrade_gems
                    account["role"] = "VIP"
                    print("---------------------------------------------------")
                    print(f"Upgrade berhasil! Anda sekarang adalah member VIP.")
                    print("---------------------------------------------------")
                    print(f"-> Sisa Gems Anda: {account['gems']} Gems.")

                    # Simpan perubahan pada akun
                    save_json({"accounts": accounts}, USERS_FILE)
                    break
                else:
                    print("-> Gems Anda tidak cukup untuk melakukan upgrade.")
                    break
            elif metode_pembayaran == 3:
                break
            else:
                print("-> Metode pembayaran tidak tersedia. Silahkan coba lagi.")
        except ValueError:
            print("-> Input tidak valid! Tolong pilih opsi metode pembayaran yang tersedia.")
        except KeyboardInterrupt:
            print("\n-> Terjadi kesalahan input! kembali ke menu utama.")
            break

# Program Utama
def main():
    while True:
        try:
            print("\n|==============================================|")
            print("|            Clash of Clans Shop               |")
            print("|==============================================|")
            print("| [1]. Login                                   |")
            print("| [2]. Daftar Akun                             |")
            print("| [3]. Keluar                                  |")
            print("|==============================================|")
            pilihan = int(input("Pilih menu (1/2/3): "))

            if pilihan == 1:
                accounts = load_json(USERS_FILE).get("accounts", {})
                account = login()
                if not account:
                    continue
                balance = account["gold"]  # Saldo Gold dari akun
                gems = account["gems"]  # Gems dari akun
                while True:
                    try:
                        print("\n|==============================================|")
                        print("|    Selamat datang di Clash of Clans Shop!    |")
                        print("|==============================================|")
                        print("| [1]. Lihat Item                              |")
                        print("| [2]. Beli Item                               |")
                        print("| [3]. Top Up                                  |")
                        print("| [4]. Upgrade akun ke VIP                     |")
                        print("| [5]. Logout                                  |")
                        print("|==============================================|")
                        pilihan = int(input("Pilih menu (1/2/3/4/5): "))

                        if pilihan == 1:
                            lihat_item(account["role"])
                        elif pilihan == 2:
                            balance, gems = beli_item(account, account["role"], balance, gems)
                        elif pilihan == 3:
                            top_up(account)
                        elif pilihan == 4:
                            upgrade_akun(account)
                        elif pilihan == 5:
                            print("-> Logout berhasil!")
                            break
                        else:
                            print("-> Nomor pilihan tidak ada. Silahkan coba lagi.")
                    except ValueError:
                        print("-> Input tidak valid! Pilihan harus berupa angka 1-5.")
                    except KeyboardInterrupt:
                        print("\nTerjadi kesalahan input! Program telah dihentikan.")
                        sys.exit(0)
            elif pilihan == 2:
                daftar_akun()
            elif pilihan == 3:
                print("---------------------------------------------------")
                print("Terima kasih telah mengunjungi Clash of Clans Shop!")
                print("---------------------------------------------------")
                break
            else:
                print("-> Nomor pilihan tidak ada. Silahkan coba lagi.")
        except ValueError:
            print("-> Input tidak valid! pilihan harus berupa angka 1-3.")
        except KeyboardInterrupt:
            print("\nTerjadi kesalahan input! Program telah dihentikan.")
            sys.exit(0)

# Menjalankan program
if __name__ == "__main__":
    main()
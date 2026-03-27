import telebot
import qrcode as karekod
from io import BytesIO as bellek
from datetime import datetime as zaman
import secrets as guvenlik
import string as karakterler
import re as desen
import requests as istek
import pandas as pd

# BURAYA YENİ TOKENI YAZ
TOKEN = "8552432590:AAG0zQ6Gx35Bex8ytv0j3dYvdoc1W9GuZLsc"
ADMIN_ID = 5693607967

EXCEL_DOSYA = "Saha iletişim bilgileri 1.xlsx"

bot = telebot.TeleBot(TOKEN)


def admin_mi(mesaj):
    return mesaj.from_user.id == ADMIN_ID


def log_yaz(text):
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{zaman.now()}] {text}\n")


@bot.message_handler(commands=['start'])
def start(mesaj):
    if not admin_mi(mesaj):
        return
    bot.reply_to(mesaj, """🔥 Personal Toolbox Aktif

Komutlar:
/sifre_uret [uzunluk]
/zaman
/qr [metin]
/regex_kontrol [pattern] [metin]
/ip_al
/saha [kod]
""")


# 🔑 Şifre üretme
@bot.message_handler(commands=['sifre_uret'])
def sifre_cmd(mesaj):
    if not admin_mi(mesaj):
        return

    try:
        uzunluk = int(mesaj.text.replace("/sifre_uret", "").strip() or 12)
    except:
        uzunluk = 12

    karakter_seti = karakterler.ascii_letters + karakterler.digits + karakterler.punctuation
    sifre = ''.join(guvenlik.choice(karakter_seti) for _ in range(uzunluk))
    bot.reply_to(mesaj, f"🔐 Şifre: {sifre}")
    log_yaz(f"SIFRE URETILDI, uzunluk={uzunluk}")


# 🕒 Zaman
@bot.message_handler(commands=['zaman'])
def zaman_cmd(mesaj):
    if not admin_mi(mesaj):
        return
    bot.reply_to(mesaj, str(zaman.now()))
    log_yaz("ZAMAN kontrol edildi")


# 📦 QR kod
@bot.message_handler(commands=['qr'])
def qr_cmd(mesaj):
    if not admin_mi(mesaj):
        return

    metin = mesaj.text.replace("/qr", "").strip()
    if not metin:
        bot.reply_to(mesaj, "Metin gir ❌")
        return

    qr = karekod.make(metin)
    bio = bellek()
    bio.name = "qr.png"
    qr.save(bio, "PNG")
    bio.seek(0)

    bot.send_photo(mesaj.chat.id, bio)
    log_yaz(f"QR kullanıldı: {metin}")


# 🔍 Regex kontrol
@bot.message_handler(commands=['regex_kontrol'])
def regex_cmd(mesaj):
    if not admin_mi(mesaj):
        return

    try:
        _, pattern, metin = mesaj.text.split(maxsplit=2)
        eslesme = desen.search(pattern, metin)
        if eslesme:
            bot.reply_to(mesaj, f"✅ Eşleşme bulundu: {eslesme.group(0)}")
        else:
            bot.reply_to(mesaj, "❌ Eşleşme yok")
        log_yaz(f"REGEX kullanıldı: pattern={pattern}, metin={metin}")
    except:
        bot.reply_to(mesaj, "Kullanım: /regex_kontrol [pattern] [metin]")


# 🌐 IP çekme
@bot.message_handler(commands=['ip_al'])
def ip_cmd(mesaj):
    if not admin_mi(mesaj):
        return
    try:
        res = istek.get("https://api.ipify.org?format=json").json()
        bot.reply_to(mesaj, f"🌍 IP: {res['ip']}")
        log_yaz("IP alındı")
    except:
        bot.reply_to(mesaj, "IP alınamadı ❌")


# 📡 SAHA SORGULAMA
@bot.message_handler(commands=['saha'])
def saha_sorgu(mesaj):
    if not admin_mi(mesaj):
        return

    kod = mesaj.text.replace("/saha", "").strip().upper()
    if not kod:
        bot.reply_to(mesaj, "Saha kodu gir ❌")
        return

    try:
        df = pd.read_excel(EXCEL_DOSYA)
        sonuc = df[df["Node"].astype(str).str.upper() == kod]

        if sonuc.empty:
            bot.reply_to(mesaj, "Saha bulunamadı ❌")
            return

        veri = sonuc.iloc[0]
        cevap = "📡 Saha Bilgisi\n\n"

        for kolon in df.columns:
            deger = str(veri[kolon])
            if deger != "nan":
                cevap += f"{kolon}: {deger}\n"

        bot.reply_to(mesaj, cevap)
        log_yaz(f"SAHA sorgulandı: {kod}")

    except Exception as e:
        bot.reply_to(mesaj, "Excel okunamadı ❌")
        print(e)


print("🔥 Toolbox Aktif...")
bot.infinity_polling()

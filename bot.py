import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# --- AYARLAR ---
BOT_TOKEN = "8536342139:AAHWl25OXIaK4-C2e4KCndELt426lvL00L8"
API_BASE = "https://arastir.vip/api"

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# --- DURUMLAR ---
class SorguStates(StatesGroup):
    tc_bekleniyor = State()
    adsoyad_ad = State()
    adsoyad_soyad = State()
    adsoyad_il = State()
    adsoyad_ilce = State()
    gsm_bekleniyor = State()

# --- GÖRSEL MENÜ TASARIMI ---
def ana_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🆔 TC Sorgu", callback_data="btn_tc"),
            InlineKeyboardButton(text="📍 Adres Bilgi", callback_data="btn_adres")
        ],
        [
            InlineKeyboardButton(text="👤 Ad Soyad (VİP)", callback_data="btn_adsoyad")
        ],
        [
            InlineKeyboardButton(text="📞 GSM -> TC", callback_data="btn_gsmtc"),
            InlineKeyboardButton(text="📱 TC -> GSM", callback_data="btn_tcgsm")
        ],
        [
            InlineKeyboardButton(text="🏢 İş Yeri", callback_data="btn_isyeri"),
            InlineKeyboardButton(text="👨‍👩‍👧‍👦 Sülale", callback_data="btn_sulale")
        ],
        [
            InlineKeyboardButton(text="💎 Destek & Bilgi", callback_data="btn_destek")
        ]
    ])
    return keyboard

async def api_get(endpoint, params):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE}/{endpoint}", params=params, timeout=15) as response:
                if response.status == 200:
                    return await response.json()
                return None
    except: return None

# --- HOŞGELDİN MESAJI ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    welcome_text = (
        f"<b>🌟 Hoş geldin {message.from_user.first_name}!</b>\n\n"
        f"🚀 <b>Sorgu Paneli Aktif!</b>\n"
        f"Lütfen aşağıdan yapmak istediğin işlemi seç.\n\n"
        f"<i>⚠️ Not: Yapılan sorgular kayıt altına alınmaz.</i>"
    )
    await message.answer(welcome_text, reply_markup=ana_menu(), parse_mode="HTML")

# --- GENEL TC SORGU TETİKLEYİCİ ---
@dp.callback_query(F.data.in_(["btn_tc", "btn_adres", "btn_isyeri", "btn_sulale", "btn_tcgsm"]))
async def tc_baslat(callback: types.CallbackQuery, state: FSMContext):
    target = callback.data.split("_")[1]
    labels = {"tc": "TC SORGULAMA", "adres": "ADRES SORGULAMA", "isyeri": "İŞ YERİ", "sulale": "SÜLALE", "tcgsm": "GSM BULUCU"}
    
    await callback.message.edit_text(
        f"✨ <b>{labels[target]}</b>\n\n"
        f"Lütfen sorgulanacak <b>11 haneli TC</b> numarasını yazınız:",
        parse_mode="HTML"
    )
    await state.update_data(sorgu_tipi=target)
    await state.set_state(SorguStates.tc_bekleniyor)

# --- AD SOYAD ÖZEL AKIŞ ---
@dp.callback_query(F.data == "btn_adsoyad")
async def adsoyad_baslat(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("👤 <b>AD SOYAD SORGU</b>\n\nLütfen aranan kişinin <b>ADINI</b> girin:", parse_mode="HTML")
    await state.set_state(SorguStates.adsoyad_ad)

@dp.message(SorguStates.adsoyad_ad)
async def ad_al(message: types.Message, state: FSMContext):
    await state.update_data(adi=message.text.upper())
    await message.answer("✅ <b>Ad Kaydedildi.</b>\nŞimdi aranan kişinin <b>SOYADINI</b> girin:", parse_mode="HTML")
    await state.set_state(SorguStates.adsoyad_soyad)

@dp.message(SorguStates.adsoyad_soyad)
async def soyad_al(message: types.Message, state: FSMContext):
    await state.update_data(soyadi=message.text.upper())
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📍 İl/İlçe Ekle (Detaylı)", callback_data="filt_evet")],
        [InlineKeyboardButton(text="⏩ Direkt Sorgula", callback_data="filt_hayir")]
    ])
    await message.answer("🔍 <b>Filtreleme Seçeneği</b>\nSorguyu daraltmak için il/ilçe eklemek ister misiniz?", reply_markup=kb, parse_mode="HTML")

# --- GSM -> TC ---
@dp.callback_query(F.data == "btn_gsmtc")
async def gsmtc_baslat(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("📞 <b>GSM -> TC SORGU</b>\n\nLütfen 10 haneli numarayı girin:\n(Örn: 5051234455)", parse_mode="HTML")
    await state.set_state(SorguStates.gsm_bekleniyor)

# --- SONUÇ GÖSTERİM PANELİ (GÖRSEL) ---
async def sonuc_paneli(message, data_obj):
    if not data_obj:
        return await message.answer("❌ <b>HATA:</b> Kayıt bulunamadı veya API çevrimdışı.", reply_markup=ana_menu(), parse_mode="HTML")
    
    # Veriyi güzelleştirme (API'den gelen veriye göre burayı düzenleyebilirsin)
    sonuc_metni = (
        f"📊 <b>SORGU SONUCU</b>\n"
        f"────────────────────\n"
        f"<code>{data_obj}</code>\n"
        f"────────────────────\n"
        f"✅ İşlem Başarıyla Tamamlandı."
    )
    await message.answer(sonuc_metni, reply_markup=ana_menu(), parse_mode="HTML")

# --- DURUM YÖNETİCİLERİ (HANDLERS) ---
@dp.message(SorguStates.tc_bekleniyor)
async def tc_sonuc_isle(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    tip = user_data.get("sorgu_tipi")
    endpoints = {"tc": "tc.php", "adres": "adres.php", "isyeri": "isyeri.php", "sulale": "sulale.php", "tcgsm": "tcgsm.php"}
    
    msg = await message.answer("🔄 <b>Veritabanı taranıyor...</b>", parse_mode="HTML")
    sonuc = await api_get(endpoints[tip], {"tc": message.text.strip()})
    await msg.delete()
    await sonuc_paneli(message, sonuc)
    await state.clear()

@dp.callback_query(F.data == "filt_hayir")
async def adsoyad_duz_isle(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    sonuc = await api_get("adsoyad.php", {"adi": data['adi'], "soyadi": data['soyadi']})
    await sonuc_paneli(callback.message, sonuc)
    await state.clear()

@dp.callback_query(F.data == "filt_evet")
async def adsoyad_il_sor(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🗺 <b>İL GİRİSİ</b>\nLütfen kişinin yaşadığı <b>İLİ</b> yazın:", parse_mode="HTML")
    await state.set_state(SorguStates.adsoyad_il)

@dp.message(SorguStates.adsoyad_il)
async def adsoyad_ilce_sor(message: types.Message, state: FSMContext):
    await state.update_data(il=message.text.upper())
    await message.answer("🏙 <b>İLÇE GİRİSİ</b>\nLütfen kişinin yaşadığı <b>İLÇEYİ</b> yazın:", parse_mode="HTML")
    await state.set_state(SorguStates.adsoyad_ilce)

@dp.message(SorguStates.adsoyad_ilce)
async def adsoyad_filtreli_bitir(message: types.Message, state: FSMContext):
    data = await state.get_data()
    params = {"adi": data['adi'], "soyadi": data['soyadi'], "il": data['il'], "ilce": message.text.upper()}
    sonuc = await api_get("adsoyad.php", params)
    await sonuc_paneli(message, sonuc)
    await state.clear()

@dp.message(SorguStates.gsm_bekleniyor)
async def gsm_sonuc_isle(message: types.Message, state: FSMContext):
    sonuc = await api_get("gsmtc.php", {"gsm": message.text.strip()})
    await sonuc_paneli(message, sonuc)
    await state.clear()

# --- DESTEK BUTONU ---
@dp.callback_query(F.data == "btn_destek")
async def destek_panel(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "💎 <b>BİLGİ PANELİ</b>\n\n"
        "✨ Bu bot eğitim amaçlı geliştirilmiştir.\n"
        "📞 Destek: @KullaniciAdin\n"
        "📢 Kanal: @Kanalin\n\n"
        "<i>Menüye dönmek için aşağıdaki butonu kullan.</i>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Ana Menü", callback_data="back_menu")]])
    )

@dp.callback_query(F.data == "back_menu")
async def back_to_menu(callback: types.CallbackQuery):
    await cmd_start(callback.message)

# --- BAŞLAT ---
async def main():
    print("🤖 Bot Başlatıldı! | Görsel mod aktif.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

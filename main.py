from telegram.ext import Application, CommandHandler
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import NetworkError, TimedOut, Conflict
from datetime import datetime, timedelta
import asyncio
import logging
import os
import time

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

USER_ROLES = {
    @RIFQI_anda: "owner",
    222222222: "operasional",
    333333333: "mandor",
    444444444: "keuangan",
}


def get_display_name(user) -> str:
    if user.username:
        return f"@{user.username}"
    return user.first_name or "User"


def get_user_role(user_id: int) -> str | None:
    return USER_ROLES.get(user_id)


def has_role(user_id: int, allowed_roles: list[str]) -> bool:
    role = get_user_role(user_id)
    return role in allowed_roles


def role_label(user_id: int) -> str:
    role = get_user_role(user_id)
    return role if role else "tidak_terdaftar"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    role = role_label(user.id)

    await update.message.reply_text(
        "Bot jagung aktif 🚀\n\n"
        f"User: {get_display_name(user)}\n"
        f"Role: {role}\n\n"
        "Ketik /menu untuk melihat menu utama."
    )


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    role = role_label(user.id)

    await update.message.reply_text(
        "📚 MENU UTAMA BOT JAGUNG\n\n"
        f"Role kamu: {role}\n\n"
        "1. Umum\n"
        "/start\n"
        "/menu\n"
        "/help\n"
        "/role\n\n"
        "2. Operasional Jagung\n"
        "/help_beli\n"
        "/help_validasi\n"
        "/help_jual\n"
        "/help_biaya\n\n"
        "3. Jasa\n"
        "/help_kering\n"
        "/help_pipil\n\n"
        "4. Petani & Lahan\n"
        "/help_petani\n"
        "/help_lahan\n"
        "/help_biayai_petani\n"
        "/help_potong_panen\n"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 RINGKASAN COMMAND\n\n"
        "UMUM\n"
        "/start\n"
        "/menu\n"
        "/role\n\n"
        "OPERASIONAL\n"
        "/beli supplier lokasi qty harga bayar\n"
        "/validasi (reply ke transaksi)\n"
        "/jual customer qty harga tempo\n"
        "/biaya jenis jumlah keterangan\n"
        "/bayar_masuk ref jumlah bank\n\n"
        "JASA\n"
        "/kering ref supplier qty kadar_awal kadar_akhir biaya\n"
        "/pipil ref supplier qty biaya\n\n"
        "PETANI\n"
        "/petani_baru nama hp desa luas\n"
        "/lahan_baru petani_id luas lokasi varietas musim\n"
        "/biayai_petani petani_id lahan musim jenis jumlah\n"
        "/potong_panen petani_id fund ref_beli jumlah\n\n"
        "Gunakan /menu untuk tampilan lebih rapi"
    )


async def help_beli(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📥 PANDUAN /beli\n\n"
        "Format:\n"
        "/beli supplier lokasi qty_kg harga bayar\n\n"
        "Contoh:\n"
        "/beli PakHadi Lampung 8000 4800 cash"
    )


async def help_validasi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ PANDUAN /validasi\n\n"
        "Cara pakai:\n"
        "1. Reply ke pesan transaksi beli\n"
        "2. Ketik /validasi"
    )


async def help_jual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📤 PANDUAN /jual\n\n"
        "Format:\n"
        "/jual customer qty_kg harga tempo_hari\n\n"
        "Contoh:\n"
        "/jual PTSinar 10000 5300 14"
    )


async def help_biaya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📉 PANDUAN /biaya\n\n"
        "Format:\n"
        "/biaya jenis jumlah keterangan\n\n"
        "Contoh:\n"
        "/biaya solar 1200000 angkut_dari_lapangan"
    )


async def help_kering(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 PANDUAN /kering\n\n"
        "Format:\n"
        "/kering ref_beli supplier qty_kg kadar_awal kadar_akhir biaya_per_kg\n\n"
        "Contoh:\n"
        "/kering BELI-20260418-001 PakHadi 8000 28 15 300"
    )


async def help_pipil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚙️ PANDUAN /pipil\n\n"
        "Format:\n"
        "/pipil ref_beli supplier qty_kg biaya_per_kg\n\n"
        "Contoh:\n"
        "/pipil BELI-20260418-001 PakHadi 8000 200"
    )


async def help_petani(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👨‍🌾 PANDUAN /petani_baru\n\n"
        "Format:\n"
        "/petani_baru nama hp desa luas_ha\n\n"
        "Contoh:\n"
        "/petani_baru PakHadi 08123456789 Trimurjo 2.5"
    )


async def help_lahan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌱 PANDUAN /lahan_baru\n\n"
        "Format:\n"
        "/lahan_baru petani_id luas_ha lokasi varietas musim\n\n"
        "Contoh:\n"
        "/lahan_baru PTN-001 2.0 LampungTimur Bisi18 MT1-2026"
    )


async def help_biayai_petani(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💳 PANDUAN /biayai_petani\n\n"
        "Format:\n"
        "/biayai_petani petani_id lahan_id musim jenis jumlah\n\n"
        "Contoh:\n"
        "/biayai_petani PTN-001 LHN-001 MT1-2026 bibit 2500000"
    )


async def help_potong_panen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✂️ PANDUAN /potong_panen\n\n"
        "Format:\n"
        "/potong_panen petani_id fund_id ref_beli jumlah\n\n"
        "Contoh:\n"
        "/potong_panen PTN-001 FUND-20260418-001 BELI-20260418-001 1500000"
    )


async def role_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Nama: {get_display_name(user)}\n"
        f"Telegram User ID: {user.id}\n"
        f"Role: {role_label(user.id)}"
    )


async def beli(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    input_by = get_display_name(user)

    if not has_role(user.id, ["operasional", "owner"]):
        await update.message.reply_text(
            f"❌ Akses ditolak.\nRole kamu: {role_label(user.id)}\n"
            "Hanya operasional/owner yang bisa pakai /beli"
        )
        return

    if len(context.args) < 5:
        await help_beli(update, context)
        return

    supplier, lokasi, qty_kg, harga, bayar = context.args[:5]

    try:
        qty_kg = int(qty_kg)
        harga = int(harga)
    except ValueError:
        await update.message.reply_text("qty_kg dan harga harus angka")
        return

    total = qty_kg * harga
    beli_id = f"BELI-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    msg = (
        f"📥 {beli_id}\n\n"
        f"👤 Petani/Supplier: {supplier}\n"
        f"📍 Lokasi: {lokasi}\n"
        f"⚖️ Qty: {qty_kg:,} kg\n"
        f"💰 Harga: Rp{harga:,}\n"
        f"💵 Total: Rp{total:,}\n"
        f"💳 Bayar: {bayar}\n\n"
        f"👨‍💼 Input: {input_by}\n"
        f"📌 Status: MENUNGGU VALIDASI\n\n"
        "Mandor, silakan reply pesan ini dengan /validasi"
    )

    await update.message.reply_text(msg)


async def validasi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    validator = get_display_name(user)

    if not has_role(user.id, ["mandor", "owner"]):
        await update.message.reply_text(
            f"❌ Akses ditolak.\nRole kamu: {role_label(user.id)}\n"
            "Hanya mandor/owner yang bisa pakai /validasi"
        )
        return

    if not update.message.reply_to_message:
        await help_validasi(update, context)
        return

    replied_text = update.message.reply_to_message.text or ""

    if not replied_text.startswith("📥 BELI-"):
        await update.message.reply_text("Pesan yang direply bukan transaksi beli yang valid.")
        return

    first_line = replied_text.splitlines()[0].strip()
    beli_id = first_line.replace("📥 ", "").strip()

    await update.message.reply_text(
        f"✅ {beli_id} VALID\n"
        f"👷 Divalidasi oleh: {validator}"
    )


async def biaya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    input_by = get_display_name(user)

    if not has_role(user.id, ["keuangan", "owner"]):
        await update.message.reply_text(
            f"❌ Akses ditolak.\nRole kamu: {role_label(user.id)}\n"
            "Hanya keuangan/owner yang bisa pakai /biaya"
        )
        return

    if len(context.args) < 3:
        await help_biaya(update, context)
        return

    jenis = context.args[0]

    try:
        jumlah = int(context.args[1])
    except ValueError:
        await update.message.reply_text("jumlah harus angka")
        return

    keterangan = " ".join(context.args[2:])
    biaya_id = f"BIAYA-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    await update.message.reply_text(
        f"📉 {biaya_id}\n\n"
        f"🧾 Jenis: {jenis}\n"
        f"💸 Jumlah: Rp{jumlah:,}\n"
        f"📝 Keterangan: {keterangan}\n\n"
        f"👨‍💼 Input: {input_by}\n"
        f"📌 Status: TERCATAT"
    )


async def jual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    input_by = get_display_name(user)

    if not has_role(user.id, ["keuangan", "owner"]):
        await update.message.reply_text(
            f"❌ Akses ditolak.\nRole kamu: {role_label(user.id)}\n"
            "Hanya keuangan/owner yang bisa pakai /jual"
        )
        return

    if len(context.args) < 4:
        await help_jual(update, context)
        return

    customer = context.args[0]

    try:
        qty_kg = int(context.args[1])
        harga = int(context.args[2])
        tempo_hari = int(context.args[3])
    except ValueError:
        await update.message.reply_text("qty_kg, harga, dan tempo_hari harus angka")
        return

    total = qty_kg * harga
    jatuh_tempo = (datetime.now() + timedelta(days=tempo_hari)).strftime("%Y-%m-%d")
    jual_id = f"JUAL-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    await update.message.reply_text(
        f"📤 {jual_id}\n\n"
        f"🏭 Customer: {customer}\n"
        f"⚖️ Qty: {qty_kg:,} kg\n"
        f"💰 Harga: Rp{harga:,}\n"
        f"💵 Total: Rp{total:,}\n"
        f"⏳ Tempo: {tempo_hari} hari\n"
        f"📅 Jatuh tempo: {jatuh_tempo}\n\n"
        f"👨‍💼 Input: {input_by}\n"
        f"📌 Status: PIUTANG"
    )


async def bayar_masuk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    input_by = get_display_name(user)

    if not has_role(user.id, ["keuangan", "owner"]):
        await update.message.reply_text(
            f"❌ Akses ditolak.\nRole kamu: {role_label(user.id)}\n"
            "Hanya keuangan/owner yang bisa pakai /bayar_masuk"
        )
        return

    if len(context.args) < 3:
        await update.message.reply_text(
            "💰 PANDUAN /bayar_masuk\n\n"
            "Format:\n"
            "/bayar_masuk ref_jual jumlah bank\n\n"
            "Contoh:\n"
            "/bayar_masuk JUAL-20260418-001 53000000 Mandiri"
        )
        return

    ref_jual = context.args[0]

    try:
        jumlah = int(context.args[1])
    except ValueError:
        await update.message.reply_text("jumlah harus angka")
        return

    bank = context.args[2]
    bayar_id = f"IN-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    await update.message.reply_text(
        f"💰 {bayar_id}\n\n"
        f"🔗 Ref Penjualan: {ref_jual}\n"
        f"🏦 Bank: {bank}\n"
        f"💵 Jumlah masuk: Rp{jumlah:,}\n\n"
        f"👨‍💼 Input: {input_by}\n"
        f"📌 Status: PEMBAYARAN DITERIMA"
    )


async def kering(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    input_by = get_display_name(user)

    if not has_role(user.id, ["operasional", "owner"]):
        await update.message.reply_text(
            f"❌ Akses ditolak.\nRole kamu: {role_label(user.id)}\n"
            "Hanya operasional/owner yang bisa pakai /kering"
        )
        return

    if len(context.args) < 6:
        await help_kering(update, context)
        return

    ref_beli = context.args[0]
    supplier = context.args[1]

    try:
        qty_kg = int(context.args[2])
        kadar_awal = int(context.args[3])
        kadar_akhir = int(context.args[4])
        biaya_per_kg = int(context.args[5])
    except ValueError:
        await update.message.reply_text(
            "qty_kg, kadar_awal, kadar_akhir, dan biaya_per_kg harus angka"
        )
        return

    total_biaya = qty_kg * biaya_per_kg
    kering_id = f"KERING-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    await update.message.reply_text(
        f"🔥 {kering_id}\n\n"
        f"🔗 Ref Beli: {ref_beli}\n"
        f"👤 Supplier: {supplier}\n"
        f"⚖️ Qty: {qty_kg:,} kg\n"
        f"💧 Kadar awal: {kadar_awal}%\n"
        f"✅ Kadar akhir: {kadar_akhir}%\n"
        f"💸 Biaya/kg: Rp{biaya_per_kg:,}\n"
        f"💵 Total biaya: Rp{total_biaya:,}\n\n"
        f"👨‍💼 Input: {input_by}\n"
        f"📌 Status: TERCATAT"
    )


async def pipil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    input_by = get_display_name(user)

    if not has_role(user.id, ["operasional", "owner"]):
        await update.message.reply_text(
            f"❌ Akses ditolak.\nRole kamu: {role_label(user.id)}\n"
            "Hanya operasional/owner yang bisa pakai /pipil"
        )
        return

    if len(context.args) < 4:
        await help_pipil(update, context)
        return

    ref_beli = context.args[0]
    supplier = context.args[1]

    try:
        qty_kg = int(context.args[2])
        biaya_per_kg = int(context.args[3])
    except ValueError:
        await update.message.reply_text("qty_kg dan biaya_per_kg harus angka")
        return

    total_biaya = qty_kg * biaya_per_kg
    pipil_id = f"PIPIL-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    await update.message.reply_text(
        f"⚙️ {pipil_id}\n\n"
        f"🔗 Ref Beli: {ref_beli}\n"
        f"👤 Supplier: {supplier}\n"
        f"⚖️ Qty: {qty_kg:,} kg\n"
        f"💸 Biaya/kg: Rp{biaya_per_kg:,}\n"
        f"💵 Total biaya: Rp{total_biaya:,}\n\n"
        f"👨‍💼 Input: {input_by}\n"
        f"📌 Status: TERCATAT"
    )


async def petani_baru(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    input_by = get_display_name(user)

    if not has_role(user.id, ["operasional", "owner"]):
        await update.message.reply_text(
            f"❌ Akses ditolak.\nRole kamu: {role_label(user.id)}\n"
            "Hanya operasional/owner yang bisa pakai /petani_baru"
        )
        return

    if len(context.args) < 4:
        await help_petani(update, context)
        return

    nama = context.args[0]
    hp = context.args[1]
    desa = context.args[2]

    try:
        luas_ha = float(context.args[3])
    except ValueError:
        await update.message.reply_text("luas_ha harus angka")
        return

    petani_id = f"PTN-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    await update.message.reply_text(
        f"👨‍🌾 {petani_id}\n\n"
        f"Nama: {nama}\n"
        f"HP: {hp}\n"
        f"Desa: {desa}\n"
        f"Luas lahan: {luas_ha} ha\n\n"
        f"👨‍💼 Input: {input_by}\n"
        f"📌 Status: PETANI TERDAFTAR"
    )


async def lahan_baru(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    input_by = get_display_name(user)

    if not has_role(user.id, ["operasional", "owner"]):
        await update.message.reply_text(
            f"❌ Akses ditolak.\nRole kamu: {role_label(user.id)}\n"
            "Hanya operasional/owner yang bisa pakai /lahan_baru"
        )
        return

    if len(context.args) < 5:
        await help_lahan(update, context)
        return

    petani_id = context.args[0]

    try:
        luas_ha = float(context.args[1])
    except ValueError:
        await update.message.reply_text("luas_ha harus angka")
        return

    lokasi = context.args[2]
    varietas = context.args[3]
    musim = context.args[4]
    lahan_id = f"LHN-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    await update.message.reply_text(
        f"🌱 {lahan_id}\n\n"
        f"Petani ID: {petani_id}\n"
        f"Luas: {luas_ha} ha\n"
        f"Lokasi: {lokasi}\n"
        f"Varietas: {varietas}\n"
        f"Musim: {musim}\n\n"
        f"👨‍💼 Input: {input_by}\n"
        f"📌 Status: LAHAN TERDAFTAR"
    )


async def biayai_petani(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    input_by = get_display_name(user)

    if not has_role(user.id, ["keuangan", "owner"]):
        await update.message.reply_text(
            f"❌ Akses ditolak.\nRole kamu: {role_label(user.id)}\n"
            "Hanya keuangan/owner yang bisa pakai /biayai_petani"
        )
        return

    if len(context.args) < 5:
        await help_biayai_petani(update, context)
        return

    petani_id = context.args[0]
    lahan_id = context.args[1]
    musim = context.args[2]
    jenis = context.args[3]

    try:
        jumlah = int(context.args[4])
    except ValueError:
        await update.message.reply_text("jumlah harus angka")
        return

    fund_id = f"FUND-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    await update.message.reply_text(
        f"💳 {fund_id}\n\n"
        f"Petani ID: {petani_id}\n"
        f"Lahan ID: {lahan_id}\n"
        f"Musim: {musim}\n"
        f"Jenis: {jenis}\n"
        f"Jumlah: Rp{jumlah:,}\n\n"
        f"👨‍💼 Input: {input_by}\n"
        f"📌 Status: OUTSTANDING"
    )


async def potong_panen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    input_by = get_display_name(user)

    if not has_role(user.id, ["keuangan", "owner"]):
        await update.message.reply_text(
            f"❌ Akses ditolak.\nRole kamu: {role_label(user.id)}\n"
            "Hanya keuangan/owner yang bisa pakai /potong_panen"
        )
        return

    if len(context.args) < 4:
        await help_potong_panen(update, context)
        return

    petani_id = context.args[0]
    fund_id = context.args[1]
    ref_beli = context.args[2]

    try:
        jumlah = int(context.args[3])
    except ValueError:
        await update.message.reply_text("jumlah harus angka")
        return

    potong_id = f"POTONG-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    await update.message.reply_text(
        f"✂️ {potong_id}\n\n"
        f"Petani ID: {petani_id}\n"
        f"Ref Fund: {fund_id}\n"
        f"Ref Beli: {ref_beli}\n"
        f"Jumlah potongan: Rp{jumlah:,}\n\n"
        f"👨‍💼 Input: {input_by}\n"
        f"📌 Status: POTONGAN TERCATAT"
    )


async def _delete_webhook(token: str):
    from telegram import Bot
    bot = Bot(token=token)
    async with bot:
        await bot.delete_webhook(drop_pending_updates=True)


def build_app() -> Application:
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("role", role_command))

    app.add_handler(CommandHandler("help_beli", help_beli))
    app.add_handler(CommandHandler("help_validasi", help_validasi))
    app.add_handler(CommandHandler("help_jual", help_jual))
    app.add_handler(CommandHandler("help_biaya", help_biaya))
    app.add_handler(CommandHandler("help_kering", help_kering))
    app.add_handler(CommandHandler("help_pipil", help_pipil))
    app.add_handler(CommandHandler("help_petani", help_petani))
    app.add_handler(CommandHandler("help_lahan", help_lahan))
    app.add_handler(CommandHandler("help_biayai_petani", help_biayai_petani))
    app.add_handler(CommandHandler("help_potong_panen", help_potong_panen))

    app.add_handler(CommandHandler("beli", beli))
    app.add_handler(CommandHandler("validasi", validasi))
    app.add_handler(CommandHandler("biaya", biaya))
    app.add_handler(CommandHandler("jual", jual))
    app.add_handler(CommandHandler("bayar_masuk", bayar_masuk))
    app.add_handler(CommandHandler("kering", kering))
    app.add_handler(CommandHandler("pipil", pipil))
    app.add_handler(CommandHandler("petani_baru", petani_baru))
    app.add_handler(CommandHandler("lahan_baru", lahan_baru))
    app.add_handler(CommandHandler("biayai_petani", biayai_petani))
    app.add_handler(CommandHandler("potong_panen", potong_panen))

    return app


def main():
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN belum diisi di Railway Variables")

    app = build_app()

    try:
        asyncio.run(_delete_webhook(TOKEN))
        logger.info("Webhook dihapus, memulai polling...")
    except (NetworkError, TimedOut) as e:
        logger.warning(f"Gagal menghapus webhook (akan tetap lanjut): {e}")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    MAX_RETRIES = 5
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            app.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True,
            )
            break
        except Conflict as e:
            if attempt < MAX_RETRIES:
                wait_seconds = 2 ** attempt
                logger.warning(
                    f"Conflict error (attempt {attempt}/{MAX_RETRIES}): {e}. "
                    f"Menunggu {wait_seconds} detik sebelum retry..."
                )
                time.sleep(wait_seconds)

                app = build_app()
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            else:
                logger.error(
                    f"Conflict error setelah {MAX_RETRIES} percobaan. Bot berhenti: {e}"
                )
                raise


if __name__ == "__main__":
    main()

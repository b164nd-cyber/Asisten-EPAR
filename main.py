from telegram.ext import Application, CommandHandler
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import NetworkError, TimedOut, Conflict
from datetime import datetime
import asyncio
import logging
import os
import time

from sheet_service import append_row

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


def get_display_name(user) -> str:
    if user.username:
        return f"@{user.username}"
    return user.first_name or "User"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bot jagung aktif 🚀\n"
        "Gunakan /beli untuk input transaksi beli.\n"
        "Gunakan /validasi dengan cara reply ke transaksi beli."
    )


async def beli(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 5:
        await update.message.reply_text(
            "Format salah.\n"
            "Contoh:\n"
            "/beli PakHadi Lampung 8000 4800 cash"
        )
        return

    supplier, lokasi, qty_kg, harga, bayar = context.args[:5]
    input_by = get_display_name(update.effective_user)

    try:
        qty_kg = int(qty_kg)
        harga = int(harga)
    except ValueError:
        await update.message.reply_text("qty_kg dan harga harus angka")
        return

    total = qty_kg * harga
    beli_id = f"BELI-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Simpan ke Google Sheet
    append_row(
        "pembelian",
        [
            beli_id,
            tanggal,
            supplier,
            lokasi,
            qty_kg,
            harga,
            total,
            bayar,
            "MENUNGGU_VALIDASI",
            str(update.effective_user.id),
            "",
            "",
            "",
        ],
    )

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
        f"Mandor, silakan reply pesan ini dengan /validasi"
    )

    await update.message.reply_text(msg)


async def validasi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    validator = get_display_name(update.effective_user)

    # Wajib reply ke pesan transaksi
    if not update.message.reply_to_message:
        await update.message.reply_text(
            "Gunakan /validasi dengan cara reply ke pesan transaksi beli."
        )
        return

    replied_text = update.message.reply_to_message.text or ""

    if not replied_text.startswith("📥 BELI-"):
        await update.message.reply_text(
            "Pesan yang direply bukan transaksi beli yang valid."
        )
        return

    # Ambil ID dari baris pertama, misalnya: "📥 BELI-20260418-001"
    first_line = replied_text.splitlines()[0].strip()
    beli_id = first_line.replace("📥 ", "").strip()

    await update.message.reply_text(
        f"✅ {beli_id} VALID\n"
        f"👷 Divalidasi oleh: {validator}"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Command tersedia:\n\n"
        "/start\n"
        "/help\n"
        "/beli PakHadi Lampung 8000 4800 cash\n"
        "/validasi  -> gunakan dengan reply ke pesan transaksi beli"
    )


async def _delete_webhook(token: str):
    from telegram import Bot

    bot = Bot(token=token)
    async with bot:
        await bot.delete_webhook(drop_pending_updates=True)


def build_app() -> Application:
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("beli", beli))
    app.add_handler(CommandHandler("validasi", validasi))
    return app


def main():
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN belum diisi di Railway Variables")

    app = build_app()

    # Hapus webhook aktif agar tidak konflik dengan polling
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
